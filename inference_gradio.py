# inference_server.py
"""
全局只加载一次模型，后续多次复用，适合Gradio、Flask、FastAPI等服务调用
"""
import time
import os
from generate import InferenceAgent, InferenceOptions

# 1. 全局只加载一次模型和权重
def get_global_agent():
    """
    获取全局唯一的 InferenceAgent 实例（单例模式）
    """
    if not hasattr(get_global_agent, "_agent"):
        # 初始化参数
        opt = InferenceOptions().parse()
        opt.rank, opt.ngpus = 0, 1
        # 可根据需要自定义 opt 的其它参数
        opt.ckpt_path = "./checkpoints/float.pth"
        # opt.res_dir = "./results"
        # 加载模型
        get_global_agent._agent = InferenceAgent(opt)
        print("模型已加载到内存/显存！")
    return get_global_agent._agent

    
# 3. 示例：命令行测试
if __name__ == "__main__":
    agent = get_global_agent()
    for i in range(10):
        start_time = time.time()
        agent.run_inference(
            res_video_path="./results/test.mp4",
            ref_path="./assets/difa.jpg",
            audio_path="./tts/tts_out/final.wav",
            a_cfg_scale = 2.0,
            r_cfg_scale = 1.0,
            e_cfg_scale = 1.0,
            emo 		= "S2E",
            nfe			= 10,
            no_crop 	= False,
            seed 		= 25
            )
        end_time = time.time()
        print(f"第{i}次生成视频耗时: {end_time - start_time} 秒")
    
  
