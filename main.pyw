import json
import os
import threading
import time
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.filedialog as fdl
from tkinter import ttk

import edit_gui
import project_class as pc

def wait():
    global num_n, ni
    ans = project_list[ti].gen_intellij_run()
    if ni == 20:
        msgbox.showerror("构建进度条", "目前无法把您的我的世界模组构建成功，请咨询专业人员，错误日志：\n" + str(project_list[ti].e))
        return
    if ans == "Yes":
        num_n = 100
    else:
        num_n = 50
        ni += 1
        lbl2.configure(text=f"（正在构建项目，第{ni}次尝试）：")
        threading.Thread(target=wait).start()


def update_progress():
    """在主线程中更新进度条（Tkinter安全更新）"""
    global num_n
    if num_n < 89:
        num_n += 1
        progressbar.configure(value=num_n)
    if num_n == 100:
        progressbar.configure(value=100)
        lbl2.configure(text="（构建成功）：")
        threading.Thread(target=edit_gui.edit, args=(project_list[ti],)).start()
        progress_root.destroy()
        time.sleep(0.5)
        exit()
    else:
        time.sleep(0.5)
        threading.Thread(target=update_progress).start()


def run_n(name, mod_id, author, js):
    global num_n
    project_list.append(pc.Project(name, mod_id, author, js))
    progressbar.configure(value=50)
    lbl2.configure(text="（正在构建项目，第1次尝试）：")
    threading.Thread(target=wait).start()
    update_progress()

def new_pj(name, mod_id, author, js):
    if os.path.exists(str(os.path.join(os.path.dirname(os.path.abspath(__file__)), "project", "TI_" + mod_id))):
        msgbox.showerror("新建项目", "已有同名项目")
        return
    global num_n, progressbar, lbl2, progress_root
    progress_root = tk.Tk()
    progress_root.title("生成进度条")
    progress_root.geometry("600x50")
    progress_root.resizable(False, False)

    lbl1 = tk.Label(progress_root, text="生成进度")
    lbl2 = tk.Label(progress_root, text="（正在生成项目文件）：")
    progressbar = ttk.Progressbar(progress_root, orient="horizontal", length=370, mode="determinate", maximum=100)

    lbl1.pack(side="left")
    lbl2.pack(side="left")
    progressbar.pack(side="left")

    threading.Thread(target=run_n, args=(name, mod_id, author, js)).start()

    progress_root.mainloop()

    root.destroy()

def create_project():
    global lbl2
    settings_root = tk.Toplevel(root)
    settings_root.title("新建项目")
    settings_root.geometry("500x600")
    lbl1 = tk.Label(settings_root, text="mod_id(模组唯一ID，全小写，也是项目名)：")
    ent1 = tk.Entry(settings_root, width=100)
    lbl2 = tk.Label(settings_root, text="模组中文名：")
    ent2 = tk.Entry(settings_root, width=100)
    lbl3 = tk.Label(settings_root, text="作者（多个作者用“, ”间隔）：")
    ent3 = tk.Entry(settings_root, width=100)
    lbl4 = tk.Label(settings_root, text="模组描述：")
    text4 = tk.Text(settings_root, width=100, height=10)
    btn3 = tk.Button(settings_root, text="创建", width=20, height=3, command=lambda: (threading.Thread(target=new_pj, args=(ent2.get(), ent1.get(), ent3.get(), text4.get(1.0, "end"))).start(), settings_root.destroy()))
    btn4 = tk.Button(settings_root, text="取消", width=20, height=3, command=lambda: settings_root.destroy())

    lbl1.pack(expand=True)
    ent1.pack(expand=True)
    lbl2.pack(expand=True)
    ent2.pack(expand=True)
    lbl3.pack(expand=True)
    ent3.pack(expand=True)
    lbl4.pack(expand=True)
    text4.pack(expand=True)
    btn3.pack(side="left", expand=True)
    btn4.pack(side="left", expand=True)

def open_project():
    filename = fdl.askdirectory(initialdir=str(os.path.join(os.path.dirname(os.path.abspath(__file__)), "project")), title="项目目录", mustexist=True)
    if filename:
        if os.path.exists(os.path.join(filename, "config.json")):
            with open(str(os.path.join(filename, "config.json")), "r") as f:
                 docs = json.loads(f.read())
            project_list.append(pc.Project(docs["name"], docs["mod_id"], docs["author"], docs["description"], filename, docs["items"], docs["blocks"], docs["item_inventories"]))
            threading.Thread(target=edit_gui.edit, args=(project_list[ti],)).start()
            exit()
        else:
            msgbox.showerror("错误", "这不是通过我的世界生成器生成的MOD")
# 初始化
root = tk.Tk()
root.deiconify()
root.title("我的世界1.20.1模组编辑器")
root.geometry("500x400")
project_list = []
progressbar = ttk.Progressbar(root)
progress_root = tk.Label(root)
lbl2 = tk.Label(root)
num_n = 50
ni = 1
ti = 0

# 添加菜单
ProjectMenu = tk.Menu(root, tearoff=False)
ProjectMenu.add_command(label="新建项目", command=lambda: threading.Thread(target=create_project).start())
ProjectMenu.add_command(label="打开项目", command=lambda: threading.Thread(target=open_project).start())

MainMenu = tk.Menu(root, tearoff=False)
root.config(menu=MainMenu)
MainMenu.add_cascade(label="项目", menu=ProjectMenu)

btn1 = tk.Button(root, text="新建项目", width=20, height=5, command=lambda: threading.Thread(target=create_project).start())
btn2 = tk.Button(root, text="打开项目", width=20, height=5, command=lambda: threading.Thread(target=open_project).start())

btn1.pack(side="left", expand=True)
btn2.pack(side="left", expand=True)

root.mainloop()
