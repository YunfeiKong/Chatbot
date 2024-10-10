from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import copy
import os
import re
import urllib3
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from utils.chat_api import ChatModel
from utils.questions import Question, questions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "src", "uploaded_files")

app = FastAPI()
app.mount("/static", StaticFiles(directory="web", html=True), name="static")
llm = ChatModel()

# 2、声明一个 源 列表；重点：要包含跨域的客户端 源
origins = ["*"]

# 3、配置 CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"],  # 允许携带的 Headers
)


class TextItem(BaseModel):
    text: str

class AnswerRequest(BaseModel):
    answer: str

def normalize_text(text):
    # 删除换行符和多余的空格，将所有空白字符替换为单一空格
    text = re.sub(r'\s+', ' ', text).strip()

    # 替换标点符号
    text = re.sub(r'[。?？!！；;]', '.', text)  # 替换省略号、问号、感叹号、分号为句号
    text = re.sub(r'[？！]', '.', text)  # 替换英文问号、感叹号为句号
    text = re.sub(r'[：:]', ',', text)  # 替换冒号为逗号
    text = re.sub(r'[，,]', ',', text)  # 替换中文逗号为英文逗号

    # 删除特殊字符
    text = re.sub(r'[《》〈〉（）()“”‘’——¥]', '', text)  # 删除中文特殊字符
    text = re.sub(
        r'[<>\"\'\[\]\{\}\|\-\_\+\=\*\&\%\$\#\@\!\`]', '', text)  # 删除英文特殊字符

    # 将多个句号或逗号合并为一个
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r',{2,}', ',', text)
    text = re.sub(r'\.+', '.', text)

    return text


@app.post("/api/llm_chat")
async def llm_chat(text: TextItem):
    try:
        llm_response = normalize_text(call_llm_api(text.text))
        logger.info(llm_response)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in LLM processing: {e}")
    return JSONResponse(content={"llm_response": llm_response})


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):

    try:
        file_path = os.path.join(UPLOAD_DIR, str(file.filename))
        logger.info(file_path)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        # 这里以二进制形式 *wb* 写入文件后以文本模式 *r* 读出，内容需要为纯文本
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        instruct = """请分析我的运动状态，给出尽可能有效简易的建议。
        参考标准0分：平衡能力好，建议做稍复杂的全身练习并增加力量性练习，增强体力,提高身体综合素质。
        1到4分：平衡能力开始降低，跌倒风险增大。建议增加提高平衡能力的练习，如单腿跳跃、倒走、太极拳和太
        极剑等。
        5到16分：平衡能力受到较大削弱，跌倒风险较大。建议做针对平衡能力的练习，如单足站立练习、“不倒翁”
        练习、沿直线行走、侧身行走等,适当增加一些力量性练习。
        17到24分：平衡能力较差，很容易跌倒。建议选择合适的助行器并补充钙质，做一些力所能及的简单运动，如
        走楼梯、散步、坐立练习、沿直线行走等，运动时应有人监护以确保安全。"""
        llm_response = normalize_text(call_llm_api(file_content + instruct))
        logger.info(llm_response)
    except Exception as e:
        logger.error("error in /api/upload")
        raise HTTPException(
            status_code=500,
            detail=f"Error in processing with ASR, LLM, or TTS APIs: {e}",
        )

    return JSONResponse(
        content={
            "asrText": "请评估我的运动状态并给出建议",
            "llm_response": llm_response,
        }
    )


user_sessions: Dict[str, List[Question]] = {}


@app.post("/start")
async def start_session(request: Request):
    session_id = request.client.host  # Use client IP as session ID for simplicity
    user_sessions[session_id] = [copy.copy(q) for q in questions]
    return {"message": "Session started", "question": user_sessions[session_id][0].to_dict()}


@app.post("/answer")
async def answer_question(request: Request, answer_request: AnswerRequest):
    session_id = request.client.host
    if session_id not in user_sessions:
        raise HTTPException(status_code=400, detail="Session not started")

    session_questions = user_sessions[session_id]
    for q in session_questions:
        if q.answer is None:
            q.mark_as_answered(answer_request.answer)
            q.score = int(call_llm_api(
                f'请根据评分标准{str(q.scoring_criteria)}和用户的回答`{q.answer}`来判断该问题的分数，返回一个数字即可，不需要任何多余的描述'))
            logger.info(q.to_dict())
            break
    else:
        raise HTTPException(
            status_code=400, detail="All questions already answered")

    next_question = next(
        (q for q in session_questions if q.answer is None), None)
    if next_question:
        return {"message": "Next question", "question": next_question.to_dict()}
    else:
        total_score = sum(q.score for q in session_questions)
        return {"message": "All questions answered", "total_score": total_score}

# 模拟的LLM API调用函数
def call_llm_api(text: str) -> str:
    # return '666'
    return llm.chat_on_arc770(text, 0.1)


# 运行FastAPI应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8086)
