import sys

from openai import OpenAI

from config import QWEN_CONFIG
from logger import setup_logger


class Qwen:
    def __init__(self, title: str):
        self.client = OpenAI(
            api_key=QWEN_CONFIG["api_key"],
            base_url=QWEN_CONFIG["base_url"]
        )
        self.title = title
        self.logger = setup_logger('qwen')

    def __req_qwen(self, text: str):
        try:
            reasoning_content = ""
            answer_content = ""
            is_answering = False

            system_prompt = """
                    请分析以下字幕内容，根据主题和内容的变化进行分段。对于每个分段：
        
                    1. 标题要求：
                       - 长度不超过20字
                       - 突出核心话题或金句
                       - 适合短视频平台传播
                       - 避免过于学术化的表述
                       - 可以适当使用网络热词或流行语
        
                    2. 时间标记：
                       - 标记该分段的起始和结束时间
                       - 确保时间点在自然的话题转换处
                       - 避免在句子中间切断
        
                    3. 内容概要要求：
                       - 篇幅50-100字
                       - 突出观点和论据
                       - 保留精彩的例证或类比
                       - 概括核心论点和结论
                       - 使用简洁明了的语言
        
                    分段原则：
                    - 优先考虑内容的完整性和逻辑连贯性
                    - 建议单个片段时长3-8分钟，重要话题可适当延长
                    - 重大话题转换处必须分段
                    - 注意节奏感，避免过长或过短
                    - 保持适合短视频平台的节奏
        
                    请按以下格式返回结果：
                    分段1：
                    - 时间：[起始时间] --> [结束时间]
                    - 标题：xxx
                    - 内容概要：xxx
        
                    分段2：
                    ...
                    """

            messages = [
                {"role": "assistant", "content": system_prompt},
                {"role": "user", "content": text}
            ]

            # 创建聊天完成请求
            completion = self.client.chat.completions.create(
                model=QWEN_CONFIG["model"],
                messages=messages,
                stream=True
            )
            # print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
            for chunk in completion:
                # 如果chunk.choices为空，则打印usage
                if not chunk.choices:
                    print("\nUsage:")
                    print(chunk.usage)
                else:
                    delta = chunk.choices[0].delta
                    # 打印思考过程
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                        # print(delta.reasoning_content, end='', flush=True)
                        reasoning_content += delta.reasoning_content
                    else:
                        # 开始回复
                        if delta.content != "" and is_answering is False:
                            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                            is_answering = True
                        # 打印回复过程
                        print(delta.content, end='', flush=True)
                        answer_content += delta.content
            # self.message_queue.append({"role": "assistant", "content": answer_content})
            print("\n")
        except Exception as e:
            self.logger.error(f"请求失败: {str(e)}")
            raise

    def req_qwen(self, text: str):
        try:
            with open(f'{self.title}.txt', "a", encoding="utf-8") as f:
                sys.stdout = f
                self.__req_qwen(text)
        except Exception as e:
            self.logger.error(f"处理失败: {str(e)}")
            raise
        finally:
            sys.stdout = sys.__stdout__
