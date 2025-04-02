import logging
import os
from datetime import datetime

from config import LOGS_DIR


def setup_logger(name):
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    log_file = os.path.join(LOGS_DIR, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 防止重复添加处理器
    if not logger.handlers:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 设置格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
