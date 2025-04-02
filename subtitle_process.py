import os.path
from dataclasses import dataclass
from typing import Generator, List, Iterator

import pysrt
from collections import deque
from qwen import Qwen


@dataclass
class SubtitleSegment:
    start_time: str
    end_time: str
    title: str
    content: str


def read_subtitle_chunks(srt_file: str, chunk_size: int = 500, overlap: int = 10) -> Iterator[List[pysrt.SubRipItem]]:
    subs = pysrt.open(srt_file)
    total_subs = len(subs)
    context_buffer = deque(maxlen=overlap)

    for i in range(0, total_subs, chunk_size):
        current_chunk = subs[i:min(i + chunk_size, total_subs)]
        # 合并上下文和当前块
        context_chunk = list(context_buffer) + current_chunk
        # 更新上下文缓存
        context_buffer.extend(current_chunk[-overlap:])
        yield context_chunk


def process_subtitle_segments(srt_file: str) -> None:
    full_name = os.path.basename(srt_file)
    name, *_ = os.path.splitext(full_name)
    qwen = Qwen(name)
    
    for chunk in read_subtitle_chunks(srt_file, chunk_size=700):
        # 将字幕块转换为文本
        chunk_text = " ".join([f"[{sub.start} --> {sub.end}] {sub.text}" for sub in chunk])
        # 调用通义千问进行主题分析
        qwen.req_qwen(chunk_text)
