#!/usr/bin/env python3
"""
项目代码导出为Markdown脚本
将项目代码导出为Markdown文件，保留文件结构层次，方便导入Obsidian
"""

import os
import shutil
from pathlib import Path
import mimetypes
from typing import List

# 需要过滤的目录
EXCLUDE_DIRS = {
    'node_modules',
    '__pycache__',
    '.git',
    '.vscode',
    '.idea',
    'dist',
    'build',
    'logs',
    'htmlcov',
    '.pytest_cache',
    '.coverage',
    'reference-AIGraphX',  # 参考代码，通常不需要导出
    '.next',
    '.nuxt',
    'coverage',
    'tmp',
    'temp',
    '.cache',
    '.venv',
    'venv',
    'env',
    'corebank-venv'
}

# 需要过滤的文件扩展名
EXCLUDE_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.dylib',
    '.log',
    '.tmp',
    '.temp',
    '.cache',
    '.lock',
    '.pid',
    '.swp',
    '.swo',
    '.DS_Store',
    '.thumbs.db'
}

# 需要过滤的文件名模式
EXCLUDE_FILES = {
    '.env',
    '.env.local',
    '.env.development',
    '.env.production',
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    'poetry.lock',
    'Pipfile.lock',
    '.gitignore',
    '.dockerignore',
    '.eslintcache',
    'thumbs.db',
    'desktop.ini'
}

# 支持的文本文件扩展名
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.txt', '.rst', '.sql', '.sh', '.bash', '.zsh', '.fish',
    '.dockerfile', '.containerfile', '.gitignore', '.env', '.editorconfig',
    '.vue', '.svelte', '.php', '.rb', '.go', '.rs', '.java', '.c', '.cpp',
    '.h', '.hpp', '.cs', '.swift', '.kt', '.scala', '.clj', '.hs', '.elm',
    '.r', '.m', '.pl', '.lua', '.vim', '.tmux', '.zshrc', '.bashrc'
}

def should_exclude_dir(dir_name: str) -> bool:
    """判断是否应该排除目录"""
    return (
        dir_name.startswith('.') or 
        dir_name in EXCLUDE_DIRS
    )

def should_exclude_file(file_path: Path) -> bool:
    """判断是否应该排除文件"""
    file_name = file_path.name
    file_ext = file_path.suffix.lower()
    
    # 排除隐藏文件（除了一些重要的配置文件）
    if file_name.startswith('.') and file_name not in {'.gitignore', '.env', '.editorconfig'}:
        return True
    
    # 排除特定扩展名
    if file_ext in EXCLUDE_EXTENSIONS:
        return True
    
    # 排除特定文件名
    if file_name in EXCLUDE_FILES:
        return True
    
    return False

def is_text_file(file_path: Path) -> bool:
    """判断是否为文本文件"""
    file_ext = file_path.suffix.lower()
    
    # 首先检查已知的文本扩展名
    if file_ext in TEXT_EXTENSIONS:
        return True
    
    # 对于没有扩展名的文件，尝试用mimetypes判断
    if not file_ext:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
    
    # 尝试读取文件开头判断是否为文本
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if not chunk:
                return True  # 空文件视为文本文件
            
            # 检查是否包含null字节（二进制文件的特征）
            if b'\x00' in chunk:
                return False
            
            # 尝试解码为UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except (IOError, OSError):
        return False

