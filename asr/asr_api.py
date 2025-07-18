from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import json
import time
from asr import file_recognize


app = FastAPI()


@app.post("/asr/")
async def asr_api(audio_url: str = Form("")):
    """HTTP API: 输入 audio_url 返回识别 text"""
    try:
        text = file_recognize(audio_url)
        return {"text": text}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    print("ASR API running at http://0.0.0.0:8020")
    uvicorn.run(app, host="0.0.0.0", port=8020)