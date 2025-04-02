import os
import subprocess
import sys
from typing import Optional
from config import BILIBILI_CONFIG
from logger import setup_logger
from cover import CoverGenerator

logger = setup_logger('uploader')

class BiliUploader:
    def __init__(self):
        self.biliup_path = BILIBILI_CONFIG["biliup_path"]
        if not os.path.exists(self.biliup_path):
            raise FileNotFoundError(f"biliup工具不存在: {self.biliup_path}")
        
        self.generator = CoverGenerator()

    def _execute_command(self, command: list) -> None:
        try:
            process = subprocess.Popen(
                command,
                text=True,
                encoding='utf-8',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output = output.strip()
                    logger.info(output)
                    print(output)
                    sys.stdout.flush()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
                
        except Exception as e:
            logger.error(f"命令执行失败: {str(e)}")
            raise

    def upload(self, title: str, video_path: str, cover: Optional[str] = None) -> None:
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")

            # 切换到biliup目录
            original_dir = os.getcwd()
            os.chdir(self.biliup_path)
            # 如果没有提供封面，生成一个
            if not cover:
                cover = self.generator.generate_cover(title=title)



            try:
                # 构建上传命令
                command = [
                    "biliup.exe",
                    "upload",
                    "--tid", BILIBILI_CONFIG["tid"],
                    "--cover", cover,
                    "--title", f"{title}|孙尚书Plus",
                    "--tag", ",".join(BILIBILI_CONFIG["tags"]),
                    "--no-reprint", str(BILIBILI_CONFIG["no_reprint"]),
                    video_path
                ]

                logger.info(f"开始上传视频: {title}")
                self._execute_command(command)
                logger.info(f"视频上传完成: {title}")
                # 上传完成后删除封面
                if cover:
                    os.remove(cover)
            finally:
                # 恢复原始工作目录
                os.chdir(original_dir)

        except Exception as e:
            logger.error(f"上传失败 {title}: {str(e)}")
            raise

async def upload(title: str, video_path: str) -> None:
    try:
        uploader = BiliUploader()
        uploader.upload(title, video_path)
    except Exception as e:
        logger.error(f"推送失败 {title}: {str(e)}")
        raise
