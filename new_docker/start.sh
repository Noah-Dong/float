#!/bin/bash

# FLOAT 项目依赖安装脚本
# 使用阿里云镜像源加速下载

echo "开始安装 FLOAT 项目依赖..."

# 切换到项目目录
cd /mnt/cfs1/dongfangzhou/float/
echo "正在安装 networkx..."
pip install networkx==2.6.3 -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "networkx 安装完成！"

echo "正在安装 PyTorch 相关包..."
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
echo "PyTorch 相关包安装完成！"




echo "正在安装 requirements.txt 中的依赖..."
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "requirements.txt 中的依赖安装完成！"

echo "正在安装 numpy..."
pip install numpy==1.24.4 -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "numpy 安装完成！"

echo "正在安装 albumentations..."
pip install albumentations==1.4.15 -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "albumentations 安装完成！"

echo "依赖安装完成！" 