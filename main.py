import argparse
import asyncio
import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from cuter import cut_video
from logger import setup_logger
from qwen import Qwen
from subtitle_process import process_subtitle_segments
from uploader import upload

logger = setup_logger('main')


class VideoProcessor:
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        self.qwen = None
        self.max_workers = multiprocessing.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def process_all(self) -> None:
        try:
            # 处理所有srt文件
            for file in os.listdir(self.input_dir):
                if file.endswith('.srt'):
                    srt_path = os.path.join(self.input_dir, file)
                    self.process_srt(srt_path)

            # 读取分析结果并处理视频
            for file in os.listdir(self.input_dir):
                if file.endswith('.txt'):
                    with open(os.path.join(self.input_dir, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        video_info = self._parse_analysis(content, file)
                        if video_info:
                            async for title, cut_path in self._process_video(video_info):
                                try:
                                    await upload(title, cut_path)
                                    logger.info(f"上传完成: {title}")
                                except Exception as e:
                                    logger.error(f"上传失败 {title}: {str(e)}")

        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
            raise


    async def _process_video(self, video_info: dict):
        """异步处理视频切片"""
        try:
            # 使用线程池执行CPU密集型的视频切片任务
            async for result in cut_video(video_info):
                yield result
        except Exception as e:
            logger.error(f"视频处理失败: {str(e)}")

    def process_srt(self, srt_file: str) -> None:
        try:
            name = os.path.splitext(os.path.basename(srt_file))[0]
            self.qwen = Qwen(name)
            process_subtitle_segments(srt_file)
            logger.info(f"字幕分析完成: {srt_file}")
        except Exception as e:
            logger.error(f"字幕处理失败: {str(e)}")
            raise

    def _parse_analysis(self, content: str, filename: str) -> Optional[dict]:
        try:
            # 解析分析结果，提取切片信息
            segments = []
            current_segment = None

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- 时间：'):
                    times = line.split('：')[1].strip('[]').split(' --> ')
                    current_segment = {'start': times[0], 'end': times[1]}
                elif line.startswith('- 标题：') and current_segment:
                    current_segment['title'] = line.split('：')[1].strip()
                    segments.append(f"{current_segment['start']} {current_segment['end']} {current_segment['title']}")

            if segments:
                return {
                    "title": os.path.splitext(filename)[0],
                    "subs": segments
                }
            return None

        except Exception as e:
            logger.error(f"解析分析结果失败: {str(e)}")
            return None


def main():
    parser = argparse.ArgumentParser(description='视频切片处理工具')
    parser.add_argument('--input', '-i', required=True, help='输入目录，包含srt文件和视频文件')

    args = parser.parse_args()

    processor = VideoProcessor(args.input)
    # 全部处理
    asyncio.run(processor.process_all())

   


if __name__ == "__main__":
    main()
