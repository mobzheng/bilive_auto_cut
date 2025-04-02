import re
import json
import os.path
from dataclasses import dataclass, asdict
from typing import List

from logger import setup_logger

logger = setup_logger('segment_parser')


@dataclass
class Segment:
    start_time: str
    end_time: str
    title: str
    summary: str


class SegmentParser:
    @staticmethod
    def parse_time(time_str: str) -> str:
        try:
            # 移除方括号并分割
            time = time_str.strip('[]')
            if ',' in time:  # 如果包含毫秒
                time = time.split(',')[0]

            # 确保时间格式为 HH:MM:SS
            parts = time.split(':')
            if len(parts) == 2:  # 如果只有分和秒
                parts.insert(0, '00')
            return ':'.join(parts)
        except Exception as e:
            logger.error(f"时间格式解析失败: {time_str}, 错误: {str(e)}")
            raise

    @staticmethod
    def parse_segments(content: str) -> List[Segment]:
        try:
            segments = []

            # 首先找到完整回复部分
            response_pattern = r"={20}完整回复={20}\n(.*?)(?:\n={20}|$)"
            response_match = re.search(response_pattern, content, re.DOTALL)

            if not response_match:
                logger.warning("未找到完整回复部分")
                return segments

            response_content = response_match.group(1)

            # 查找所有分段
            pattern = r"分段\d+：\s*\n- 时间：\[(.*?)\] --> \[(.*?)\]\s*\n- 标题：(.*?)\s*\n- 内容概要：(.*?)(?=\n\n分段\d+：|$)"
            matches = re.finditer(pattern, response_content, re.DOTALL)

            for match in matches:
                try:
                    start_time = SegmentParser.parse_time(match.group(1))
                    end_time = SegmentParser.parse_time(match.group(2))
                    title = match.group(3).strip()
                    summary = match.group(4).strip()

                    segments.append(Segment(start_time, end_time, title, summary))
                except Exception as e:
                    logger.error(f"分段解析失败: {match.group(0)}, 错误: {str(e)}")
                    continue

            if not segments:
                logger.warning("未找到任何有效分段")

            return segments

        except Exception as e:
            logger.error(f"解析失败: {str(e)}")
            raise

    @staticmethod
    def save_segments(segments: List[Segment], output_file: str) -> None:
        try:
            # 获取视频名称
            name, _ = os.path.splitext(os.path.basename(output_file))
            
            # 构建JSON结构
            result = {
                "video_name": name,
                "total_segments": len(segments),
                "segments": [asdict(segment) for segment in segments]
            }

            # 确保输出文件使用.json扩展名
            json_file = f"{os.path.splitext(output_file)[0]}.json"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"分段信息已保存至: {json_file}")
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            raise


def process_ai_response(input_file: str, output_file: str) -> None:
    try:
        # 读取AI回答文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 获取输出文件名（不含扩展名）
        output_name = os.path.splitext(input_file)[0]
        
        # 解析分段信息
        parser = SegmentParser()
        segments = parser.parse_segments(content)

        # 保存结构化数据
        parser.save_segments(segments, f"{output_name}_segments")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise


if __name__ == "__main__":
    input_file = "20250314-150450-812-升哥下午茶.txt"
    output_file = "segments.txt"
    process_ai_response(input_file, output_file)
