import os
from typing import List, Tuple

from moviepy import VideoFileClip

from config import OUTPUT_DIR
from logger import setup_logger

logger = setup_logger('video_cutter')


def time_to_seconds(time_str: str) -> float:
    try:
        hours, minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split(',')
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    except Exception as e:
        logger.error(f"时间格式转换失败: {time_str}, 错误: {str(e)}")
        raise


def _cut(start_time: float, end_time: float, video_path: str, output_file: str) -> None:
    video = None
    clip = None
    try:
        # 检查输入文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 加载视频文件
        video = VideoFileClip(video_path)

        # 验证时间范围
        if end_time <= start_time:
            raise ValueError(f"无效的时间范围: {start_time} -> {end_time}")
        if start_time < 0 or end_time > video.duration:
            raise ValueError(f"时间超出视频长度: {video.duration}")

        # 截取指定时间段
        clip = video.subclipped(start_time, end_time)

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 保存输出文件
        clip.write_videofile(output_file, logger=None)
        logger.info(f"视频切割完成: {output_file}")

    except Exception as e:
        logger.error(f"视频切割失败: {str(e)}")
        raise
    finally:
        # 释放资源
        if clip:
            clip.close()
        if video:
            video.close()


async def cut_video(video_info: dict):
    """
    切割视频并返回切片信息列表
    返回: [(标题, 切片路径), ...]
    """
    video_path = video_info['video_path']
    name = video_info["video_name"]
    output_path = os.path.join(OUTPUT_DIR, name)
    os.makedirs(output_path, exist_ok=True)

    for split in video_info["segments"]:
        title = split['title']
        start_time = split['start_time']
        end_time = split['end_time']
        cut_path = os.path.join(output_path, f"{title}.mp4")
        # 提交切片任务
        _cut(time_to_seconds(start_time), time_to_seconds(end_time), video_path,
             cut_path)
        yield title, cut_path

# cut_video(json.load(open("20250315-150234-278-升哥下午茶_segments.json", "r", encoding="utf-8")))
