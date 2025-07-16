from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from deepseek_chat import deepseek_chat

app = FastAPI()

@app.post("/deepseek-chat/")
async def deepseek_chat_api(
    prompt: str = Form(""),
    text: str = Form(...),
    max_emotion_level: float = Form(5)
):
    # text_with_history 这里假设为 [{"role": "user", "content": text}]
    text_with_history = [{"role": "user", "content": text}]
    try:
        result = deepseek_chat(prompt, text_with_history, max_emotion_level)
        # 按格式分割
        try:
            emotion, level, content = result.split(";", 2)
        except Exception:
            emotion, level, content = "neutral", "1", result
        return JSONResponse({
            "emotion": emotion,
            "level": level,
            "content": content
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("Deepseek Chat API 启动于: http://0.0.0.0:8010")
    uvicorn.run(app, host="0.0.0.0", port=8010)