import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class SegmentEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("分段编辑器")
        self.root.geometry("800x600")

        self.current_file = None
        self.segments_data = None
        
        # 添加文件名标签
        self.file_label = ttk.Label(self.root, text="当前文件: 未加载")
        self.file_label.pack(fill='x', padx=5, pady=2)

        self.create_widgets()

    def create_widgets(self):
        # 顶部按钮区
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(btn_frame, text="打开JSON", command=self.load_json).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="保存修改", command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="删除分段", command=self.delete_segment).pack(side='left', padx=5)

        # 分段列表
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.segments_tree = ttk.Treeview(list_frame, columns=('start', 'end', 'title', 'summary'), show='headings')
        self.segments_tree.heading('start', text='开始时间')
        self.segments_tree.heading('end', text='结束时间')
        self.segments_tree.heading('title', text='标题')
        self.segments_tree.heading('summary', text='内容概要')

        self.segments_tree.column('start', width=100)
        self.segments_tree.column('end', width=100)
        self.segments_tree.column('title', width=200)
        self.segments_tree.column('summary', width=400)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.segments_tree.yview)
        self.segments_tree.configure(yscrollcommand=scrollbar.set)

        self.segments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 编辑区域
        edit_frame = ttk.LabelFrame(self.root, text='编辑分段')
        edit_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(edit_frame, text='开始时间:').grid(row=0, column=0, padx=5, pady=5)
        self.start_var = tk.StringVar()
        self.start_entry = ttk.Entry(edit_frame, textvariable=self.start_var)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_frame, text='结束时间:').grid(row=0, column=2, padx=5, pady=5)
        self.end_var = tk.StringVar()
        self.end_entry = ttk.Entry(edit_frame, textvariable=self.end_var)
        self.end_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(edit_frame, text='标题:').grid(row=1, column=0, padx=5, pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(edit_frame, textvariable=self.title_var)
        self.title_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Label(edit_frame, text='内容概要:').grid(row=2, column=0, padx=5, pady=5)
        self.summary_text = tk.Text(edit_frame, height=4)
        self.summary_text.grid(row=2, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Button(edit_frame, text='更新分段', command=self.update_segment).grid(row=3, column=0, columnspan=4,
                                                                                  pady=10)

        # 绑定选择事件
        self.segments_tree.bind('<<TreeviewSelect>>', self.on_select)

    def load_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=os.getcwd()
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.segments_data = json.load(f)
                self.current_file = file_path
                # 更新文件名标签
                self.file_label.config(text=f"当前文件: {os.path.basename(file_path)}")
                self.refresh_tree()
                messagebox.showinfo("成功", "成功加载JSON文件")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")

    def refresh_tree(self):
        for item in self.segments_tree.get_children():
            self.segments_tree.delete(item)

        if self.segments_data and 'segments' in self.segments_data:
            for segment in self.segments_data['segments']:
                self.segments_tree.insert('', 'end', values=(
                    segment['start_time'],
                    segment['end_time'],
                    segment['title'],
                    segment['summary']
                ))

    def on_select(self, event):
        selected = self.segments_tree.selection()
        if not selected:
            return

        values = self.segments_tree.item(selected[0])['values']
        self.start_var.set(values[0])
        self.end_var.set(values[1])
        self.title_var.set(values[2])
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', values[3])

    def update_segment(self):
        selected = self.segments_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个分段")
            return

        # 更新树形视图
        self.segments_tree.item(selected[0], values=(
            self.start_var.get(),
            self.end_var.get(),
            self.title_var.get(),
            self.summary_text.get('1.0', 'end-1c')
        ))

        # 更新数据
        idx = self.segments_tree.index(selected[0])
        self.segments_data['segments'][idx].update({
            'start_time': self.start_var.get(),
            'end_time': self.end_var.get(),
            'title': self.title_var.get(),
            'summary': self.summary_text.get('1.0', 'end-1c')
        })

        messagebox.showinfo("成功", "分段更新成功")

    def save_changes(self):
        if not self.current_file or not self.segments_data:
            messagebox.showwarning("警告", "没有可保存的数据")
            return

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.segments_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def delete_segment(self):
        selected = self.segments_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个分段")
            return

        if messagebox.askyesno("确认", "确定要删除选中的分段吗？"):
            # 获取选中项的索引
            idx = self.segments_tree.index(selected[0])
            
            # 从数据中删除
            self.segments_data['segments'].pop(idx)
            
            # 从树形视图中删除
            self.segments_tree.delete(selected[0])
            
            # 更新总数
            self.segments_data['total_segments'] = len(self.segments_data['segments'])
            
            # 清空编辑区
            self.start_var.set('')
            self.end_var.set('')
            self.title_var.set('')
            self.summary_text.delete('1.0', tk.END)
            
            messagebox.showinfo("成功", "分段已删除")


if __name__ == "__main__":
    root = tk.Tk()
    app = SegmentEditor(root)
    root.mainloop()
