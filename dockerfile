# FROM --platform=linux/amd64 docker.m.daocloud.io/nvidia/cuda:11.8.0-base-ubuntu20.04
FROM docker.m.daocloud.io/python:3.8.5-slim
# 直接设置时区文件（无需交互）
# RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
#     echo "Asia/Shanghai" > /etc/timezone
# RUN mkdir /app
# 复制脚本到容器

COPY ./start.sh /app/start.sh
COPY ./sleep.sh /app/sleep.sh
# COPY HunyuanVideo-Avatar /app/HunyuanVideo-Avatar
# COPY Python-3.10.0.tgz /app/Python-3.10.0.tgz
WORKDIR /app
# 运行安装脚本
RUN chmod +x /app/sleep.sh
RUN chmod +x /app/start.sh 
RUN /app/start.sh




ENTRYPOINT ["./sleep.sh"]
# 设置工作目录


# 示例运行命令（实际使用时可能需要覆盖）
# CMD ["python3.10", "lite_avatar.py", "--data_dir", "./data/preload", "--audio_file", "asr_example.wav", "--result_dir", "result"]