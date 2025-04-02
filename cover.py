import os

from PIL import Image, ImageDraw, ImageFont


class CoverGenerator:
    def __init__(self, template_path=None, output_dir="covers", width=1080, height=1920):
        """初始化封面生成器"""
        self.output_dir = output_dir
        self.width = width
        self.height = height

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 加载模板或创建空白模板
        if template_path and os.path.exists(template_path):
            self.template = Image.open(template_path).resize((self.width, self.height))
        else:
            # 创建默认深灰色背景
            self.template = self._create_gradient_background((50, 50, 50), (30, 30, 30))

        # 加载字体
        self.title_font = ImageFont.truetype("simhei.ttf", 50)
        self.subtitle_font = ImageFont.truetype("simhei.ttf", 30)
        self.tag_font = ImageFont.truetype("simhei.ttf", 24)

    def _create_gradient_background(self, color1, color2):
        """创建渐变背景"""
        background = Image.new('RGB', (self.width, self.height), color1)
        draw = ImageDraw.Draw(background)

        for y in range(self.height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / self.height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / self.height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / self.height)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return background

    def _add_overlay(self, image, opacity=0.3):
        """添加半透明遮罩，使文字更易读"""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, int(255 * opacity)))
        return Image.alpha_composite(image.convert('RGBA'), overlay)

    def _wrap_text(self, text, font, max_width):
        """文本自动换行"""
        if not text:
            return []

            # 对于中文文本，按字符分割更合适
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)

        if is_chinese:
            # 中文文本按字符处理
            result = []
            line = ""

            for char in text:
                test_line = line + char
                if font.getlength(test_line) <= max_width:
                    line = test_line
                else:
                    result.append(line)
                    line = char

            if line:
                result.append(line)
            return result
        else:
            # 英文文本按单词处理
            lines = []
            words = text.split()
            if not words:
                return []

            line = words[0]
            for word in words[1:]:
                test_line = line + ' ' + word
                if font.getlength(test_line) <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word

            if line:
                lines.append(line)
            return lines

    def generate_cover(self, title, subtitle=None, tags=None, host_image=None, background_image=None,
                       output_filename=None):
        """生成封面图片"""
        # 创建基础图像
        if background_image and os.path.exists(background_image):
            base = Image.open(background_image).resize((self.width, self.height))
            # 添加半透明遮罩使文字更易读
            base = self._add_overlay(base)
        else:
            base = self.template.copy()

        # 转换为RGBA模式以支持透明度
        if base.mode != 'RGBA':
            base = base.convert('RGBA')

        # 添加主持人图像
        if host_image and os.path.exists(host_image):
            host = Image.open(host_image)
            # 调整主持人图像大小
            host_width = int(self.width * 0.3)
            host_height = int(host_width * host.height / host.width)
            host = host.resize((host_width, host_height))

            # 将主持人图像放在右下角
            base.paste(host, (self.width - host_width - 50, self.height - host_height - 50),
                       host if host.mode == 'RGBA' else None)

        draw = ImageDraw.Draw(base)

        # 添加标题
        wrapped_title = self._wrap_text(title, self.title_font, self.width - 100)
        title_height = len(wrapped_title) * self.title_font.size
        y_position = (self.height - title_height) // 2 - 50  # 标题位置偏上

        for line in wrapped_title:
            # 添加文字阴影
            shadow_offset = 3
            text_width = self.title_font.getlength(line)
            x_position = (self.width - text_width) // 2

            # 绘制阴影
            draw.text((x_position + shadow_offset, y_position + shadow_offset),
                      line, font=self.title_font, fill=(0, 0, 0, 180))

            # 绘制文字
            draw.text((x_position, y_position), line, font=self.title_font, fill=(255, 215, 0))
            y_position += self.title_font.size + 10

        # 添加副标题
        if subtitle:
            wrapped_subtitle = self._wrap_text(subtitle, self.subtitle_font, self.width - 150)
            y_position += 20  # 与标题保持一定距离

            for line in wrapped_subtitle:
                text_width = self.subtitle_font.getlength(line)
                x_position = (self.width - text_width) // 2

                # 绘制阴影
                draw.text((x_position + 2, y_position + 2),
                          line, font=self.subtitle_font, fill=(0, 0, 0, 180))

                # 绘制文字
                draw.text((x_position, y_position), line, font=self.subtitle_font, fill=(255, 200, 0))
                y_position += self.subtitle_font.size + 5

        # 添加标签
        if tags:
            y_position = self.height - 80
            x_position = 50

            for tag in tags:
                tag_text = f"#{tag}"
                tag_width = self.tag_font.getlength(tag_text)

                # 绘制标签背景
                draw.rectangle([(x_position - 5, y_position - 5),
                                (x_position + tag_width + 5, y_position + self.tag_font.size + 5)],
                               fill=(0, 0, 0, 128))

                # 绘制标签文字
                draw.text((x_position, y_position), tag_text, font=self.tag_font, fill=(255, 255, 255))
                x_position += tag_width + 20

        # 保存图像
        if not output_filename:
            # 使用标题的前几个字作为文件名
            short_title = title[:10].replace(" ", "_").replace("？", "").replace("！", "")
            output_filename = f"{short_title}.png"

        output_path = os.path.join(self.output_dir, output_filename)
        base.convert('RGB').save(output_path)
        print(f"封面已保存至: {output_path}")
        return output_path

#
# # 使用示例
# if __name__ == "__main__":
#     generator = CoverGenerator()
#
#     # 为不同视频生成封面
#     generator.generate_cover(
#         title="《唐朝豪放女》深度解析",
#         subtitle="升哥揭秘1984年港片经典的超前思想",
#         tags=["电影解析", "港片经典", "女性觉醒"],
#         output_filename="tangchao_analysis.png"
#     )
#
#     generator.generate_cover(
#         title="徐静雨现象批判",
#         subtitle="升哥解析：为什么不懂篮球也能成为篮球网红？",
#         tags=["网红现象", "篮球", "男性心理"],
#         output_filename="xujingyu_critique.png"
#     )
#
#     generator.generate_cover(
#         title="连麦职业建议",
#         subtitle="26岁学吊车来得及吗？升哥现场指导入行捷径",
#         tags=["职业建议", "技术工种", "转行指南"],
#         output_filename="career_advice.png"
#     )
#
#     generator.generate_cover(
#         title="无间道解析",
#         subtitle="为何成为经典？升哥剖析港片黄金时代的巅峰之作",
#         tags=["电影解析", "港片经典", "刘德华", "梁朝伟"],
#         output_filename="infernal_affairs.png"
#     )
#
# generator.generate_cover(
#     title="王者qq区和微信区要不要喷",
#     subtitle="升哥揭秘游戏区服差异与玩家心理",
#     tags=["王者荣耀", "游戏", "区服对比"],
#     output_filename="honor_of_kings.png"
# )
#
#     generator.generate_cover(
#         title="年轻人把精力用在这事上面就废了",
#         subtitle="升哥人生忠告：避开这些时间黑洞",
#         tags=["人生建议", "时间管理", "升哥金句"],
#         output_filename="youth_advice.png"
#     )
