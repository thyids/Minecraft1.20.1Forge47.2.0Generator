import os
import json
import shutil
import zipfile
import subprocess

class Project:
    def __init__(self, name, mod_id, author, description, project_dir=None, items=None, blocks=None, item_inventories=None):
        if items is None:
            self.items = {}
        else:
            self.items = items
        if blocks is None:
            self.blocks = {}
        else:
            self.blocks = blocks
        if item_inventories is None:
            self.item_inventories = {}
        else:
            self.item_inventories = item_inventories
        self.name = name
        self.e = ""
        self.project_name = "TI_" + mod_id
        self.gradle_user_home = os.path.join(os.path.expanduser('~'), '.gradle')
        self.mod_id = str(mod_id).replace(" ", "_").lower()
        self.author = author
        self.description = description
        if project_dir is None:
            self.project_dir = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), "project", self.project_name))
        else:
            self.project_dir = project_dir
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)
            with zipfile.ZipFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "project.zip"), "r") as zipf:
                zipf.extractall(self.project_dir)
            self.write_project_config()
            self.write_json()
        try:
            if not os.path.exists(self.gradle_user_home):
                os.makedirs(self.gradle_user_home)
                with zipfile.ZipFile(self.gradle_user_home, 'r') as zipf:
                    zipf.extractall(self.gradle_user_home)
        except Exception as e:
            self.e=e

    def write_text(self, path, text="", typ="text", value=None, key=None, x=None):
        self.e = ""
        if typ == "text":
            with open(path, "w") as f:
                f.write(text)
        elif typ == "json":
            with open(path, "r", encoding="utf-8") as f:
                doc = json.loads(f.read())
            doc[key] = value
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(doc))
        elif typ == "replace":
            with open(path, "r", encoding="utf-8") as f:
                doc = f.read()
            if x is None:
                doc = doc.replace(text, value)
            else:
                doc = doc.replace(text, value, x)
            with open(path, "w", encoding="utf-8") as f:
                f.write(doc)
        elif typ == "insert":
            with open(path, "r", encoding="utf-8") as f:
                doc = f.readlines()
            doc.insert(x, text)
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(doc)
        elif typ == "prop":
            lines = []
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            key_found = False
            new_lines = []
            for line in lines:
                if line.strip() == "" or line.strip().startswith("#"):
                    new_lines.append(line)
                    continue
                line_key, line_value = line.strip().split("=", 1)
                if line_key == key:
                    new_lines.append(f"{key}={value}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            if not key_found:
                new_lines.append(f"{key}={value}\n")
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(value if value else "")

    def yes_or_no(self, text):
        self.e = ""
        if "BUILD SUCCESSFUL" in text:
            return "Yes"
        else:
            return "No"

    def gen_intellij_run(self):
        result = subprocess.run(
            "gradlew genIntellijRuns",
            shell=True,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        # 合并stdout和stderr，确保不遗漏任何关键信息
        output = result.stdout + result.stderr
        self.e = output
        return self.yes_or_no(output)

    def build_jar(self):
        result = subprocess.run(
            "gradlew build",
            shell=True,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        # 合并stdout和stderr，确保不遗漏任何关键信息
        output = result.stdout + result.stderr
        print(output)
        return self.yes_or_no(output)

    def write_project_config(self):
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\Test.java", typ="replace", text="author", value=self.author)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\Test.java", typ="replace", text="gs_mod_id", value=self.mod_id.capitalize())
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\Test.java", typ="replace", text="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModItems.java", typ="replace", text="author", value=self.author)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModItems.java", typ="replace", text="gs_mod_id", value=self.mod_id.capitalize())
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModItems.java", typ="replace", text="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\block\\ModBlocks.java", typ="replace", text="author", value=self.author)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\block\\ModBlocks.java", typ="replace", text="gs_mod_id", value=self.mod_id.capitalize())
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\block\\ModBlocks.java", typ="replace", text="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModCreativeModeTabs.java", typ="replace", text="author", value=self.author)
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModCreativeModeTabs.java", typ="replace", text="gs_mod_id", value=self.mod_id.capitalize())
        self.write_text(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\item\\ModCreativeModeTabs.java", typ="replace", text="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\gradle.properties", typ="prop", key="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\gradle.properties", typ="prop", key="mod_id", value=self.mod_id)
        self.write_text(self.project_dir + "\\gradle.properties", typ="prop", key="mod_authors", value=self.author)
        self.write_text(self.project_dir + "\\gradle.properties", typ="prop", key="mod_description", value=self.description)
        self.write_text(self.project_dir + "\\gradle.properties", typ="prop", key="mod_group_id", value="com." + self.author + "." + self.mod_id)
        self.write_text(self.project_dir + "\\src\\main\\resources\\META-INF\\mods.toml", typ="replace", text="mod_idd", value=self.mod_id)
        self.write_text(self.project_dir + "\\src\\main\\resources\\META-INF\\mods.toml", typ="replace", text="GameName", value=self.name)
        self.write_text(self.project_dir + "\\src\\main\\resources\\META-INF\\mods.toml", typ="replace", text="author_is", value=self.author)
        self.write_text(self.project_dir + "\\src\\main\\resources\\META-INF\\mods.toml", typ="replace", text="Desk", value=self.description)
        # 重命名
        os.rename(self.project_dir + "\\src\\main\\java\\com\\thyids\\test\\Test.java", self.project_dir + f"\\src\\main\\java\\com\\thyids\\test\\{self.mod_id.capitalize()}.java")
        os.rename(self.project_dir + "\\src\\main\\java\\com\\thyids\\test", self.project_dir + "\\src\\main\\java\\com\\thyids\\" + self.mod_id)
        os.rename(self.project_dir + "\\src\\main\\java\\com\\thyids", self.project_dir + "\\src\\main\\java\\com\\" + self.author)
        os.rename(self.project_dir + "\\src\\main\\resources\\assets\\test", self.project_dir + "\\src\\main\\resources\\assets\\" + self.mod_id)
        os.rename(self.project_dir + "\\src\\main\\resources\\data\\test", self.project_dir + "\\src\\main\\resources\\data\\" + self.mod_id)

    def write_json(self):
        config_path = os.path.join(self.project_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("{}")
        self.write_text(path=config_path, typ="json", key="name", value=self.name)
        self.write_text(path=config_path, typ="json", key="author", value=self.author)
        self.write_text(path=config_path, typ="json", key="mod_id", value=self.mod_id)
        self.write_text(path=config_path, typ="json", key="description", value=self.description)
        self.write_text(path=config_path, typ="json", key="items", value=self.items)
        self.write_text(path=config_path, typ="json", key="blocks", value=self.blocks)
        self.write_text(path=config_path, typ="json", key="item_inventories", value=self.item_inventories)


    def insert_item(self, name, item_id, assets_path, tabs="INGREDIENTS"):
        if tabs == "INGREDIENTS":
            self.write_text(r"Ro.java", "// this_insert_wpl", "replace",
                       "if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModItems.%s);\n        }\n        // this_insert_wpl" % (
                           tabs, item_id.upper()))
        elif tabs in self.item_inventories:
            pass
        elif tabs != "NULL":
            return False
        shutil.copy(assets_path, os.path.join(self.project_dir, ""))
        text = f"    public static final RegistryObject<Item> {item_id.upper()} = ITEMS.register(\"{item_id.lower()}\", () -> new Item(new Item.Properties()));\n"
        self.write_text(r"ModItems.java", text, "insert", x=17)
        return True