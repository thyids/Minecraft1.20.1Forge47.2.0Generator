from tkinter import ttk
import tkinter as tk


class ProjectTreeView:
    def __init__(self, root):
        self.e = None
        self.root = root

        self.menu = tk.Menu(root, tearoff=False)

        self.scrollbar = ttk.Scrollbar(root)
        self.scrollbar.pack(side='right', fill='y')

        self.tree = ttk.Treeview(
            root,
            yscrollcommand=self.scrollbar.set,
            show='tree'
        )
        self.scrollbar.config(command=self.tree.yview)

        self.folder_icon = "📁"
        self.file_icon = "📄"

        self.tree.bind('<Double-1>', self.on_double_click)

    def add_node(self, parent, text, is_folder=True):
        """添加节点到树中"""
        icon = self.folder_icon if is_folder else self.file_icon
        return self.tree.insert(parent, 'end', text=f"{icon} {text}")

    def on_double_click(self, event):
        """双击节点事件"""
        self.e = event
        item = self.tree.selection()[0]
        if self.tree.item(item, 'text').startswith(self.folder_icon):
            # 切换文件夹展开/折叠状态
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)

    def pack(self):
        self.tree.pack(fill="y", expand=True)