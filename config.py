import os

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = r'D:\output'
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 视频相关配置
VIDEO_SETTINGS = {
    "width": 1080,
    "height": 1920,
    "font_path": "simhei.ttf",
    "title_font_size": 50,
    "subtitle_font_size": 30,
    "tag_font_size": 24,
}

# B站上传配置
BILIBILI_CONFIG = {
    "tid": "160",
    "tags": ["生活", "学习", "知识","日常"],
    "no_reprint": 1,
    "biliup_path": r"C:\Users\admin\Downloads\biliupR-v0.2.2-x86_64-windows\biliupR-v0.2.2-x86_64-windows"
}

# 通义千问配置
QWEN_CONFIG = {
    "api_key": "sk-xxxxxxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwq-32b",
}
