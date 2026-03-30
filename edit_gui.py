import os
import json
import shutil
import threading
import time
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fdl
from tkinter import simpledialog as sdl
import tkinter.messagebox as msgbox
import project_class
import ProjectTreeView

code_root = None
resource_root = None

def edit(project):
    def question(title, kwargs):
        q_root = tk.Tk()
        q_root.title(title)

        qqlist = []
        for arg in kwargs.keys():
            lbl = tk.Label(q_root, text=arg + ": ")
            lbl.pack(expand=True)
            text = tk.StringVar(q_root)
            text.set("")
            if kwargs[arg] == "text" or kwargs[arg].split("_")[0] == "open":

                ent = tk.Entry(q_root, textvariable=text)
                ent.pack(expand=True)
                if kwargs[arg].split("_")[0] == "open":
                    sp = kwargs[arg].split("_")
                    def open_file(sp=sp, text=text):
                        path = fdl.askopenfilename(filetypes=[(sp[1], "*." + sp[2])],
                                                   parent=q_root, title=title)
                        text.set(path)

                    btn = tk.Button(q_root, text="打开", command=lambda: threading.Thread(target=open_file).start())
                    btn.pack(expand=True)
                qqlist.append([arg, text])
            elif kwargs[arg].split("/")[0] == "choose":
                text.set(kwargs[arg].split("/")[1])
                op = tk.OptionMenu(q_root, text, *kwargs[arg].split("/")[1:])
                op.pack(expand=True)
                qqlist.append([arg, text])

        ans = {'no_no_no_no_no': 1}

        def yes():
            for qlist in qqlist:
                ans[qlist[0]] = qlist[1].get()
                if ans[qlist[0]] == "":
                    msgbox.showerror(title, f"{qlist[0]}不能为空")
                    return
            ans['no_no_no_no_no'] = 0
            q_root.destroy()

        def no():
            q_root.destroy()

        yes_btn = tk.Button(q_root, text="确定", command=yes)
        no_btn = tk.Button(q_root, text="取消", command=no)

        yes_btn.pack(side="left")
        no_btn.pack(side="right")

        q_root.mainloop()

        if ans['no_no_no_no_no'] == 0:
            del ans['no_no_no_no_no']
            return ans
        else:
            return None

    def change_en_us(param, b_name):
        with open(project.project_dir + "\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % project.mod_id, "r",
                  encoding="utf-8") as file:
            data = json.load(file)

        data[param] = b_name

        with open(project.project_dir + "\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % project.mod_id, "w",
                  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def create_block():
        pass

    def create_item():
        ins = ""
        for key in project.item_inventories.keys():
            ins += "/" + key
        chinese_name, item_id, res_path, tabs = question("创建物品", {"中文名": "text", "物品id": "text", "材质文件": "open_16位材质文件_png", "物品栏": "choose/无/原料" + ins}).values()
        res_path = str(res_path).replace("/", "\\")
        print(res_path)
        if item_id in project.items.keys():
            msgbox.showerror("创建物品", "物品id已经存在")
            return

        if tabs != "原料" and tabs != "无" and tabs not in project.item_inventories:
            msgbox.showerror("创建物品", "没有物品栏")
            return

        lbl2.configure(text=f"正在创建物品")

        with open(project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java", "r",
                  encoding="utf-8") as f:
            ModItems = f.readlines()

        for i in range(len(ModItems)):
            if ModItems[i] == f"            DeferredRegister.create(ForgeRegistries.ITEMS, {project.mod_id.capitalize()}.MOD_ID);\n":
                ModItems.insert(i + 1,
                                f"\n    public static final RegistryObject<Item> {item_id.upper()} = ITEMS.register(\"{item_id.lower()}\", () -> new Item(new Item.Properties()));")
                break

        with open(project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java", "w",
                  encoding="utf-8") as f:
            f.writelines(ModItems)

        if tabs == "原料":
            tabs = "INGREDIENTS"
            with open(project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java", "r",
                      encoding="utf-8") as f:
                ModItems = f.readlines()

            for i in range(len(ModItems)):
                if ModItems[i] == "        // this_insert_wpl\n":
                    ModItems.insert(i + 1,
                                    "        if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModItems.%s);\n        }\n" % (
                                        tabs, item_id.upper()))
                    break

            with open(project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java", "w",
                      encoding="utf-8") as f:
                f.writelines(ModItems)
        elif tabs == "无":
            pass
        else:
            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModCreativeModeTabs.java",
                    "r",
                    encoding="utf-8") as f:
                ModCreativeModeTabs = f.readlines()

            for i in range(len(ModCreativeModeTabs)):
                if "pOutput.accept" in ModCreativeModeTabs[i] or ModCreativeModeTabs[i] in "pOutput.accept":
                    ModCreativeModeTabs.insert(i,
                                               "\n        pOutput.accept(ModItems.%s.get());\n" % (
                                                   item_id.upper()))
                    break

            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModCreativeModeTabs.java",
                    "w",
                    encoding="utf-8") as f:
                f.writelines(ModCreativeModeTabs)

        change_en_us("item.%s.%s" % (project.mod_id, item_id), chinese_name)

        data = {
            "parent": "item/generated",
            "textures": {
                "layer0": "%s:item/%s" % (project.mod_id, item_id),
            }
        }

        with open(project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\models\\item\\{item_id}.json", "w",
                  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        add_file_to_tree(f"assets\\{project.mod_id}\\models\\item\\{item_id}.json", resource_root)

        assets_item_path = project.project_dir + f'\\src\\main\\resources\\assets\\{project.mod_id}\\textures\\item\\{item_id}.png'
        print(assets_item_path)

        os.system(F"copy {res_path} {assets_item_path}")

        add_file_to_tree("assets\\%s\\textures\\item\\%s.png" % (project.mod_id, item_id.lower()), resource_root)

        project.items[item_id] = chinese_name
        project.write_json()

        lbl2.configure(text=f"创建物品成功")
        time.sleep(1)
        text1.configure(state="normal")
        text1.delete(1.0, tk.END)
        with open(project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java", "r", encoding="utf-8", errors="ignore") as ff:
            text1.insert(tk.END, ff.read())
            lbl2.configure(text="路径：" + project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java")

    def delete_block():
        pass

    def delete_item():
        pass

    def show_menu(event):
        treeview.menu.post(event.x_root, event.y_root)

    def build_mod(i, text):
        lbl2.configure(text=f"正在构建（第{i}次尝试）")
        y = project.gen_intellij_run()
        if y:
            lbl2.configure(text="构建成功")
            time.sleep(1)
            lbl2.configure(text=text)
        else:
            if i != 15:
                build_mod(i+1, text)
            else:
                lbl2.configure(text="构建失败")
                time.sleep(1)
                lbl2.configure(text=text)
    def gen_jar(i, text):
        lbl2.configure(text=f"正在生成jar（第{i}次尝试）")
        y = project.build_jar()
        if y:
            lbl2.configure(text="生成成功，请选择保存位置")
            filename = fdl.asksaveasfilename(parent=root, filetypes=[("模组", "*.jar")], title="选择模组保存位置", initialdir=project.project_dir, initialfile=project.mod_id + ".jar")
            if filename:
                if str(filename)[-4:] != ".jar":
                    filename += ".jar"
                shutil.move(project.project_dir + "\\build\\libs\\" + project.mod_id + "-1.0.0-Minecraft1.20.1-Forge47.2.0.jar", filename)
            time.sleep(1)
            lbl2.configure(text=text)
        else:
            if i != 15:
                gen_jar(i+1, text)

    def get_path(item, is_path = 1):
        try:
            path = treeview.tree.item(treeview.tree.parent(item), "text").split(' ', 1)[1] + "\\" + \
                   treeview.tree.item(item, "text").split(' ', 1)[1]
            item = treeview.tree.parent(item)
            while 1:
                try:
                    path = treeview.tree.item(treeview.tree.parent(item), "text").split(' ', 1)[1] + "\\" + path
                    item = treeview.tree.parent(item)
                except IndexError:
                    break
            path_list = path.split("\\", 1)
            if path_list[0] == "Code":
                path = os.path.join(project_java_path, path_list[1])
            else:
                path = os.path.join(project_resources_path, path_list[1])
            if is_path:
                return path
            else:
                return path, path_list[1]
        except Exception as e:
            print(e)
            return False

    def create_java():
        item = treeview.tree.selection()[0]
        print(type(item))
        path = get_path(item, 0)
        if path[0]:
            ask_name = sdl.askstring(title="新建java类", prompt="请输入类名", parent=root)
            if ask_name:
                lbl_y = lbl2["text"]
                lbl2.configure(text="正在创建java类")
                ask_path = ask_name
                if ask_path[-5:] != ".java":
                    ask_path += ".java"
                package = f"package com.{project.author}.{project.mod_id}"
                for name in path[1].split("\\"):
                    package += "." + name
                print(path[1])
                package += ";"
                with open(os.path.join(path[0], ask_path), "w", encoding="utf-8") as ff:
                    ff.write(package + "\n" + "public class %s {" % ask_name + "\n    \n" + "}")
                treeview.add_node(item, ask_path, False)
                print(item, ask_path)
                lbl2.configure(text="创建成功")
                time.sleep(1)
                lbl2.configure(text=lbl_y)

    def create_folder():
        item = treeview.tree.selection()[0]
        path = get_path(item)
        print(path)
        if path:
            ask_name = sdl.askstring(title="新建文件夹", prompt="请输入文件夹名", parent=root)
            if ask_name:
                print(os.path.join(path, ask_name))
                lbl_y = lbl2["text"]
                lbl2.configure(text="正在创建文件夹")
                os.makedirs(os.path.join(path, ask_name))
                treeview.add_node(item, ask_name)
                lbl2.configure(text="创建成功")
                time.sleep(0.7)
                lbl2.configure(text=lbl_y)

    def create_file():
        item = treeview.tree.selection()[0]
        path = get_path(item)
        if path:
            ask_name = sdl.askstring(title="新建文件", prompt="请输入文件名", parent=root)
            if ask_name:
                lbl_y = lbl2["text"]
                lbl2.configure(text="正在创建文件")
                with open(os.path.join(path, ask_name), "w", encoding="utf-8") as ff:
                    ff.write("")
                treeview.add_node(item, ask_name, False)
                lbl2.configure(text="创建成功")
                time.sleep(1)
                lbl2.configure(text=lbl_y)

    def delete_file():
        item = treeview.tree.selection()[0]
        path = get_path(item)
        if path:
            get_item_name = treeview.tree.item(item, 'text')
            file = "文件"
            if get_item_name.startswith(treeview.folder_icon):
                file = "文件夹"
            if msgbox.askokcancel("删除", f"确定要 {get_item_name[1:]} {file}吗？（他会消失很久）", parent=root):
                lbl_y = lbl2["text"]
                lbl2.configure(text="正在删除文件/文件夹")
                if get_item_name.startswith(treeview.folder_icon):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                treeview.tree.delete(item)
                lbl2.configure(text="删除成功")
                time.sleep(1)
                lbl2.configure(text=lbl_y)


    def on_double_click(event):
        print(event)
        item = treeview.tree.selection()[0]
        if treeview.tree.item(item, 'text').startswith(treeview.file_icon):
            path = get_path(item)
        else:
            path = False
        if path:
            text1.configure(state="normal")
            text1.delete(1.0, tk.END)
            with open(path, "r", encoding="utf-8", errors="ignore") as ff:
                text1.insert(tk.END, ff.read())
                lbl2.configure(text="路径：" + path)

    def add_project(path, parent):
        file_list = os.listdir(path)
        for file_name in file_list:
            if os.path.isdir(os.path.join(path, file_name)):
                node = treeview.add_node(parent, file_name)
                add_project(os.path.join(path, file_name), node)
            else:
                treeview.add_node(parent, file_name, False)

    def add_project_file():
        global code_root, resource_root
        code_root = treeview.add_node("", "Code")
        add_project(project_java_path, code_root)
        resource_root = treeview.add_node("", "Resource")
        add_project(project_resources_path, resource_root)


    def tab_insert(event):
        print(event)
        text1.insert(tk.INSERT, "    ")
        text1.edit_separator()
        return "break"

    def undo(event):
        print(event)
        try:
            text1.edit_undo()
        except tk.TclError:
            pass

        return "break"
    def redo(event):
        print(event)
        try:
            text1.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def save_file(event):
        print(event)
        path = lbl2['text'].split("：", 1)[1]
        with open(path, "w", encoding="utf-8", errors="ignore") as ff:
            ff.write(text1.get("1.0", "end"))
        lbl2.configure(text="保存成功")
        time.sleep(1)
        lbl2.configure(text="路径：" + path)

    def add_separator(event):
        ignore_keys = ["Shift_L", "Shift_R", "Control_L", "Control_R",
                       "Alt_L", "Alt_R", "Caps_Lock", "Tab", "Return"]
        if event and event.keysym in ignore_keys:
            return
        text1.edit_separator()

    def add_file_to_tree(file_path, root_node):
        try:
            rel_path = file_path
            parts = rel_path.split(os.sep)
            current = root_node
            for part in parts:
                children = treeview.tree.get_children(current)
                node = None
                for child in children:
                    if part in treeview.tree.item(child, "text"):
                        node = child
                        break
                if not node:
                    full = os.path.join(project.project_dir, *parts[:parts.index(part) + 1])
                    is_dir = os.path.isdir(full)
                    node = treeview.add_node(current, part, is_dir)
                    print(file_path, "成功")
                else:
                    print(file_path, "error")
                current = node
        except Exception as e:
            print(file_path,e)

    with open(str(os.path.join(project.project_dir, "config.json")), "r") as f:
        docs = json.loads(f.read())
    print(docs["name"], docs["mod_id"], docs["author"], docs["description"])
    root = tk.Tk()
    root.title("项目：" + docs["name"])
    root.geometry("1000x700")
    project_java_path = str(os.path.join(project.project_dir, "src", "main", "java", "com", docs["author"], docs["mod_id"]))
    project_resources_path = str(os.path.join(project.project_dir, "src", "main", "resources"))

    new_menu = tk.Menu(root, tearoff=False)
    new_menu.add_command(label="添加物品",
                            command=lambda: threading.Thread(target=create_item, daemon=True).start())
    new_menu.add_command(label="添加方块",
                         command=lambda: threading.Thread(target=create_block, daemon=True).start())

    delete_menu = tk.Menu(root, tearoff=False)
    delete_menu.add_command(label="删除物品",
                            command=lambda: threading.Thread(target=delete_item, daemon=True).start())
    delete_menu.add_command(label="删除方块",
                            command=lambda: threading.Thread(target=delete_block, daemon=True).start())

    build_menu = tk.Menu(root, tearoff=False)
    build_menu.add_command(label="重新构建",
                         command=lambda: threading.Thread(target=build_mod, args=(1, lbl2["text"]), daemon=True).start())
    build_menu.add_command(label="生成jar模组",
                         command=lambda: threading.Thread(target=gen_jar, args=(1, lbl2["text"]), daemon=True).start())

    main_menu = tk.Menu(root, tearoff=False)
    root.config(menu=main_menu)
    main_menu.add_cascade(label="添加游戏玩法", menu=new_menu)
    main_menu.add_cascade(label="删除游戏玩法", menu=delete_menu)
    main_menu.add_cascade(label="构建", menu=build_menu)

    left_frame = tk.Frame(root)
    lbl1 = tk.Label(left_frame, text="项目列表：")
    treeview = ProjectTreeView.ProjectTreeView(left_frame)
    treeview.tree.bind('<Double-1>', on_double_click)
    treeview.tree.bind('<Button-3>', show_menu)
    treeview.menu.add_command(label="新建文件夹", command=lambda: threading.Thread(target=root.after, args=(0, create_folder, ), daemon=True).start())
    treeview.menu.add_command(label="新建文件", command=lambda: threading.Thread(target=root.after, args=(0, create_file(), ), daemon=True).start())
    treeview.menu.add_command(label="新建java类", command=lambda: threading.Thread(target=root.after, args=(0, create_java(), ), daemon=True).start())
    treeview.menu.add_command(label="删除", command=lambda: threading.Thread(target=root.after, args=(0, delete_file(), ), daemon=True).start())
    treeview.tree.bind("<Delete>", lambda event: threading.Thread(target=root.after, args=(0, delete_file(), ), daemon=True).start())

    center_frame = tk.Frame(root)
    lbl2 = tk.Label(center_frame, text="路径：")
    scrollbar_x = ttk.Scrollbar(center_frame, orient="horizontal")
    scrollbar_y = ttk.Scrollbar(center_frame)
    text1 = tk.Text(center_frame, xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set, wrap="none", undo=True, maxundo=-1, state="disabled")
    scrollbar_x.config(command=text1.xview)
    scrollbar_y.config(command=text1.yview)
    text1.bind("<Control-z>", undo)
    text1.bind("<Control-y>", redo)
    text1.bind("<Control-Z>", undo)
    text1.bind("<Control-Y>", redo)
    text1.bind("<Control-S>", lambda event: threading.Thread(target=save_file, args=(event,), daemon=True).start())
    text1.bind("<Control-s>", lambda event: threading.Thread(target=save_file, args=(event,), daemon=True).start())
    text1.bind("<KeyRelease>", add_separator)
    text1.bind("<Delete>", add_separator)
    text1.bind("<BackSpace>", add_separator)
    text1.bind("<Tab>", tab_insert)

    left_frame.pack(side="left", fill="y")
    lbl1.pack(side="top")
    treeview.pack()
    threading.Thread(target=add_project_file, daemon=True).start()

    # right_frame = tk.Frame(root)
    # right_frame.pack(side="right", fill="y")

    center_frame.pack(fill="both", expand=True)
    lbl2.pack(side="top", fill="x")
    scrollbar_x.pack(side='bottom', fill='x')
    scrollbar_y.pack(side='right', fill='y')
    text1.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    edit(project_class.Project("thyids", "thyid", "thyi", "thy"))