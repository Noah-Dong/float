from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import shutil
import asyncio
from inference_gradio import get_global_agent
import tts.tts_long as tts_long
import time

# 角色与 voice_type 映射
voice_type_dict = {
    "湾区大叔":"zh_female_wanqudashu_moon_bigtts",
    "呆萌川妹":"zh_female_daimengchuanmei_moon_bigtts",
    "广州德哥":"zh_male_guozhoudege_moon_bigtts",
    "北京小爷":"zh_male_beijingxiaoye_moon_bigtts",
    "少年梓辛/Brayan":"zh_male_shaonianzixin_moon_bigtts",
    "魅力女友":"zh_female_meilinvyou_moon_bigtts",
    "深夜播客":"zh_male_shenyeboke_moon_bigtts",
    "柔美女友":"zh_female_sajiaonvyou_moon_bigtts",
    "撒娇学妹":"zh_female_yuanqinvyou_moon_bigtts",
    "浩宇小哥":"zh_male_haoyuxiaoge_moon_bigtts"
}

app = FastAPI()
agent = get_global_agent()

@app.post("/generate-avatar/")
async def generate_avatar_api(
    ref_image: UploadFile = File(...),
    emo: str = Form("auto"),
    seed: int = Form(15),
    a_cfg_scale: float = Form(2.0),
    e_cfg_scale: float = Form(0),
    max_emotion_level: float = Form(5),
    no_crop: bool = Form(False),
    role: str = Form("魅力女友"),
    # prompt: str = Form("你的名字叫蒂法，性别为女"),
    # user_id: str = Form(""),
    text: str = Form("你好~很高兴认识你哦")
):
    # 1. 保存图片到临时文件夹
    tmp_dir = f"./results/api_{uuid.uuid4().hex}"
    os.makedirs(tmp_dir, exist_ok=True)
    ref_path = os.path.join(tmp_dir, "ref.png")
    with open(ref_path, "wb") as f:
        shutil.copyfileobj(ref_image.file, f)
    tts_start_time = time.time()
    # 2. 生成音频（TTS，异步调用）
    vt = voice_type_dict.get(role, "zh_female_meilinvyou_moon_bigtts")
    aud_path = await tts_long.batch_query(text, vt)  # 返回音频路径
    tts_end_time = time.time()
    print(f"TTS耗时: {tts_end_time - tts_start_time} 秒")
    # 3. 生成视频输出路径
    out_path = os.path.join(tmp_dir, "output.mp4")

    start_time = time.time()
    # 4. 调用 agent.run_inference
    try:
        agent.run_inference(
            res_video_path=out_path,
            ref_path=ref_path,
            audio_path=aud_path,
            a_cfg_scale=a_cfg_scale,
            e_cfg_scale=e_cfg_scale,
            emo=emo,
            nfe=10,
            no_crop=no_crop,
            seed=seed
        )
        end_time = time.time()
        print(f"生成视频耗时: {end_time - start_time} 秒")
    except Exception as e:
        return JSONResponse({"error": f"生成失败: {str(e)}"}, status_code=500)

    if not os.path.exists(out_path):
        return JSONResponse({"error": "生成失败"}, status_code=500)
    return FileResponse(out_path, media_type="video/mp4", filename="output.mp4")