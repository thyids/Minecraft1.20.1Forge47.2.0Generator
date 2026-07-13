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
import ai_sidebar

code_root = None
resource_root = None


def edit(project):
    def question(title, kwargs):
        q_root = tk.Tk()
        q_root.title(title)
        q_root.attributes("-topmost", True)

        qqlist = []

        top_frame = tk.Frame(q_root)
        top_frame.pack(fill="x", padx=10, pady=5)

        grid_frame = tk.Frame(q_root)
        grid_frame.pack(pady=10)

        grid_rows = {}

        for arg, val in kwargs.items():
            text = tk.StringVar(q_root)

            is_grid = "," in arg and arg.replace(",", "").isdigit()

            if is_grid:
                r, c = map(int, arg.split(","))
                if r not in grid_rows:
                    grid_rows[r] = tk.Frame(grid_frame)
                    grid_rows[r].pack()
                target_frame = grid_rows[r]
            else:
                target_frame = top_frame

            container = tk.Frame(target_frame)
            if is_grid:
                container.grid(row=0, column=c, padx=2, pady=2)
            else:
                container.pack(fill="x", anchor="w")

            if not is_grid:
                tk.Label(container, text=arg + ": ").pack(side="left")

            if val == "text" or val.startswith("open"):
                ent = tk.Entry(container, textvariable=text)
                ent.pack(side="left", expand=True, fill="x")

                if val.startswith("open"):
                    sp = val.split("_")

                    def make_open_file(t=text, s=sp):
                        path = fdl.askopenfilename(filetypes=[(s[1], "*." + s[2])], title=title)
                        if path: t.set(path)

                    tk.Button(container, text="...",
                              command=lambda: threading.Thread(target=make_open_file).start()).pack(side="left")

                qqlist.append([arg, text])

            elif val.startswith("choose"):
                options = val.split("/")[1:]
                text.set(options[0])
                width = 10 if is_grid else 20
                op = tk.OptionMenu(container, text, *options)
                op.config(width=width)
                op.pack(side="left")
                qqlist.append([arg, text])

        ans = {'_cancelled': True}

        def yes():
            for q_item in qqlist:
                val_str = q_item[1].get()
                if "," not in q_item[0] and val_str == "":
                    msgbox.showerror("错误", f"{q_item[0]} 不能为空")
                    return
                ans[q_item[0]] = val_str
            ans['_cancelled'] = False
            q_root.destroy()

        btn_frame = tk.Frame(q_root)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="确定", command=yes, width=10, bg="#e1e1e1").pack(side="left", padx=20)
        tk.Button(btn_frame, text="取消", command=q_root.destroy, width=10).pack(side="right", padx=20)

        q_root.mainloop()

        return None if ans.get('_cancelled') else {k: v for k, v in ans.items() if k != '_cancelled'}

    def change_en_us(param, b_name):
        with open(project.project_dir + "\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % project.mod_id, "r",
                  encoding="utf-8") as file:
            data = json.load(file)

        data[param] = b_name

        with open(project.project_dir + "\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % project.mod_id, "w",
                  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def create_block():
        ins = ""
        for key in project.blocks.keys():
            ins += "/" + key
        chinese_name, block_id, res_path, tabs = question("创建方块", {"中文名": "text", "方块id": "text",
                                                                       "材质文件": "open_16位材质文件_png",
                                                                       "物品栏": "choose/无/建筑方块" + ins}).values()
        res_path = str(res_path).replace("/", "\\")
        print(res_path)
        if block_id in project.blocks.keys():
            msgbox.showerror("创建方块", "方块id已经存在")
            return

        if tabs != "建筑方块" and tabs != "无" and tabs not in project.item_inventories:
            msgbox.showerror("创建方块", "没有物品栏")
            return

        lbl2.configure(text=f"正在创建方块")

        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\block\\ModBlocks.java",
                "r",
                encoding="utf-8") as f:
            ModBlocks = f.readlines()

        for i in range(len(ModBlocks)):
            if ModBlocks[
                i] == f"    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, {project.mod_id.capitalize()}.MOD_ID);\n":
                ModBlocks.insert(i + 1,
                                 f"\n    public static final RegistryObject<Block> {block_id.upper()} = registerBlock(\"{block_id.lower()}\",\n            () -> new Block(BlockBehaviour.Properties.copy(Blocks.STONE).sound(SoundType.STONE)));")
                break

        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\block\\ModBlocks.java",
                "w",
                encoding="utf-8") as f:
            f.writelines(ModBlocks)

        if tabs == "建筑方块":
            tabs = "BUILDING_BLOCKS"
            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java",
                    "r",
                    encoding="utf-8") as f:
                MainClass = f.readlines()

            for i in range(len(MainClass)):
                if MainClass[i] == "        // this_insert_wpl\n":
                    MainClass.insert(i + 1,
                                     "        if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModBlocks.%s);\n        }\n" % (
                                         tabs, block_id.upper()))
                    break

            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java",
                    "w",
                    encoding="utf-8") as f:
                f.writelines(MainClass)
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
                                               "\n        pOutput.accept(ModBlocks.%s.get());\n" % (
                                                   block_id.upper()))
                    break

            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModCreativeModeTabs.java",
                    "w",
                    encoding="utf-8") as f:
                f.writelines(ModCreativeModeTabs)

        change_en_us("block.%s.%s" % (project.mod_id, block_id), chinese_name)

        data = {
            "parent": "block/cube_all",
            "textures": {
                "all": "%s:block/%s" % (project.mod_id, block_id),
            }
        }

        with open(
                project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\models\\block\\{block_id}.json",
                "w",
                encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        add_file_to_tree(f"assets\\{project.mod_id}\\models\\block\\{block_id}.json", resource_root)

        blockstate_data = {
            "variants": {
                "": {
                    "model": "%s:block/%s" % (project.mod_id, block_id)
                }
            }
        }

        with open(
                project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\blockstates\\{block_id}.json",
                "w",
                encoding="utf-8") as f:
            json.dump(blockstate_data, f, ensure_ascii=False)
        add_file_to_tree(f"assets\\{project.mod_id}\\blockstates\\{block_id}.json", resource_root)

        item_model_data = {
            "parent": "%s:block/%s" % (project.mod_id, block_id)
        }

        with open(
                project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\models\\item\\{block_id}.json",
                "w",
                encoding="utf-8") as f:
            json.dump(item_model_data, f, ensure_ascii=False)
        add_file_to_tree(f"assets\\{project.mod_id}\\models\\item\\{block_id}.json", resource_root)

        assets_block_path = project.project_dir + f'\\src\\main\\resources\\assets\\{project.mod_id}\\textures\\block\\{block_id}.png'
        print(assets_block_path)

        os.system(F"copy {res_path} {assets_block_path}")

        add_file_to_tree("assets\\%s\\textures\\block\\%s.png" % (project.mod_id, block_id.lower()), resource_root)

        loot_dir = project.project_dir + f"\\src\\main\\resources\\data\\{project.mod_id}\\loot_tables\\blocks"
        os.makedirs(loot_dir, exist_ok=True)
        loot_data = {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [
                        {
                            "type": "minecraft:item",
                            "name": f"{project.mod_id}:{block_id}"
                        }
                    ],
                    "conditions": [
                        {
                            "condition": "minecraft:survives_explosion"
                        }
                    ]
                }
            ]
        }
        with open(loot_dir + f"\\{block_id}.json", "w", encoding="utf-8") as f:
            json.dump(loot_data, f, ensure_ascii=False, indent=2)
        add_file_to_tree(f"data\\{project.mod_id}\\loot_tables\\blocks\\{block_id}.json", resource_root)

        project.blocks[block_id] = chinese_name
        project.write_json()

        lbl2.configure(text=f"创建方块成功")
        time.sleep(1)
        text1.configure(state="normal")
        text1.delete(1.0, tk.END)
        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\block\\ModBlocks.java",
                "r", encoding="utf-8", errors="ignore") as ff:
            text1.insert(tk.END, ff.read())
            lbl2.configure(
                text="路径：" + project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\block\\ModBlocks.java")

    def create_item():
        ins = ""
        for key in project.item_inventories.keys():
            ins += "/" + key
        chinese_name, item_id, res_path, tabs = question("创建物品", {"中文名": "text", "物品id": "text",
                                                                      "材质文件": "open_16位材质文件_png",
                                                                      "物品栏": "choose/无/原料" + ins}).values()
        res_path = str(res_path).replace("/", "\\")
        print(res_path)
        if item_id in project.items.keys():
            msgbox.showerror("创建物品", "物品id已经存在")
            return

        if tabs != "原料" and tabs != "无" and tabs not in project.item_inventories:
            msgbox.showerror("创建物品", "没有物品栏")
            return

        lbl2.configure(text=f"正在创建物品")

        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java",
                "r",
                encoding="utf-8") as f:
            ModItems = f.readlines()

        for i in range(len(ModItems)):
            if ModItems[
                i] == f"            DeferredRegister.create(ForgeRegistries.ITEMS, {project.mod_id.capitalize()}.MOD_ID);\n":
                ModItems.insert(i + 1,
                                f"\n    public static final RegistryObject<Item> {item_id.upper()} = ITEMS.register(\"{item_id.lower()}\", () -> new Item(new Item.Properties()));")
                break

        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java",
                "w",
                encoding="utf-8") as f:
            f.writelines(ModItems)

        if tabs == "原料":
            tabs = "INGREDIENTS"
            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java",
                    "r",
                    encoding="utf-8") as f:
                ModItems = f.readlines()

            for i in range(len(ModItems)):
                if ModItems[i] == "        // this_insert_wpl\n":
                    ModItems.insert(i + 1,
                                    "        if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModItems.%s);\n        }\n" % (
                                        tabs, item_id.upper()))
                    break

            with open(
                    project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java",
                    "w",
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

        with open(
                project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\models\\item\\{item_id}.json",
                "w",
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
        with open(
                project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java",
                "r", encoding="utf-8", errors="ignore") as ff:
            text1.insert(tk.END, ff.read())
            lbl2.configure(
                text="路径：" + project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java")

    def create_recipes():
        all_ids = list(project.items.keys()) + list(project.blocks.keys())
        vanilla_items = [
            "minecraft:stick", "minecraft:cobblestone", "minecraft:oak_planks",
            "minecraft:iron_ingot", "minecraft:gold_ingot", "minecraft:diamond",
            "minecraft:coal", "minecraft:iron_ore", "minecraft:gold_ore",
            "minecraft:crafting_table", "minecraft:furnace"
        ]
        choose_list = "/" + "/".join(all_ids + vanilla_items)

        res = question("创建新配方", {
            "输出物品": "choose" + choose_list,
            "输出数量": "text",
            "配方类型": "choose/工作台_无位置要求/工作台_有位置要求/熔炉/高炉"
        })

        if not res:
            return

        target_id = res["输出物品"]
        count = res["输出数量"]
        r_type = res["配方类型"]

        try:
            count = int(count)
        except ValueError:
            msgbox.showerror("创建配方", "输出数量必须是整数")
            return

        if count <= 0:
            msgbox.showerror("创建配方", "输出数量必须大于0")
            return

        recipe_dir = project.project_dir + f"\\src\\main\\resources\\data\\{project.mod_id}\\recipes"
        os.makedirs(recipe_dir, exist_ok=True)

        recipe_data = None
        recipe_id = None

        if r_type == "工作台_有位置要求":
            grid_res = question("设置 3x3 布局 (空=无物品)", {
                "0,0": "choose/空" + choose_list,
                "0,1": "choose/空" + choose_list,
                "0,2": "choose/空" + choose_list,
                "1,0": "choose/空" + choose_list,
                "1,1": "choose/空" + choose_list,
                "1,2": "choose/空" + choose_list,
                "2,0": "choose/空" + choose_list,
                "2,1": "choose/空" + choose_list,
                "2,2": "choose/空" + choose_list,
            })

            if not grid_res:
                return

            letters = list("ABCDEFGHI")
            letter_idx = 0
            pattern = []
            key = {}

            for r in range(3):
                row = ""
                for c in range(3):
                    val = grid_res.get(f"{r},{c}", "空")
                    if val != "空":
                        row += letters[letter_idx]
                        key[letters[letter_idx]] = {"item": val}
                        letter_idx += 1
                    else:
                        row += " "
                pattern.append(row)

            if letter_idx == 0:
                msgbox.showerror("创建配方", "至少需要一个原料")
                return

            recipe_id = target_id
            recipe_data = {
                "type": "minecraft:crafting_shaped",
                "pattern": pattern,
                "key": key,
                "result": {
                    "item": target_id,
                    "count": count
                }
            }

        elif r_type == "工作台_无位置要求":
            ing_res = question("添加原料 (最多9个)", {
                "原料1": "choose/无" + choose_list,
                "原料2": "choose/无" + choose_list,
                "原料3": "choose/无" + choose_list,
            })

            if not ing_res:
                return

            ingredients = [{"item": v} for v in ing_res.values() if v != "无"]
            if not ingredients:
                msgbox.showerror("创建配方", "至少需要一个原料")
                return

            recipe_id = target_id
            recipe_data = {
                "type": "minecraft:crafting_shapeless",
                "ingredients": ingredients,
                "result": {
                    "item": target_id,
                    "count": count
                }
            }

        elif r_type in ["熔炉", "高炉"]:
            burn_res = question("烧炼设置", {
                "输入材料": "choose" + choose_list,
                "经验值": "text",
                "烧炼时间": "text"
            })

            if not burn_res:
                return

            input_item = burn_res["输入材料"]
            try:
                experience = float(burn_res["经验值"])
            except ValueError:
                msgbox.showerror("创建配方", "经验值必须是数字")
                return

            try:
                cook_time = int(burn_res["烧炼时间"])
            except ValueError:
                msgbox.showerror("创建配方", "烧炼时间必须是整数")
                return

            if cook_time <= 0:
                msgbox.showerror("创建配方", "烧炼时间必须大于0")
                return

            recipe_type = "minecraft:smelting" if r_type == "熔炉" else "minecraft:blasting"
            recipe_id = f"{target_id}_from_{input_item.split(':')[-1]}"
            recipe_data = {
                "type": recipe_type,
                "ingredient": {
                    "item": input_item
                },
                "result": target_id,
                "experience": experience,
                "cookingtime": cook_time
            }

        if recipe_data and recipe_id:
            lbl2.configure(text="正在创建配方")

            file_path = recipe_dir + f"\\{recipe_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(recipe_data, f, ensure_ascii=False, indent=2)

            add_file_to_tree(f"data\\{project.mod_id}\\recipes\\{recipe_id}.json", resource_root)

            project.recipes[recipe_id] = {
                "output": target_id,
                "type": r_type
            }
            project.write_json()

            lbl2.configure(text=f"配方 {recipe_id} 创建成功")
            time.sleep(1)
            lbl2.configure(text=f"配方文件: {file_path}")

    def delete_recipes():
        if not project.recipes:
            msgbox.showinfo("删除配方", "当前没有可删除的配方")
            return

        recipe_options = "/".join(project.recipes.keys())
        result = question("删除配方", {"选择要删除的配方": "choose/" + recipe_options})
        if not result:
            return

        recipe_id = result.get("选择要删除的配方")
        if not recipe_id:
            return

        if not msgbox.askokcancel("删除配方", f"确定要删除配方 '{recipe_id}' 吗？", parent=root):
            return

        lbl2.configure(text=f"正在删除配方 {recipe_id}")

        recipe_dir = project.project_dir + f"\\src\\main\\resources\\data\\{project.mod_id}\\recipes"
        file_path = recipe_dir + f"\\{recipe_id}.json"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(e)

        if recipe_id in project.recipes:
            del project.recipes[recipe_id]
            project.write_json()

        lbl2.configure(text=f"配方 {recipe_id} 删除成功")
        time.sleep(1)
        lbl2.configure(text="就绪")

    def delete_block():
        if not project.blocks:
            msgbox.showinfo("删除方块", "当前没有可删除的方块")
            return

        block_options = ""
        for block_id in project.blocks.keys():
            block_options += "/" + block_id

        result = question("删除方块", {"选择要删除的方块": "choose/" + block_options[1:]})
        block_id = result.get("选择要删除的方块")

        if not block_id:
            return

        if not msgbox.askokcancel("删除方块", f"确定要删除方块 '{block_id}' 吗？", parent=root):
            return

        lbl2.configure(text=f"正在删除方块 {block_id}")

        modblocks_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\block\\ModBlocks.java"
        if os.path.exists(modblocks_path):
            with open(modblocks_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            skip_next = False
            for line in lines:
                if f"public static final RegistryObject<Block> {block_id.upper()} =" in line:
                    skip_next = True
                    continue
                if skip_next and line.strip().startswith("() ->"):
                    continue
                if skip_next and line.strip() == "":
                    skip_next = False
                    continue
                if not skip_next:
                    new_lines.append(line)
                else:
                    skip_next = False

            with open(modblocks_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        mainclass_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java"
        if os.path.exists(mainclass_path):
            with open(mainclass_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if f"event.accept(ModBlocks.{block_id.upper()})" in line:
                    i += 3
                    continue
                new_lines.append(line)
                i += 1

            with open(mainclass_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        creative_tabs_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModCreativeModeTabs.java"
        if os.path.exists(creative_tabs_path):
            with open(creative_tabs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if f"pOutput.accept(ModBlocks.{block_id.upper()}" not in line:
                    new_lines.append(line)

            with open(creative_tabs_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        en_us_path = project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\lang\\en_us.json"
        if os.path.exists(en_us_path):
            with open(en_us_path, "r", encoding="utf-8") as f:
                try:
                    lang_data = json.load(f)
                except:
                    lang_data = {}

            lang_key = f"block.{project.mod_id}.{block_id}"
            if lang_key in lang_data:
                del lang_data[lang_key]

            with open(en_us_path, "w", encoding="utf-8") as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=2)

        files_to_delete = [
            f"models\\block\\{block_id}.json",
            f"blockstates\\{block_id}.json",
            f"models\\item\\{block_id}.json"
        ]

        for file_rel_path in files_to_delete:
            full_path = os.path.join(project.project_dir, "src", "main", "resources", "assets", project.mod_id,
                                     file_rel_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except:
                    pass

        texture_path = os.path.join(project.project_dir, "src", "main", "resources", "assets", project.mod_id,
                                    "textures", "block", f"{block_id}.png")
        if os.path.exists(texture_path):
            try:
                os.remove(texture_path)
            except:
                pass

        loot_path = os.path.join(project.project_dir, "src", "main", "resources", "data", project.mod_id,
                                 "loot_tables", "blocks", f"{block_id}.json")
        if os.path.exists(loot_path):
            try:
                os.remove(loot_path)
            except:
                pass

        if block_id in project.blocks:
            del project.blocks[block_id]
            project.write_json()

        lbl2.configure(text=f"方块 {block_id} 删除成功")
        time.sleep(1)

        text1.configure(state="normal")
        text1.delete(1.0, tk.END)
        if os.path.exists(modblocks_path):
            with open(modblocks_path, "r", encoding="utf-8", errors="ignore") as ff:
                text1.insert(tk.END, ff.read())
                lbl2.configure(text="路径：" + modblocks_path)

    def delete_item():
        if not project.items:
            msgbox.showinfo("删除物品", "当前没有可删除的物品")
            return

        item_options = ""
        for item_id in project.items.keys():
            item_options += "/" + item_id

        result = question("删除物品", {"选择要删除的物品": "choose/" + item_options[1:]})
        item_id = result.get("选择要删除的物品")

        if not item_id:
            return

        if not msgbox.askokcancel("删除物品", f"确定要删除物品 '{item_id}' 吗？", parent=root):
            return

        lbl2.configure(text=f"正在删除物品 {item_id}")

        moditems_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModItems.java"
        if os.path.exists(moditems_path):
            with open(moditems_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if f"public static final RegistryObject<Item> {item_id.upper()} =" not in line:
                    new_lines.append(line)

            with open(moditems_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        mainclass_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\{project.mod_id.capitalize()}.java"
        if os.path.exists(mainclass_path):
            with open(mainclass_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if f"event.accept(ModItems.{item_id.upper()})" in line:
                    i += 3
                    continue
                new_lines.append(line)
                i += 1

            with open(mainclass_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        creative_tabs_path = project.project_dir + f"\\src\\main\\java\\com\\{project.author}\\{project.mod_id}\\item\\ModCreativeModeTabs.java"
        if os.path.exists(creative_tabs_path):
            with open(creative_tabs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if f"pOutput.accept(ModItems.{item_id.upper()}" not in line:
                    new_lines.append(line)

            with open(creative_tabs_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        en_us_path = project.project_dir + f"\\src\\main\\resources\\assets\\{project.mod_id}\\lang\\en_us.json"
        if os.path.exists(en_us_path):
            with open(en_us_path, "r", encoding="utf-8") as f:
                try:
                    lang_data = json.load(f)
                except:
                    lang_data = {}

            lang_key = f"item.{project.mod_id}.{item_id}"
            if lang_key in lang_data:
                del lang_data[lang_key]

            with open(en_us_path, "w", encoding="utf-8") as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=2)

        model_path = os.path.join(project.project_dir, "src", "main", "resources", "assets", project.mod_id, "models",
                                  "item", f"{item_id}.json")
        if os.path.exists(model_path):
            try:
                os.remove(model_path)
            except:
                pass

        texture_path = os.path.join(project.project_dir, "src", "main", "resources", "assets", project.mod_id,
                                    "textures", "item", f"{item_id}.png")
        if os.path.exists(texture_path):
            try:
                os.remove(texture_path)
            except:
                pass

        if item_id in project.items:
            del project.items[item_id]
            project.write_json()

        lbl2.configure(text=f"物品 {item_id} 删除成功")
        time.sleep(1)

        text1.configure(state="normal")
        text1.delete(1.0, tk.END)
        if os.path.exists(moditems_path):
            with open(moditems_path, "r", encoding="utf-8", errors="ignore") as ff:
                text1.insert(tk.END, ff.read())
                lbl2.configure(text="路径：" + moditems_path)

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
                build_mod(i + 1, text)
            else:
                lbl2.configure(text="构建失败")
                time.sleep(1)
                lbl2.configure(text=text)

    def gen_jar(i, text):
        lbl2.configure(text=f"正在生成jar（第{i}次尝试）")
        y = project.build_jar()
        if y:
            lbl2.configure(text="生成成功，请选择保存位置")
            filename = fdl.asksaveasfilename(parent=root, filetypes=[("模组", "*.jar")], title="选择模组保存位置",
                                             initialdir=project.project_dir, initialfile=project.mod_id + ".jar")
            if filename:
                if str(filename)[-4:] != ".jar":
                    filename += ".jar"
                shutil.move(
                    project.project_dir + "\\build\\libs\\" + project.mod_id + "-1.0.0-Minecraft1.20.1-Forge47.2.0.jar",
                    filename)
            time.sleep(1)
            lbl2.configure(text=text)
        else:
            if i != 15:
                gen_jar(i + 1, text)

    def get_path(item, is_path=1):
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
            print(file_path, e)

    with open(str(os.path.join(project.project_dir, "config.json")), "r") as f:
        docs = json.loads(f.read())
    print(docs["name"], docs["mod_id"], docs["author"], docs["description"])
    root = tk.Tk()
    root.title("项目：" + docs["name"])
    root.geometry("1350x700")
    project_java_path = str(
        os.path.join(project.project_dir, "src", "main", "java", "com", docs["author"], docs["mod_id"]))
    project_resources_path = str(os.path.join(project.project_dir, "src", "main", "resources"))

    new_menu = tk.Menu(root, tearoff=False)
    new_menu.add_command(label="添加物品",
                         command=lambda: threading.Thread(target=create_item, daemon=True).start())
    new_menu.add_command(label="添加方块",
                         command=lambda: threading.Thread(target=create_block, daemon=True).start())
    new_menu.add_command(label="添加配方",
                         command=lambda: threading.Thread(target=create_recipes, daemon=True).start())

    delete_menu = tk.Menu(root, tearoff=False)
    delete_menu.add_command(label="删除物品",
                            command=lambda: threading.Thread(target=delete_item, daemon=True).start())
    delete_menu.add_command(label="删除方块",
                            command=lambda: threading.Thread(target=delete_block, daemon=True).start())
    delete_menu.add_command(label="删除配方",
                         command=lambda: threading.Thread(target=delete_recipes, daemon=True).start())

    build_menu = tk.Menu(root, tearoff=False)
    build_menu.add_command(label="重新构建",
                           command=lambda: threading.Thread(target=build_mod, args=(1, lbl2["text"]),
                                                            daemon=True).start())
    build_menu.add_command(label="生成jar模组",
                           command=lambda: threading.Thread(target=gen_jar, args=(1, lbl2["text"]),
                                                            daemon=True).start())

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
    treeview.menu.add_command(label="新建文件夹",
                              command=lambda: threading.Thread(target=root.after, args=(0, create_folder,),
                                                               daemon=True).start())
    treeview.menu.add_command(label="新建文件",
                              command=lambda: threading.Thread(target=root.after, args=(0, create_file(),),
                                                               daemon=True).start())
    treeview.menu.add_command(label="新建java类",
                              command=lambda: threading.Thread(target=root.after, args=(0, create_java(),),
                                                               daemon=True).start())
    treeview.menu.add_command(label="删除",
                              command=lambda: threading.Thread(target=root.after, args=(0, delete_file(),),
                                                               daemon=True).start())
    treeview.tree.bind("<Delete>",
                       lambda event: threading.Thread(target=root.after, args=(0, delete_file(),), daemon=True).start())

    center_frame = tk.Frame(root)
    lbl2 = tk.Label(center_frame, text="路径：")
    scrollbar_x = ttk.Scrollbar(center_frame, orient="horizontal")
    scrollbar_y = ttk.Scrollbar(center_frame)
    text1 = tk.Text(center_frame, xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set, wrap="none",
                    undo=True, maxundo=-1, state="disabled")
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

    sidebar = ai_sidebar.AISidebar(root, project.project_dir)
    sidebar.project_dir_attr = project.project_dir
    sidebar.mod_id_attr = project.mod_id
    sidebar.author_attr = project.author
    sidebar.java_path_attr = project_java_path
    sidebar.resources_path_attr = project_resources_path

    left_frame.pack(side="left", fill="y")
    lbl1.pack(side="top")
    treeview.pack()
    threading.Thread(target=add_project_file, daemon=True).start()

    sidebar.frame.pack(side="right", fill="y")
    center_frame.pack(side="left", fill="both", expand=True)

    lbl2.pack(side="top", fill="x")
    scrollbar_x.pack(side='bottom', fill='x')
    scrollbar_y.pack(side='right', fill='y')
    text1.pack(fill="both", expand=True)

    root.mainloop()
    print(4)


if __name__ == "__main__":
    edit(project_class.Project("thyids", "thyid", "thyi", "thy", blocks={"sdf": "dsf"}))
