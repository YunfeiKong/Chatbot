from loguru import logger
from paddlespeech.cli.tts.infer import TTSExecutor
from pathlib import Path as P
from paddlespeech.cli.asr.infer import ASRExecutor


WAV_DIR = "./src/wavs"


class TransClient:

    def __init__(self):
        self.asr_executor = ASRExecutor()
        self.tts_executor = TTSExecutor()

        self.tts_executor(
            text="你好，这是一段测试音频",
            output="./test/output.wav",
            am="fastspeech2_csmsc",
            voc="pwgan_csmsc",
        )
        self.asr_executor(P("./test/output.wav"))


    def tts(self, input_text: str) -> str:
        try:
            self.tts_executor(
                text=input_text,
                output=WAV_DIR + "/tts_output.wav",
                am="fastspeech2_csmsc",
                voc="pwgan_csmsc",
            )
        except:
            logger.error(f"Error in tts({input_text})")
        
        return WAV_DIR + "/tts_output.wav"

    def asr(self, audio_path: str) -> str:
        return str(self.asr_executor(P(WAV_DIR + audio_path)))
