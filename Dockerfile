# 使用轻量级的 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，确保 Python 输出直接打印到控制台
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖（如果以后用到 PostgreSQL 或某些 AI 库，可能需要这些）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt 以利用 Docker 缓存层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件
COPY . .

# 暴露应用端口（假设你的 Flask/FastAPI 运行在 5000）
EXPOSE 5000

# 启动命令（开发阶段建议直接运行 run.py）
CMD ["python", "run.py"]