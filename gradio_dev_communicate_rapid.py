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



roles = [
    "湾区大叔", "呆萌川妹", "广州德哥", "北京小爷", "少年梓辛/Brayan",
    "魅力女友", "深夜播客", "柔美女友", "撒娇学妹", "浩宇小哥"
]

voice_type={
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

# 获取历史对话
def get_history_text(ip, user_input):
    history = user_history.get(ip, [])
    # full_prompt = ""
    # for turn in history:
    #     full_prompt += f"用户：{turn['user']}\nAI：{turn['ai']}\n"
    # full_prompt += f"用户：{user_input}\nAI："
    return history

# 更新历史对话
def update_history(ip, user_input, ai_output):
    if ip not in user_history:
        user_history[ip] = []
    user_history[ip].append({"role": "user", "content": user_input})
    user_history[ip].append({"role": "assistant", "content": ai_output})
    if len(user_history[ip]) > 100:
        user_history[ip] = user_history[ip][-100:]

# 新增：清空用户历史对话

def clear_user_history(user_id):
    global user_history
    if user_id == "":
        raise gr.Error("用户id不能为空，请输入用户id后再操作！")
    if user_id in user_history:
        user_history[user_id] = []
        return f"已清空用户 {user_id} 的历史对话。"
    else:
        return f"未找到用户 {user_id} 的历史对话。"

def generate_avatar(ref_image, emo, seed, a_cfg_scale, e_cfg_scale, no_crop,role, prompt,user_id,text, request: gr.Request = None):
    if user_id == "":
        raise gr.Error("用户id不能为空，请输入用户id后再操作！")

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
        # user_ip = request.client.host if request else "unknown"#获取用户ip
        print("当前用户id",user_id)
        # 1. 拼接历史
        history_text = get_history_text(user_id, text)

        print("history_text",history_text)
        if len(history_text) == 0:
            text_with_history = [{"role": "user", "content": text}]
        else:
            text_with_history = history_text+[{"role": "user", "content": text}]
        print("text_with_history",text_with_history)

        max_retry = 3
        retry_count = 0
        while retry_count < max_retry:
            try:
                # 2. deepseek 生成
                ai_output = deepseek_chat(prompt, text_with_history)
                print("ai_output",ai_output)
                emo_llm = ai_output.split(";")[0]
                emo_level_llm = int(ai_output.split(";")[1])
                llm_text = ai_output.split(";")[2:]
                llm_text = ";".join(llm_text)
                print("emo_llm",emo_llm )
                print("emo_level_llm",emo_level_llm)
                print("llm_text",llm_text)
                print("输入的emo",emo)
                print("输入的e_cfg_scale",e_cfg_scale)
                if emo == None:
                    print("emo为空，使用大模型生成的情绪")
                    emo = emo_llm
                    print("使用大模型生成的情绪",emo)
                if e_cfg_scale == 0:
                    print("e_cfg_scale为空，使用大模型生成的情绪等级")
                    e_cfg_scale = emo_level_llm
                    print("使用大模型生成的情绪等级",e_cfg_scale)
                # 3. 更新历史
                update_history(user_id, text, ai_output)
                print("更新历史对话:",user_history)
                end_time_llm = time.time()
                print(f"LLM耗时: {end_time_llm - start_time_llm} 秒")
                start_time_tts = time.time()
                aud_path = asyncio.run(batch_query(llm_text,voice_type[role]))  # 这里拿到音频文件路径
                end_time_tts = time.time()
                print(f"TTS耗时: {end_time_tts - start_time_tts} 秒")
                break
            except Exception as e:
                print(f"TTS生成失败，正在重试... 错误信息: {e}")
                retry_count += 1
                # time.sleep(1)
        if retry_count == max_retry:
            print("TTS生成失败，重试次数超过最大值，请检查网络连接或重试")
            return f"生成失败"
   
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
        gr.Dropdown(choices=emo_list, label="情感,若为默认值0,则根据大模型生成的情绪等级自动设置"),
        gr.Number(value=15, label="随机种子"),
        gr.Number(value=2.0, label="口型和音频同步的权重"),
        gr.Number(label="情感等级，越大越夸张，建议小于15.若不设置,则根据大模型生成的情绪等级自动设置"),
        gr.Checkbox(label="跳过裁剪(no_crop)"),
        gr.Dropdown(choices=roles, value=roles[5],label="音色选择"),
        gr.Textbox(label="提示词",value="你的名字叫蒂法，性别为女"),
        gr.Textbox(label="用户id,请输入一个唯一id,用于记录用户历史对话",value=""),
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
    user_history = {}
    agent = get_global_agent()

    with gr.Blocks() as demo:
        gr.Markdown("# Float数字人口型生成 by Noah Dong\n输入你想说的话，与数字人对话，生成匹配口型的数字人视频。")
        with gr.Row():
            with gr.Column(scale=1):
                ref_image = gr.Image(type="pil", value="./assets/difa.jpg", label="人物图片")
                emo = gr.Dropdown(choices=emo_list, label="情感,若为默认值0,则根据大模型生成的情绪等级自动设置")
                seed = gr.Number(value=15, label="随机种子")
                a_cfg_scale = gr.Number(value=2.0, label="口型和音频同步的权重")
                e_cfg_scale = gr.Number(label="情感等级，越大越夸张，建议小于15.若不设置,则根据大模型生成的情绪等级自动设置")
                no_crop = gr.Checkbox(label="跳过裁剪(no_crop)")
                role = gr.Dropdown(choices=roles, value=roles[5],label="音色选择")
                prompt = gr.Textbox(label="数字人人设", value="你的名字叫蒂法，性别为女")
                user_id = gr.Textbox(label="用户id,请输入一个唯一id,用于记录用户历史对话")
                text = gr.Textbox(label="聊天对话框", value="你好~很高兴认识你哦")
                gen_btn = gr.Button("与数字人对话")
            with gr.Column(scale=1):
                video_output = gr.Video(label="生成的视频")
                clear_btn = gr.Button("清空该用户历史对话")
                clear_output = gr.Textbox(label="清空结果", interactive=False)
  


        # 绑定事件
        gen_btn.click(
            fn=generate_avatar,
            inputs=[ref_image, emo, seed, a_cfg_scale, e_cfg_scale, no_crop,role, prompt, user_id, text],
            outputs=video_output
        )
        clear_btn.click(
            fn=clear_user_history,
            inputs=user_id,
            outputs=clear_output
        )
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
