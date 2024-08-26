import os
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
    allow_headers=["*"]  # 允许携带的 Headers
)

app.mount("/static", StaticFiles(directory="web", html=True), name="static")


# 当用户上传录音文件，本方法用于接收和处理上传的音频文件
@app.post('/api/audio_to_audio')
async def audio_to_audio(audio: UploadFile = File(...), history: str = Form(...)):
    if audio.filename == '':
        raise HTTPException(status_code=400, detail="No audio part")
    # if not history:
    #     raise HTTPException(status_code=400, detail="No history part")

    try:
        # 读取音频文件
        contents = await audio.read()

        webm_path = './test/input_audio.webm'
        wav_path = './test/input_audio.wav'
        try:
            with open(webm_path, 'wb') as file:
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
            raise HTTPException(status_code=500, detail=f"Error in processing with ASR, LLM, or TTS APIs: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    return JSONResponse(content={"asrText": asr_text, "llm_response": llm_response, "ttsAudio": tts_audio_path})


class TextItem(BaseModel):
    text: str


@app.post('/api/text_to_audio')
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
        instruct = '请分析我的运动状态，给出建议。'
        # 模拟调用 LLM 和 TTS API
        llm_response = call_llm_api(file_content + '请尽可能简要分析我的运动状态，给出一句话作为建议，不需要太长')
        tts_audio_path = call_tts_api(llm_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in processing with ASR, LLM, or TTS APIs: {e}")

    return JSONResponse(content={"asrText": instruct, "llm_response": llm_response, "ttsAudio": tts_audio_path})



asr = ASRExecutor()
tts = TTSExecutor()
llm = ChatModel()

# 先跑一遍ASR+TTS以加快推理速度

tts(text="你好，这是一段测试音频", output="./test/output.wav",
    am="fastspeech2_csmsc", voc="pwgan_csmsc")
asr(P('./test/output.wav'))

# 模拟的ASR API调用函数
def call_asr_api(audio_path: str):
    # 这里应该是调用外部ASR服务的代码
    return asr(P(audio_path), force_yes=True)  # "转换后的文本"


# 模拟的LLM API调用函数
def call_llm_api(text: str):
    # 这里应该是调用外部LLM服务的代码
    return llm.new_line(text)


# 模拟的TTS API调用函数
def call_tts_api(text: str):
    # 调用外部TTS服务的代码
    output_wav_path = './web/wavs/tts.wav'
    tts(text=text, output=output_wav_path, am="fastspeech2_csmsc", voc="pwgan_csmsc")
    return output_wav_path


# 运行FastAPI应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8086)