def create_markdown_content(file_path: Path, relative_path: Path) -> str:
    """创建Markdown内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"# {relative_path}\n\n**无法读取文件内容（编码问题）**\n"
    except Exception as e:
        return f"# {relative_path}\n\n**读取文件时出错: {str(e)}**\n"

    file_ext = file_path.suffix.lower()

    # 对于Markdown文件，直接返回原内容，只添加文件路径注释
    if file_ext == '.md':
        if content.strip():
            return f"<!-- 文件路径: {relative_path} -->\n\n{content}"
        else:
            return f"<!-- 文件路径: {relative_path} -->\n\n**文件为空**\n"

    # 对于其他文件，包装成代码块
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.dockerfile': 'dockerfile',
        '.containerfile': 'dockerfile',
        '.vue': 'vue',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin'
    }

    language = language_map.get(file_ext, '')

    markdown_content = f"# {relative_path}\n\n"

    if content.strip():
        markdown_content += f"```{language}\n{content}\n```\n"
    else:
        markdown_content += "**文件为空**\n"

    return markdown_content

def create_index_file(output_path: Path, exported_files: List[Path]):
    """创建索引文件"""
    index_content = "# 项目文件索引\n\n"
    index_content += f"总共导出了 {len(exported_files)} 个文件\n\n"

    # 按目录组织文件
    dirs_dict = {}
    for file_path in exported_files:
        dir_path = file_path.parent
        if dir_path not in dirs_dict:
            dirs_dict[dir_path] = []
        dirs_dict[dir_path].append(file_path)

    # 排序目录
    sorted_dirs = sorted(dirs_dict.keys())

    for dir_path in sorted_dirs:
        if str(dir_path) != ".":
            index_content += f"## {dir_path}\n\n"
        else:
            index_content += f"## 根目录\n\n"

        # 排序文件
        sorted_files = sorted(dirs_dict[dir_path])
        for file_path in sorted_files:
            # 对于原本是.md的文件，直接使用文件名；对于其他文件，移除添加的.md扩展名
            if file_path.name.endswith('.md.md'):
                # 这是非Markdown文件添加了.md扩展名的情况
                original_name = file_path.name[:-3]  # 移除.md
                link_name = file_path.stem  # 用于链接的名称
            else:
                # 这是原本就是Markdown文件的情况
                original_name = file_path.name
                link_name = file_path.stem
            index_content += f"- [[{link_name}|{original_name}]]\n"

        index_content += "\n"

    # 写入索引文件
    index_file_path = output_path / "README.md"
    with open(index_file_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"创建索引文件: {index_file_path}")

def export_project_to_markdown(source_dir: str, output_dir: str):
    """将项目导出为Markdown文件"""
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # 创建输出目录
    if output_path.exists():
        print(f"输出目录已存在，将清空: {output_path}")
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # 统计信息
    total_files = 0
    exported_files = 0
    skipped_files = 0
    exported_file_paths = []

    print(f"开始导出项目: {source_path.absolute()}")
    print(f"输出目录: {output_path.absolute()}")
    print("-" * 50)

    # 遍历所有文件
    for root, dirs, files in os.walk(source_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        root_path = Path(root)
        relative_root = root_path.relative_to(source_path)

        for file_name in files:
            file_path = root_path / file_name
            relative_file_path = relative_root / file_name

            total_files += 1

            # 检查是否应该排除文件
            if should_exclude_file(file_path):
                skipped_files += 1
                continue

            # 检查是否为文本文件
            if not is_text_file(file_path):
                skipped_files += 1
                print(f"跳过二进制文件: {relative_file_path}")
                continue

            # 创建输出文件路径
            # 对于Markdown文件，保持原文件名；对于其他文件，添加.md扩展名
            if file_path.suffix.lower() == '.md':
                output_file_path = output_path / relative_file_path
            else:
                output_file_path = output_path / f"{relative_file_path}.md"
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建Markdown内容
            markdown_content = create_markdown_content(file_path, relative_file_path)

            # 写入文件
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                exported_files += 1
                exported_file_paths.append(output_file_path.relative_to(output_path))
                print(f"导出: {relative_file_path}")
            except Exception as e:
                print(f"导出失败 {relative_file_path}: {str(e)}")
                skipped_files += 1

    # 创建索引文件
    create_index_file(output_path, exported_file_paths)

    print("-" * 50)
    print(f"导出完成!")
    print(f"总文件数: {total_files}")
    print(f"成功导出: {exported_files}")
    print(f"跳过文件: {skipped_files}")
    print(f"输出目录: {output_path.absolute()}")
    print(f"可以将 {output_path.absolute()} 目录导入到 Obsidian 中使用")

if __name__ == "__main__":
    import sys
    
    # 默认参数
    source_directory = "."
    output_directory = "exported_markdown"
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        source_directory = sys.argv[1]
    if len(sys.argv) > 2:
        output_directory = sys.argv[2]
    
    export_project_to_markdown(source_directory, output_directory)
