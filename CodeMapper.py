import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import json

# 定义配置文件路径
CONFIG_FILE = "config.json"

# 定义默认的跳过模式
DEFAULT_SKIP_PATTERNS = [".git", "node_modules", "__pycache__", ".idea", ".vscode", "venv"]

# 定义文件类型对应的注释符号
COMMENT_SYMBOLS = {
    ".py": "#",
    ".js": "//",
    ".java": "//",
    ".c": "//",
    ".cpp": "//",
    ".html": "<!--",
    ".htm": "<!--",
    ".css": "/*",
    ".scss": "/*",
    ".php": "//",
    ".rb": "#",
    ".sh": "#",
    ".go": "//",
    ".rs": "//",
    ".swift": "//",
    ".kt": "//",
    ".ts": "//",
    ".tsx": "//",
    ".vue": "<!--",
    ".xml": "<!--",
    ".yaml": "#",
    ".yml": "#",
    ".md": "<!--",
    ".txt": "#",
}

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"skip_patterns": DEFAULT_SKIP_PATTERNS}

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def generate_tree_structure(root_dir, output_file, skip_invalid_files, skip_license):
    """生成目录树结构和文件内容"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入项目名称
        project_name = os.path.basename(root_dir)
        f.write(f"1. 项目名称: {project_name}\n")

        # 生成目录树结构
        f.write(f"{project_name}/\n")
        _generate_tree(root_dir, f, prefix="", skip_invalid_files=skip_invalid_files, skip_license=skip_license)

        # 写入文件内容
        f.write("\n")
        _write_file_contents(root_dir, f, skip_invalid_files=skip_invalid_files, skip_license=skip_license)

def _generate_tree(path, file, prefix="", skip_invalid_files=False, skip_license=False):
    """递归生成目录树结构"""
    if os.path.isdir(path):
        items = os.listdir(path)
        for i, item in enumerate(sorted(items)):
            full_path = os.path.join(path, item)
            is_last = (i == len(items) - 1)

            # 如果需要跳过无效文件，则检查当前项是否需要跳过
            if skip_invalid_files and any(skip_pattern in item for skip_pattern in skip_patterns_var.get()):
                continue
            # 如果需要跳过 LICENSE 文件，则检查当前项是否为 LICENSE
            if skip_license and item == "LICENSE":
                continue

            if os.path.isdir(full_path):
                # 替换反斜杠为正斜杠
                display_path = full_path.replace("\\", "/")
                file.write(f"{prefix}├── {item}/\n")
                _generate_tree(full_path, file, prefix + ("│   " if not is_last else "    "), skip_invalid_files, skip_license)
            else:
                # 替换反斜杠为正斜杠
                display_path = full_path.replace("\\", "/")
                file.write(f"{prefix}├── {item}\n")

def _write_file_contents(root_dir, file, skip_invalid_files=False, skip_license=False):
    """写入文件内容"""
    file_count = 1  # 序号计数器
    for root, _, files in os.walk(root_dir):
        # 如果需要跳过无效文件，则检查当前文件夹是否需要跳过
        if skip_invalid_files and any(skip_pattern in root for skip_pattern in skip_patterns_var.get()):
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 如果需要跳过无效文件，则检查当前文件是否需要跳过
            if skip_invalid_files and any(skip_pattern in file_name for skip_pattern in skip_patterns_var.get()):
                continue
            # 如果需要跳过 LICENSE 文件，则检查当前文件是否为 LICENSE
            if skip_license and file_name == "LICENSE":
                continue

            # 替换反斜杠为正斜杠
            relative_path = os.path.relpath(file_path, root_dir).replace("\\", "/")
            # 获取文件扩展名
            _, file_extension = os.path.splitext(file_name)
            # 根据文件扩展名选择注释符号，默认使用 "#"
            comment_symbol = COMMENT_SYMBOLS.get(file_extension, "#")
            # 写入空行
            file.write("\n")
            # 写入文件路径（带注释符号和序号）
            file.write(f"{comment_symbol} {file_count}. {relative_path}\n")
            file_count += 1  # 序号递增
            try:
                with open(file_path, 'r', encoding='utf-8') as content_file:
                    file.write(content_file.read())
            except Exception as e:
                file.write(f"无法读取文件: {e}\n")

def select_project_folder():
    """选择工程文件夹"""
    folder = filedialog.askdirectory()
    if folder:
        project_folder_var.set(folder)
        # 自动设置默认输出路径
        set_default_output_path(folder)
        update_status("已选择工程文件夹: " + folder)

def set_default_output_path(project_folder):
    """设置默认输出路径"""
    project_name = os.path.basename(project_folder)
    # 直接使用项目名称作为文件名，覆盖同名文件
    default_output_file = os.path.join(os.path.dirname(project_folder), f"{project_name}.txt")
    # 替换反斜杠为正斜杠
    default_output_file = default_output_file.replace("\\", "/")
    output_file_var.set(default_output_file)

def select_output_file():
    """选择输出文件路径"""
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file:
        # 替换反斜杠为正斜杠
        file = file.replace("\\", "/")
        output_file_var.set(file)
        update_status("已选择输出文件: " + file)

def export_project_info():
    """导出项目信息"""
    project_folder = project_folder_var.get()
    output_file = output_file_var.get()

    if not project_folder:
        update_status("警告: 请选择工程文件夹！")
        return
    if not output_file:
        update_status("警告: 请选择输出文件路径！")
        return

    try:
        skip_invalid_files = skip_invalid_files_var.get()
        skip_license = skip_license_var.get()
        generate_tree_structure(project_folder, output_file, skip_invalid_files, skip_license)
        update_status(f"成功: 项目信息已导出到 {output_file}")
    except Exception as e:
        update_status(f"错误: 导出失败: {e}")

def on_drop(event):
    """处理拖放文件夹事件"""
    folder_path = event.data.strip('{}')  # 去除拖放路径中的多余字符
    if os.path.isdir(folder_path):
        project_folder_var.set(folder_path)
        set_default_output_path(folder_path)
        update_status("已拖放工程文件夹: " + folder_path)
    else:
        update_status("警告: 请拖放一个有效的文件夹！")

def update_status(message):
    """更新状态栏信息"""
    status_var.set(message)

def edit_skip_patterns():
    """编辑跳过模式"""
    # 创建一个新窗口
    edit_window = tk.Toplevel(root)
    edit_window.title("编辑跳过模式")

    # 创建一个文本框，显示当前的跳过模式
    text_box = tk.Text(edit_window, width=50, height=10)
    text_box.pack(padx=10, pady=10)
    text_box.insert(tk.END, "\n".join(skip_patterns_var.get()))

    # 保存按钮
    def save_skip_patterns():
        new_patterns = text_box.get("1.0", tk.END).strip().split("\n")
        skip_patterns_var.set(new_patterns)
        config = load_config()
        config["skip_patterns"] = new_patterns
        save_config(config)
        edit_window.destroy()
        update_status("跳过模式已更新")

    tk.Button(edit_window, text="保存", command=save_skip_patterns).pack(pady=10)

# 创建主窗口（支持拖放）
root = TkinterDnD.Tk()
root.title("CodeMapper 1.0.0 ———— QwejayHuang")  # 修改程序名称为 CodeMapper

# 加载配置文件
config = load_config()
skip_patterns_var = tk.Variable(value=config["skip_patterns"])

# 变量
project_folder_var = tk.StringVar()
output_file_var = tk.StringVar()
skip_invalid_files_var = tk.BooleanVar(value=True)  # 默认勾选“智能跳过无效文件”
skip_license_var = tk.BooleanVar(value=True)  # 默认勾选“忽略 LICENSE 文件”
status_var = tk.StringVar()  # 状态栏变量

# GUI 布局
tk.Label(root, text="工程文件夹:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
tk.Entry(root, textvariable=project_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="选择文件夹", command=select_project_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="输出文件:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="选择文件", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

# 添加“智能跳过无效文件”复选框
tk.Checkbutton(root, text="跳过忽略列表中的文件", variable=skip_invalid_files_var).grid(row=2, column=1, pady=5, sticky="w")

# 添加“忽略 LICENSE 文件”复选框
tk.Checkbutton(root, text="忽略 LICENSE 文件", variable=skip_license_var).grid(row=3, column=1, pady=5, sticky="w")

# 添加“编辑跳过模式”按钮
tk.Button(root, text="忽略文件列表", command=edit_skip_patterns).grid(row=4, column=0, pady=10)

tk.Button(root, text="导出项目信息", command=export_project_info).grid(row=4, column=1, pady=10)

# 添加状态栏
status_label = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.grid(row=5, column=0, columnspan=3, sticky="we")

# 支持拖放文件夹
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# 运行主循环
root.mainloop()