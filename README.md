# FLOAT - 数字人视频生成系统

<div align="center">
  <img src="assets/float-abstract.png" alt="FLOAT Logo" width="400"/>
</div>

## 📖 项目简介

FLOAT 是一个基于深度学习的数字人视频生成系统，能够根据参考图像和音频输入，生成逼真的说话人视频。该系统支持多种情感表达，提供多种部署方式，适用于数字人直播、虚拟主播、AI助手等场景。

本项目是对FLOAT的复现与工程化，后者用于给数字人agent项目（位于/mnt/cfs1/dongfangzhou/digital-human-simple/digital-human-go）提供float生成视频与llm的接口。      
运行接口的方法：    
        python  run_server.py (运行float模型的接口，host="0.0.0.0", port=8000)
        python  llm/deepseek_chat_api.py(运行deepseek llm的接口，Deepseek Chat API 启动于: http://0.0.0.0:8010)


### ✨ 主要特性

- 🎭 **多模态生成**: 支持图像+音频的端到端视频生成
- 🎨 **情感控制**: 支持7种情感类型（愤怒、厌恶、恐惧、快乐、中性、悲伤、惊讶）
- 🔧 **灵活部署**: 提供Web界面、API接口、Gradio演示等多种使用方式
- 🎯 **高质量输出**: 基于Flow Matching Transformer的高质量视频生成
- 🚀 **实时推理**: 优化的推理流程，支持快速生成
- 🎤 **TTS集成**: 内置文本转语音功能，支持多种音色

## 🏗️ 系统架构

```
输入: 参考图像 + 音频/文本
    ↓
预处理: 人脸检测 + 音频特征提取
    ↓
FLOAT模型: 运动潜在自编码器 + 条件编码器 + 流匹配变换器
    ↓
输出: 说话人视频
```

### 核心组件

- **运动潜在自编码器**: 编码/解码图像，控制面部运动
- **音频编码器**: 基于Wav2Vec2的音频特征提取
- **情感编码器**: 语音情感识别和分类
- **流匹配变换器**: 核心生成模块，基于ODE求解器

## 🛠️ 环境要求

- **Python**: 3.8+
- **CUDA**: 11.8+ (推荐)
- **GPU**: 8GB+ VRAM (推荐)
- **内存**: 16GB+ RAM

## 📦 安装指南

### 1. 克隆项目

```bash
git clone <repository-url>
cd float
```

### 2. 安装依赖

#### 方法一：使用安装脚本（推荐）

```bash
chmod +x start.sh
./start.sh
```

#### 方法二：手动安装

```bash
# 安装PyTorch
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118

# 安装项目依赖
pip install -r requirements.txt

# 安装额外依赖
pip install fastapi uvicorn gradio opencv-python numpy
```

### 3. 下载模型权重

```bash
chmod +x download_checkpoints.sh
./download_checkpoints.sh
```

或者手动下载模型权重文件到 `checkpoints/` 目录。

## 🚀 快速开始

### 命令行使用

```bash
CUDA_VISIBLE_DEVICES=1 python generate.py   
    --ref_path assets/sam_altman.webp  
    --aud_path assets/aud-sample-vs-1.wav    
    --seed  15  
    --a_cfg_scale 2  
    --e_cfg_scale 1 
    --ckpt_path ./checkpoints/float.pth  
```
### API服务

```bash
python run_server.py(本质上是调用api_server.py)
```

API服务运行在 `http://localhost:8000`。
### Web界面

```bash
python web_server.py
```

访问 `http://localhost:8080` 使用Web界面。

### Gradio演示

```bash
python gradio_dev_communicate_rapid.py
```

访问 `http://localhost:7860` 使用Gradio界面。



## 📚 使用指南

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--ref_path` | str | - | 参考图像路径 |
| `--aud_path` | str | - | 音频文件路径 |
| `--emo` | str | 'auto' | 情感类型 |
| `--a_cfg_scale` | float | 2.0 | 音频同步权重 |
| `--e_cfg_scale` | float | 0 | 情感强度 |
| `--nfe` | int | 10 | 推理步数 |
| `--seed` | int | 25 | 随机种子 |
| `--no_crop` | bool | False | 是否跳过人脸裁剪 |

### 情感类型

- `auto`: 自动检测情感
- `angry`: 愤怒
- `disgust`: 厌恶
- `fear`: 恐惧
- `happy`: 快乐
- `neutral`: 中性
- `sad`: 悲伤
- `surprise`: 惊讶

### 音色选择

- 湾区大叔
- 呆萌川妹
- 广州德哥
- 北京小爷
- 少年梓辛/Brayan
- 魅力女友
- 深夜播客
- 柔美女友
- 撒娇学妹
- 浩宇小哥

## 🔌 API文档

### 生成视频接口

**POST** `/generate-avatar/`

**请求参数:**
- `ref_image`: 参考图像文件
- `text`: 要说的文本
- `role`: 音色选择
- `emo`: 情感类型 (可选)
- `seed`: 随机种子 (可选)
- `a_cfg_scale`: 音频同步权重 (可选)
- `e_cfg_scale`: 情感强度 (可选)
- `no_crop`: 是否跳过裁剪 (可选)

**响应:**
- 成功: 返回生成的视频文件
- 失败: 返回错误信息

### Web接口

**POST** `/generate`

**请求参数:**
- `image`: 参考图像文件
- `text`: 要说的文本
- `voice`: 音色选择
- `prompt`: 提示词 (可选)
- `userId`: 用户ID (可选)
- `digitalHumanId`: 数字人ID (可选)

**响应:**
```json
{
    "success": true,
    "videoData": "base64编码的视频数据"
}
```

## 📁 项目结构

```
float/
├── models/                 # 模型定义
│   ├── float/             # FLOAT模型核心
│   ├── wav2vec2.py        # 音频特征提取
│   └── wav2vec2_ser.py    # 语音情感识别
├── options/               # 配置选项
├── checkpoints/           # 模型权重
├── assets/               # 示例资源
├── results/              # 输出结果
├── template/             # Web模板
├── tts/                  # 文本转语音
├── asr/                  # 语音识别
├── memory/               # 用户历史记录
├── generate.py           # 核心推理脚本
├── web_server.py         # Web服务器
├── api_server.py         # API服务器
├── gradio_dev_communicate_rapid.py  # Gradio演示
└── requirements.txt      # 依赖列表
```

## 🔧 高级配置

### 自定义模型参数

```python
# 修改推理参数
opt.nfe = 20              # 增加推理步数提高质量
opt.a_cfg_scale = 3.0     # 增强音频同步
opt.e_cfg_scale = 1.5     # 增强情感表达
```

```

## 🐛 常见问题

### Q: 生成的视频底部有黑色区域？
A: 这是正常现象，模型只生成人脸区域。如需完整背景，可以：
- 使用 `--no_crop` 参数
- 后期合成背景图像
- 调整输出分辨率

### Q: 音频同步效果不好？
A: 可以尝试：
- 增加 `a_cfg_scale` 参数值
- 使用更清晰的音频文件
- 调整音频采样率

### Q: 情感表达不够明显？
A: 可以尝试：
- 增加 `e_cfg_scale` 参数值
- 选择更明确的情感类型
- 使用情感更丰富的音频

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE.md](LICENSE.md) 文件了解详情。

## 🙏 致谢

- 感谢所有开源项目的贡献者
- 感谢社区用户的支持和反馈
- 感谢研究团队的技术支持

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

---

<div align="center">
  <p>⭐ 如果这个项目对您有帮助，请给我们一个星标！</p>
</div>
