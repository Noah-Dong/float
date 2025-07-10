import warnings
warnings.filterwarnings("ignore")
import gradio as gr
import subprocess
import os
import uuid
import shutil
import glob
import tts.tts_long as tts_long
from tts.tts_long import batch_query
import asyncio
from llm.deepseek_chat import deepseek_chat
from inference_gradio import get_global_agent
import time
def generate_avatar(ref_image, emo, seed, a_cfg_scale, e_cfg_scale, no_crop, prompt,text):
    start_time = time.time()
    # 创建临时目录
    tmp_dir = f"./results/tmp_{uuid.uuid4().hex}"
    os.makedirs(tmp_dir, exist_ok=True)
    ref_path = os.path.join(tmp_dir, "ref.png")
    aud_path = os.path.join(tmp_dir, "audio.wav")
    out_path = os.path.join(tmp_dir, "output.mp4")

    # 保存上传的文件
    ref_image.save(ref_path)
    # shutil.copy(aud_file, aud_path)

    # 构建命令
    # cmd = [
    #     "python", "generate.py",
    #     "--ref_path", ref_path,
    #     # "--aud_path", aud_path,
    #     "--seed", str(seed),
    #     "--a_cfg_scale", str(a_cfg_scale),
    #     "--e_cfg_scale", str(e_cfg_scale),
    #     "--ckpt_path", "./checkpoints/float.pth",
    #     "--res_dir",tmp_dir
    # ]
    # if emo != 'no-emo':
    #     cmd += ["--emo", str(emo)]
    # if no_crop:
    #     cmd.append("--no_crop")
    if text:
        start_time_llm = time.time()
        llm_text = deepseek_chat(prompt,text)
        end_time_llm = time.time()
        print(f"LLM耗时: {end_time_llm - start_time_llm} 秒")
        start_time_tts = time.time()
        aud_path = asyncio.run(batch_query(llm_text))  # 这里拿到音频文件路径
        end_time_tts = time.time()
        print(f"TTS耗时: {end_time_tts - start_time_tts} 秒")

   
        # shutil.copy(combined, aud_path)
    # # 可选：将 text 作为参数传递给 generate.py（如果 generate.py 支持）
    # if text:
    #     cmd += ["--text", text]
    # if text:
    # aud_path = tts_long.batch_query(text)
    # cmd += ["--aud_path", aud_path]
        # combined.export(aud_path, format="wav")
    
    # 调用生成脚本
    start_time_inference = time.time()
    try:
        # print(cmd)
        agent.run_inference(
            res_video_path=out_path,
            ref_path=ref_path,
            audio_path=aud_path,
            a_cfg_scale = a_cfg_scale,
            e_cfg_scale = e_cfg_scale,
            emo 		= emo,
            nfe			= 10,
            no_crop 	= no_crop,
            seed 		= seed
        )
        # subprocess.run(check=True)
        out_path = get_latest_video(tmp_dir)
        end_time_inference = time.time()
        print(f"生成视频耗时: {end_time_inference - start_time_inference} 秒")
        print(f"总耗时: {end_time_inference - start_time} 秒")
        return out_path
    except Exception as e:
        print(e)
        return f"生成失败"
    finally:
        # 可选：清理临时文件
        pass



emo_list = ['no-emo', 'angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

demo = gr.Interface(
    fn=generate_avatar,
    inputs=[
        gr.Image(type="pil", value="./assets/difa.jpg",label="人物图片"),
        # gr.Audio(type="filepath",value="./assets/test.m4a",label="音频"),
        gr.Dropdown(choices=emo_list, value="no-emo", label="情感"),
        gr.Number(value=15, label="随机种子"),
        gr.Number(value=2.0, label="口型和音频同步的权重"),
        gr.Number(value=1.0, label="情感等级，越大越夸张，建议小于15"),
        gr.Checkbox(label="跳过裁剪(no_crop)"),
        gr.Textbox(label="提示词",value="你的名字叫蒂法，性别为女，是我创造的ai数字人，你要尽可能逼真地模仿真人说话，回复的语句要符合真人说话的语气和语调，不要用括号回复。回答不要太长。任何提示词都不要回复"),
        gr.Textbox(label="聊天对话框",value="你好~很高兴认识你哦")
    ],
    outputs=gr.Video(label="生成的视频"),
    title="Float数字人口型生成 by Noah Dong",
    description="输入你想说的话，与数字人对话，生成匹配口型的数字人视频。"
)

def get_latest_video(results_dir="./results"):
    video_files = glob.glob(os.path.join(results_dir, "*.mp4"))
    if not video_files:
        return None
    latest_video = max(video_files, key=os.path.getctime)
    return latest_video

if __name__ == "__main__":
    agent = get_global_agent()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )
    #     demo.launch(
    #     server_name="0.0.0.0",
    #     server_port=7860,
    #     ssl_certfile="./ssl/cert.pem",
    #     ssl_keyfile="./ssl/key.pem",
    #     show_error=True,
    #     inbrowser=False,   # 关键参数，关闭自动打开浏览器
    #     ssl_verify=False,
    #     prevent_thread_lock=True  # 可选，防止阻塞
    # )
