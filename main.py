import os
import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from api.ffmpeg_api import convert_opus_to_wav
from pydantic import BaseModel
from api.chat_api import ChatModel
from paddlespeech.cli.tts.infer import TTSExecutor
from pathlib import Path as P
from paddlespeech.cli.asr.infer import ASRExecutor
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

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

app.mount("/static", StaticFiles(directory="web", html=True), name="static")


# 当用户上传录音文件，本方法用于接收和处理上传的音频文件
@app.post("/api/audio_to_audio")
async def audio_to_audio(audio: UploadFile = File(...), history: str = Form(...)):
    if audio.filename == "":
        raise HTTPException(status_code=400, detail="No audio part")
    # if not history:
    #     raise HTTPException(status_code=400, detail="No history part")

    try:
        # 读取音频文件
        contents = await audio.read()

        webm_path = "./test/input_audio.webm"
        wav_path = "./test/input_audio.wav"
        try:
            with open(webm_path, "wb") as file:
                # 将字节流写入文件
                file.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing webm file: {e}")
        convert_opus_to_wav(webm_path, wav_path)

        try:
            asr_text = call_asr_api(wav_path)
            llm_response = call_llm_api(asr_text)
            # TODO parse llm_response
            tts_audio_path = call_tts_api("llm_response")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in processing with ASR, LLM, or TTS APIs: {e}",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    return JSONResponse(
        content={
            "asrText": asr_text,
            "llm_response": llm_response,
            "ttsAudio": tts_audio_path,
        }
    )


class TextItem(BaseModel):
    text: str


@app.post("/api/text_to_audio")
async def text_to_audio(item: TextItem):
    text = item.text
    if not text:
        raise HTTPException(status_code=400, detail="No text part")

    llm_response = call_llm_api(text)
    tts_audio = call_tts_api(llm_response)
    return JSONResponse(content={"llm_response": llm_response, "ttsAudio": tts_audio})


UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 保存文件到本地
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        instruct = """请分析我的运动状态，给出尽可能有效简易的建议，以纯文本的形式给出。参考标准0分：平衡能力好，建议做稍复杂的全身练习并增加力量性练习，增强体力,提高身体综合素质。
1-4分：平衡能力开始降低，跌倒风险增大。建议增加提高平衡能力的练习，如单腿跳跃、倒走、太极拳和太
极剑等。
5-16分：平衡能力受到较大削弱，跌倒风险较大。建议做针对平衡能力的练习，如单足站立练习、“不倒翁”
练习、沿直线行走、侧身行走等,适当增加一些力量性练习。
17-24分：平衡能力较差，很容易跌倒。建议选择合适的助行器并补充钙质，做一些力所能及的简单运动，如
走楼梯、散步、坐立练习、沿直线行走等，运动时应有人监护以确保安全。"""
        # 模拟调用 LLM 和 TTS API
        llm_response = call_llm_api(file_content + instruct)
        tts_audio_path = call_tts_api(llm_response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in processing with ASR, LLM, or TTS APIs: {e}",
        )

    return JSONResponse(
        content={
            "asrText": "请评估我的运动状态并给出建议",
            "llm_response": llm_response,
            "ttsAudio": tts_audio_path,
        }
    )


asr = ASRExecutor()
tts = TTSExecutor()
llm = ChatModel()

# 先跑一遍ASR+TTS以加快推理速度

tts(
    text="你好，这是一段测试音频",
    output="./test/output.wav",
    am="fastspeech2_csmsc",
    voc="pwgan_csmsc",
)
asr(P("./test/output.wav"))


# 模拟的ASR API调用函数
def call_asr_api(audio_path: str):
    # 这里应该是调用外部ASR服务的代码
    return asr(P(audio_path), force_yes=True)  # "转换后的文本"

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
    text = re.sub(r'[<>\"\'\[\]\{\}\|\-\_\+\=\*\&\%\$\#\@\!\`]', '', text)  # 删除英文特殊字符

    # 将多个句号或逗号合并为一个
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r',{2,}', ',', text)
    text = re.sub(r'\.+', '.', text)

    return text
# 模拟的LLM API调用函数
def call_llm_api(text: str):
    # 这里应该是调用外部LLM服务的代码
    return normalize_text(llm.new_line(text))


# 模拟的TTS API调用函数
def call_tts_api(text: str):
    # 调用外部TTS服务的代码
    output_wav_path = "./web/wavs/tts.wav"
    tts(text=text, output=output_wav_path, am="fastspeech2_csmsc", voc="pwgan_csmsc")
    return output_wav_path


# 运行FastAPI应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8086)
