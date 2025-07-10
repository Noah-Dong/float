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

def generate_avatar(ref_image, emo, seed, a_cfg_scale, e_cfg_scale, no_crop, text):
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
    cmd = [
        "python", "generate.py",
        "--ref_path", ref_path,
        # "--aud_path", aud_path,
        "--seed", str(seed),
        "--a_cfg_scale", str(a_cfg_scale),
        "--e_cfg_scale", str(e_cfg_scale),
        "--ckpt_path", "./checkpoints/float.pth",
        "--res_dir",tmp_dir
    ]
    if emo != 'no-emo':
        cmd += ["--emo", str(emo)]
    if no_crop:
        cmd.append("--no_crop")
    if text:
        aud_path = asyncio.run(batch_query(text))  # 这里拿到音频文件路径
        # shutil.copy(combined, aud_path)
    # # 可选：将 text 作为参数传递给 generate.py（如果 generate.py 支持）
    # if text:
    #     cmd += ["--text", text]
    # if text:
    # aud_path = tts_long.batch_query(text)
    cmd += ["--aud_path", aud_path]
        # combined.export(aud_path, format="wav")
    
    # 调用生成脚本
    try:
        print(cmd)
        subprocess.run(cmd, check=True)
        out_path = get_latest_video(tmp_dir)
        return out_path
    except subprocess.CalledProcessError as e:
        return f"生成失败: {e}"
    finally:
        # 可选：清理临时文件
        pass

emo_list = ['no-emo', 'angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

demo = gr.Interface(
    fn=generate_avatar,
    inputs=[
        gr.Image(type="pil", value="./assets/kun2.jpg",label="人物图片"),
        # gr.Audio(type="filepath",value="./assets/test.m4a",label="音频"),
        gr.Dropdown(choices=emo_list, value="no-emo", label="情感"),
        gr.Number(value=15, label="随机种子"),
        gr.Number(value=2.0, label="口型和音频同步的权重"),
        gr.Number(value=1.0, label="情感等级，越大越夸张，建议小于15"),
        gr.Checkbox(label="跳过裁剪(no_crop)"),
        gr.Textbox(label="文本输入",value="大叫好，我是蔡徐坤")
    ],
    outputs=gr.Video(label="生成的视频"),
    title="Float数字人口型生成 by Noah Dong",
    description="上传人物图片和音频，选择情感等参数，生成匹配口型的数字人视频。"
)

def get_latest_video(results_dir="./results"):
    video_files = glob.glob(os.path.join(results_dir, "*.mp4"))
    if not video_files:
        return None
    latest_video = max(video_files, key=os.path.getctime)
    return latest_video

if __name__ == "__main__":
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
