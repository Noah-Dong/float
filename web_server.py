from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import os, uuid, shutil, base64, asyncio, pathlib

# 业务依赖
from inference_gradio import get_global_agent
import tts.tts_long as tts_long

BASE_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "template"

voice_type_dict = {
    "湾区大叔": "zh_female_wanqudashu_moon_bigtts",
    "呆萌川妹": "zh_female_daimengchuanmei_moon_bigtts",
    "广州德哥": "zh_male_guozhoudege_moon_bigtts",
    "北京小爷": "zh_male_beijingxiaoye_moon_bigtts",
    "少年梓辛/Brayan": "zh_male_shaonianzixin_moon_bigtts",
    "魅力女友": "zh_female_meilinvyou_moon_bigtts",
    "深夜播客": "zh_male_shenyeboke_moon_bigtts",
    "柔美女友": "zh_female_sajiaonvyou_moon_bigtts",
    "撒娇学妹": "zh_female_yuanqinvyou_moon_bigtts",
    "浩宇小哥": "zh_male_haoyuxiaoge_moon_bigtts",
}

app = FastAPI()

# 允许跨域（如有需要可调整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态模板资源（用于 html 内部引用图片等）
if TEMPLATE_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(TEMPLATE_DIR)), name="static")

agent = get_global_agent()

# ---------------------------------------------------------------------------
# 页面路由
# ---------------------------------------------------------------------------
@app.get("/setAvatar", response_class=HTMLResponse)
async def set_avatar_page():
    with open(TEMPLATE_DIR / "setAvatar.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    with open(TEMPLATE_DIR / "chat.html", "r", encoding="utf-8") as f:
        return f.read()


# 根路径重定向到 /setAvatar 方便直接访问
@app.get("/", response_class=HTMLResponse)
async def index_page():
    return await set_avatar_page()


# ---------------------------------------------------------------------------
# 生成视频接口
# ---------------------------------------------------------------------------
@app.post("/generate")
async def generate_api(
    image: UploadFile = File(...),
    text: str = Form(...),
    voice: str = Form(...),
    prompt: str = Form(""),
    userId: str = Form(""),
    digitalHumanId: str = Form(""),
):
    try:
        # 创建临时目录
        tmp_dir = f"./results/web_{uuid.uuid4().hex}"
        os.makedirs(tmp_dir, exist_ok=True)
        # 保存图片
        ref_path = os.path.join(tmp_dir, "ref.png")
        with open(ref_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # TTS 生成音频（异步）
        vt = voice_type_dict.get(voice, "zh_female_meilinvyou_moon_bigtts")
        aud_path = await tts_long.batch_query(text, vt)

        # 输出视频路径
        out_path = os.path.join(tmp_dir, "output.mp4")

        # 生成视频
        agent.run_inference(
            res_video_path=out_path,
            ref_path=ref_path,
            audio_path=aud_path,
            a_cfg_scale=2.0,
            e_cfg_scale=0,
            emo="auto",
            nfe=10,
            no_crop=False,
            seed=25,
        )

        # 读视频并 base64
        with open(out_path, "rb") as vf:
            video_b64 = base64.b64encode(vf.read()).decode()

        return {
            "success": True,
            "videoData": video_b64,
        }
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# 语音识别接口 (录音文件)
# 简易回传占位，后续可接入实际 ASR
# ---------------------------------------------------------------------------
@app.post("/asr")
async def asr_api(audio: UploadFile = File(...)):
    # TODO: 接入真实 ASR 服务，这里先返回占位文本
    return {"success": True, "text": "(语音识别结果占位)"}


if __name__ == "__main__":
    import uvicorn

    print("Web server running at http://0.0.0.0:8080")
    uvicorn.run("web_server:app", host="0.0.0.0", port=8080, reload=True) 