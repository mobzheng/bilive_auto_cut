import asyncio
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from cuter import cut_video
from logger import setup_logger
from uploader import upload

logger = setup_logger('gui_processor')


class ProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("视频切片处理工具")
        self.root.geometry("800x600")

        self.json_path = None
        self.video_path = None
        self.segments_data = None

        # 创建新的事件循环
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, args=(self.loop,))
        self.thread.daemon = True  # 设置为守护线程，随主线程退出
        self.thread.start()

        self.create_widgets()

    def create_widgets(self):
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.root, text="文件选择")
        file_frame.pack(fill='x', padx=10, pady=5)

        # JSON文件选择
        ttk.Label(file_frame, text="分段JSON:").grid(row=0, column=0, padx=5, pady=5)
        self.json_label = ttk.Label(file_frame, text="未选择")
        self.json_label.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="选择JSON", command=self.select_json).grid(row=0, column=2, padx=5, pady=5)

        # 视频文件选择
        ttk.Label(file_frame, text="视频文件:").grid(row=1, column=0, padx=5, pady=5)
        self.video_label = ttk.Label(file_frame, text="未选择")
        self.video_label.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="选择视频", command=self.select_video).grid(row=1, column=2, padx=5, pady=5)

        # 分段列表
        list_frame = ttk.LabelFrame(self.root, text="分段列表")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.segments_tree = ttk.Treeview(list_frame, columns=('start', 'end', 'title'), show='headings')
        self.segments_tree.heading('start', text='开始时间')
        self.segments_tree.heading('end', text='结束时间')
        self.segments_tree.heading('title', text='标题')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.segments_tree.yview)
        self.segments_tree.configure(yscrollcommand=scrollbar.set)

        self.segments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 处理按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=10, pady=5)

        self.process_btn = ttk.Button(btn_frame, text="开始处理", command=self.start_processing)
        self.process_btn.pack(side='left', padx=5)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)

    def select_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=os.getcwd()
        )
        if file_path:
            self.json_path = file_path
            self.json_label.config(text=os.path.basename(file_path))
            self.load_segments()

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("视频文件", "*.mp4 *.flv *.avi *.mkv *.wmv *.mov *.webm"),
                ("MP4文件", "*.mp4"),
                ("FLV文件", "*.flv"),
                ("AVI文件", "*.avi"),
                ("MKV文件", "*.mkv"),
                ("WMV文件", "*.wmv"),
                ("MOV文件", "*.mov"),
                ("WebM文件", "*.webm"),
                ("所有文件", "*.*")
            ],
            initialdir=os.getcwd()
        )
        if file_path:
            self.video_path = file_path
            self.video_label.config(text=os.path.basename(file_path))

    def load_segments(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.segments_data = json.load(f)

            # 清空现有列表
            for item in self.segments_tree.get_children():
                self.segments_tree.delete(item)

            # 添加分段信息
            if 'segments' in self.segments_data:
                for segment in self.segments_data['segments']:
                    self.segments_tree.insert('', 'end', values=(
                        segment['start_time'],
                        segment['end_time'],
                        segment['title']
                    ))
        except Exception as e:
            messagebox.showerror("错误", f"加载JSON失败: {str(e)}")

    async def process_video(self):
        try:
            if not self.json_path or not self.video_path:
                messagebox.showwarning("警告", "请先选择JSON文件和视频文件")
                return

            # 执行切片
            async for title, cut_path in await self.root.async_call(cut_video, self.segments_data):
                # 上传切片
                try:
                    await self.root.async_call(upload, title, cut_path)
                    logger.info(f"上传完成: {title}")
                except Exception as e:
                    logger.error(f"上传失败 {title}: {str(e)}")

            messagebox.showinfo("完成", "所有任务处理完成")
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.process_btn.config(state='normal')

    def _start_loop(self, loop):
        """在新线程中运行事件循环"""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start_processing(self):
        self.process_btn.config(state='disabled')
        self.progress.pack(fill='x', padx=10, pady=5)
        self.progress.start()
        
        # 在事件循环中安排协程执行
        asyncio.run_coroutine_threadsafe(self.process_video(), self.loop)

    def __del__(self):
        """清理事件循环"""
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()

    # 在文件顶部添加导入
    import threading


# 添加异步支持
class AsyncRoot(tk.Tk):
    async def async_call(self, func, *args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(None, func, *args, **kwargs)


if __name__ == "__main__":
    root = AsyncRoot()
    app = ProcessorGUI(root)
    root.mainloop()
