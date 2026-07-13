import os
import json
import re
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.messagebox as msgbox
import requests


class AISidebar:
    def __init__(self, parent, project_dir):
        self.parent = parent
        self.project_dir = project_dir
        self.project_dir_attr = None
        self.mod_id_attr = None
        self.author_attr = None
        self.java_path_attr = None
        self.resources_path_attr = None

        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thyids_minecraft")
        os.makedirs(self.data_dir, exist_ok=True)

        self.config_path = os.path.join(self.data_dir, "api_config.json")
        self.history_path = os.path.join(self.data_dir, "chat_history.json")

        self.config = self._load_config()
        self.history = self._load_history()

        self.frame = tk.Frame(parent, width=350)
        self.frame.pack_propagate(False)

        self._build_settings_bar()
        self._build_chat_area()
        self._build_input_area()
        self._load_history_to_display()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 4096
        }

    def _save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def _build_settings_bar(self):
        settings_frame = tk.Frame(self.frame)
        settings_frame.pack(fill="x", padx=5, pady=(5, 0))

        self.collapse_var = tk.BooleanVar(value=True)
        self.toggle_btn = tk.Button(
            settings_frame, text="AI 设置 ▼", anchor="w",
            command=self._toggle_settings, relief="flat",
            bg="#e8e8e8", activebackground="#d0d0d0"
        )
        self.toggle_btn.pack(fill="x")

        self.settings_inner = tk.Frame(self.frame)
        self.settings_inner.pack(fill="x", padx=5)

        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        self.base_url_var = tk.StringVar(value=self.config.get("base_url", "https://api.openai.com/v1"))
        self.model_var = tk.StringVar(value=self.config.get("model", "gpt-3.5-turbo"))

        row1 = tk.Frame(self.settings_inner)
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="API Key:", width=8, anchor="w").pack(side="left")
        self.api_key_entry = tk.Entry(row1, textvariable=self.api_key_var, show="*", width=28)
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(self.settings_inner)
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="Base URL:", width=8, anchor="w").pack(side="left")
        tk.Entry(row2, textvariable=self.base_url_var, width=28).pack(side="left", fill="x", expand=True)

        row3 = tk.Frame(self.settings_inner)
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="Model:", width=8, anchor="w").pack(side="left")
        tk.Entry(row3, textvariable=self.model_var, width=28).pack(side="left", fill="x", expand=True)

        btn_frame = tk.Frame(self.settings_inner)
        btn_frame.pack(fill="x", pady=(4, 2))
        tk.Button(btn_frame, text="保存设置", command=self._on_save_settings,
                  bg="#4CAF50", fg="white", width=12).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="清空聊天记录", command=self._on_clear_history,
                  width=12).pack(side="left")

        self.settings_inner.pack_forget()

    def _toggle_settings(self):
        if self.collapse_var.get():
            self.settings_inner.pack(fill="x", padx=5)
            self.toggle_btn.config(text="AI 设置 ▲")
            self.collapse_var.set(False)
        else:
            self.settings_inner.pack_forget()
            self.toggle_btn.config(text="AI 设置 ▼")
            self.collapse_var.set(True)

    def _on_save_settings(self):
        self.config["api_key"] = self.api_key_var.get().strip()
        self.config["base_url"] = self.base_url_var.get().strip().rstrip("/")
        self.config["model"] = self.model_var.get().strip()
        self._save_config()
        msgbox.showinfo("设置", "API 设置已保存", parent=self.parent)

    def _on_clear_history(self):
        if msgbox.askyesno("确认", "确定要清空所有聊天记录吗？", parent=self.parent):
            self.history = []
            self._save_history()
            self.chat_display.config(state="normal")
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state="disabled")

    def _build_chat_area(self):
        self.chat_display = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, state="disabled",
            font=("Consolas", 10), height=20,
            bg="#fafafa", relief="flat"
        )
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)

        self.chat_display.tag_config("user_name", foreground="#1a73e8",
                                     font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_config("user_msg", foreground="#333333",
                                     font=("Microsoft YaHei", 10))
        self.chat_display.tag_config("ai_name", foreground="#d93025",
                                     font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_config("ai_msg", foreground="#333333",
                                     font=("Microsoft YaHei", 10))
        self.chat_display.tag_config("system", foreground="#888888",
                                     font=("Microsoft YaHei", 9, "italic"))
        self.chat_display.tag_config("file_op", foreground="#137333",
                                     font=("Consolas", 9))
        self.chat_display.tag_config("error", foreground="#d93025",
                                     font=("Microsoft YaHei", 10))
        self.chat_display.tag_config("code", background="#f0f0f0",
                                     font=("Consolas", 9))

    def _build_input_area(self):
        input_frame = tk.Frame(self.frame)
        input_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.input_text = tk.Text(
            input_frame, height=3, wrap=tk.WORD,
            font=("Microsoft YaHei", 10)
        )
        self.input_text.pack(side="left", fill="both", expand=True)
        self.input_text.bind("<Return>", self._on_return_key)

        send_btn = tk.Button(
            input_frame, text="发送", command=self._on_send,
            bg="#4CAF50", fg="white", width=6, height=2
        )
        send_btn.pack(side="right", padx=(5, 0))

    def _on_return_key(self, event):
        if event.state & 0x1:
            return None
        self._on_send()
        return "break"

    def _on_send(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        self.input_text.delete("1.0", tk.END)

        self._append_message("user", user_input)
        self._set_send_enabled(False)

        threading.Thread(target=self._send_to_ai, args=(user_input,), daemon=True).start()

    def _set_send_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and child.cget("text") == "发送":
                        child.config(state=state)

    def _append_message(self, role, content):
        def _do():
            self.chat_display.config(state="normal")
            if role == "user":
                self.chat_display.insert(tk.END, "你: ", "user_name")
                self.chat_display.insert(tk.END, content + "\n\n", "user_msg")
            elif role == "ai":
                self.chat_display.insert(tk.END, "AI: ", "ai_name")
                self.chat_display.insert(tk.END, content + "\n\n", "ai_msg")
            elif role == "system":
                self.chat_display.insert(tk.END, content + "\n", "system")
            elif role == "file_op":
                self.chat_display.insert(tk.END, content + "\n", "file_op")
            elif role == "error":
                self.chat_display.insert(tk.END, content + "\n\n", "error")
            self.chat_display.config(state="disabled")
            self.chat_display.see(tk.END)
        self.parent.after(0, _do)

    def _build_system_prompt(self):
        project_root = self.project_dir_attr or self.project_dir
        mod_id = self.mod_id_attr or "unknown"
        author = self.author_attr or "unknown"

        parts = [
            "You are an AI assistant for a Minecraft 1.20.1 Forge mod development project.",
            f"Project root: {project_root}",
            f"Mod ID: {mod_id}",
            f"Author: {author}",
            "",
            "When you need to modify/create files, use this format EXACTLY:",
            "",
            "[CREATE_FILE] <relative_path>",
            "```<file_content>```",
            "",
            "[WRITE_FILE] <relative_path>",
            "```<file_content>```",
            "",
            "[EDIT_FILE] <relative_path>",
            "<<<SEARCH>>>",
            "<exact_text_to_find>",
            "<<<REPLACE>>>",
            "<replacement_text>",
            "<<<END>>>",
            "",
            "Rules:",
            "- Relative paths are relative to project root.",
            "- [CREATE_FILE] creates a new file. [WRITE_FILE] overwrites an existing file.",
            "- [EDIT_FILE] does search-and-replace on an existing file.",
            "- You can include multiple file operations in one response.",
            "- Always explain what you did after file operations.",
            "- For Minecraft Forge 1.20.1, use Java 17, DeferredRegister for registration.",
            "- Recipes go in: src/main/resources/data/<mod_id>/recipes/",
            "- Models go in: src/main/resources/assets/<mod_id>/models/",
            "- Blockstates go in: src/main/resources/assets/<mod_id>/blockstates/",
            "- Textures go in: src/main/resources/assets/<mod_id>/textures/",
            "- Language files: src/main/resources/assets/<mod_id>/lang/en_us.json",
            "- Main class: src/main/java/com/<author>/<mod_id>/<ModId>.java",
            "- Items: src/main/java/com/<author>/<mod_id>/item/ModItems.java",
            "- Blocks: src/main/java/com/<author>/<mod_id>/block/ModBlocks.java",
            "- Creative tabs: src/main/java/com/<author>/<mod_id>/item/ModCreativeModeTabs.java",
        ]

        try:
            tree_str = self._get_project_tree(project_root)
            if tree_str:
                parts.append("")
                parts.append("Current project structure:")
                parts.append(tree_str)
        except Exception:
            pass

        return "\n".join(parts)

    def _get_project_tree(self, root_path, max_depth=5):
        lines = []
        skip_dirs = {".git", "build", ".gradle", "__pycache__", ".idea", "run", "out"}

        def walk(path, prefix="", depth=0):
            if depth >= max_depth:
                return
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                return
            dirs = [e for e in entries if os.path.isdir(os.path.join(path, e)) and e not in skip_dirs]
            files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
            for f in files:
                lines.append(f"{prefix}{f}")
            for i, d in enumerate(dirs):
                is_last = (i == len(dirs) - 1) and not files
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{d}/")
                extension = "    " if is_last else "│   "
                walk(os.path.join(path, d), prefix + extension, depth + 1)

        walk(root_path)
        return "\n".join(lines[:100])

    def _send_to_ai(self, user_message):
        if not self.config.get("api_key"):
            self._append_message("error", "请先在设置中配置 API Key")
            self._set_send_enabled(True)
            return

        self.history.append({"role": "user", "content": user_message})

        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.history[-50:])

        try:
            url = self.config["base_url"] + "/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['api_key']}"
            }
            payload = {
                "model": self.config["model"],
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 4096)
            }

            self._append_message("system", "正在请求 AI 响应...")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)

            if resp.status_code != 200:
                error_detail = ""
                try:
                    err = resp.json()
                    error_detail = err.get("error", {}).get("message", resp.text)
                except Exception:
                    error_detail = resp.text
                self._append_message("error", f"API 错误 ({resp.status_code}): {error_detail}")
                self.history.pop()
                self._set_send_enabled(True)
                return

            data = resp.json()
            ai_content = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": ai_content})
            self._save_history()

            operations = self._parse_operations(ai_content)
            display_text = ai_content

            if operations:
                accepted = self._confirm_operations(operations)
                if accepted:
                    results = self._apply_operations(accepted)
                    display_text += "\n\n---\n" + "\n".join(results)
                else:
                    display_text += "\n\n---\n所有文件修改已跳过"
                    self.history.pop()

            self._append_message("ai", display_text)

        except requests.exceptions.Timeout:
            self._append_message("error", "请求超时，请检查网络连接或增加超时时间")
            self.history.pop()
        except requests.exceptions.ConnectionError:
            self._append_message("error", "连接失败，请检查 Base URL 是否正确")
            self.history.pop()
        except Exception as e:
            self._append_message("error", f"请求失败: {str(e)}")
            self.history.pop()

        self._set_send_enabled(True)

    def _parse_operations(self, text):
        operations = []

        create_pattern = re.compile(
            r'\[CREATE_FILE\]\s*(\S+?)\s*\n```(?:\w*\n)?(.*?)```',
            re.DOTALL
        )
        write_pattern = re.compile(
            r'\[WRITE_FILE\]\s*(\S+?)\s*\n```(?:\w*\n)?(.*?)```',
            re.DOTALL
        )
        edit_pattern = re.compile(
            r'\[EDIT_FILE\]\s*(\S+?)\s*\n<<<SEARCH>>>\n(.*?)<<<REPLACE>>>\n(.*?)<<<END>>>',
            re.DOTALL
        )

        for match in create_pattern.finditer(text):
            operations.append({
                "type": "create",
                "path": match.group(1).strip(),
                "content": match.group(2)
            })

        for match in write_pattern.finditer(text):
            operations.append({
                "type": "write",
                "path": match.group(1).strip(),
                "content": match.group(2)
            })

        for match in edit_pattern.finditer(text):
            operations.append({
                "type": "edit",
                "path": match.group(1).strip(),
                "search": match.group(2),
                "replace": match.group(3)
            })

        return operations

    def _confirm_operations(self, operations):
        project_root = self.project_dir_attr or self.project_dir
        result = {"accepted": None}
        event = threading.Event()

        def _dialog():
            dlg = tk.Toplevel(self.parent)
            dlg.title("确认文件修改")
            dlg.geometry("600x450")
            dlg.transient(self.parent)
            dlg.grab_set()

            tk.Label(dlg, text="AI 请求修改以下文件，请确认是否执行：",
                     font=("Microsoft YaHei", 10, "bold"), anchor="w"
                     ).pack(fill="x", padx=10, pady=(10, 5))

            list_frame = tk.Frame(dlg)
            list_frame.pack(fill="both", expand=True, padx=10, pady=5)

            canvas = tk.Canvas(list_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas)

            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind("<MouseWheel>", _on_mousewheel)

            vars_list = []
            for i, op in enumerate(operations):
                var = tk.BooleanVar(value=True)
                vars_list.append(var)

                row = tk.Frame(inner)
                row.pack(fill="x", pady=2)

                cb = tk.Checkbutton(row, variable=var)
                cb.pack(side="left")

                if op["type"] == "create":
                    label = f"[新建] {op['path']}"
                elif op["type"] == "write":
                    label = f"[覆写] {op['path']}"
                else:
                    label = f"[编辑] {op['path']}"

                tk.Label(row, text=label, anchor="w",
                         font=("Consolas", 9)).pack(side="left", fill="x", expand=True)

            btn_frame = tk.Frame(dlg)
            btn_frame.pack(fill="x", padx=10, pady=10)

            def _accept():
                result["accepted"] = [var.get() for var in vars_list]
                event.set()
                dlg.destroy()

            def _skip_all():
                result["accepted"] = [False] * len(operations)
                event.set()
                dlg.destroy()

            def _cancel():
                result["accepted"] = None
                event.set()
                dlg.destroy()

            tk.Button(btn_frame, text="全部接受", command=_accept,
                      bg="#4CAF50", fg="white", width=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="全部跳过", command=_skip_all,
                      width=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="取消(AI回复撤回)", command=_cancel,
                      width=16).pack(side="right", padx=5)

            dlg.protocol("WM_DELETE_WINDOW", _cancel)
            dlg.mainloop()

        self.parent.after(0, _dialog)
        event.wait()

        if result["accepted"] is None:
            return None

        accepted = []
        for i, op in enumerate(operations):
            if result["accepted"][i]:
                accepted.append(op)
        return accepted

    def _apply_operations(self, operations):
        results = []
        project_root = self.project_dir_attr or self.project_dir

        for op in operations:
            rel_path = op["path"]
            full_path = os.path.join(project_root, rel_path)
            op_type = op["type"]

            try:
                if op_type == "create" or op_type == "write":
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(op["content"])
                    label = "创建" if op_type == "create" else "覆写"
                    results.append(f"[{label}] {rel_path}")
                    self._append_message("file_op", f"  [{label}文件] {rel_path}")

                elif op_type == "edit":
                    if not os.path.exists(full_path):
                        results.append(f"[失败] {rel_path}: 文件不存在")
                        self._append_message("error", f"  [编辑失败] {rel_path}: 文件不存在")
                        continue
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if op["search"] not in content:
                        results.append(f"[失败] {rel_path}: 未找到要替换的文本")
                        self._append_message("error", f"  [编辑失败] {rel_path}: 未找到要替换的文本")
                        continue
                    new_content = content.replace(op["search"], op["replace"], 1)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    results.append(f"[编辑] {rel_path}")
                    self._append_message("file_op", f"  [编辑文件] {rel_path}")

            except Exception as e:
                results.append(f"[失败] {rel_path}: {e}")
                self._append_message("error", f"  [操作失败] {rel_path}: {e}")

        return results

    def _load_history_to_display(self):
        if not self.history:
            self._append_message("system",
                "欢迎使用 AI 助手！\n"
                "请先在设置中配置 API Key，\n"
                "然后即可通过对话让 AI 帮你修改项目文件。\n\n"
                "AI 可以自动创建、写入和编辑项目中的文件。\n"
                "直接描述你的需求即可。"
            )
            return
        for msg in self.history:
            if msg["role"] == "user":
                self._append_message("user", msg["content"])
            elif msg["role"] == "assistant":
                self._append_message("ai", msg["content"])

    def clear_conversation(self):
        self.history = []
        self._save_history()
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state="disabled")
        self._append_message("system", "对话已重置，请继续提问。")
