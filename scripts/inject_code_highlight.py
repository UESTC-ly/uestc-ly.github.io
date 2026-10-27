#!/usr/bin/env python3
"""
为所有笔记页面注入代码高亮功能
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"

def inject_code_highlight():
    """在所有笔记HTML中注入代码高亮CSS和JS"""

    # CSS和JS引用
    css_link = '<link rel="stylesheet" href="../../assets/css/code-highlight.css">'
    js_script = '<script defer src="../../assets/js/code-highlight.js"></script>'

    # 统计
    updated_count = 0
    skipped_count = 0

    # 遍历所有笔记HTML文件
    for html_file in NOTES_DIR.rglob("*.html"):
        # 跳过index.html
        if html_file.name == "index.html":
            continue

        try:
            content = html_file.read_text(encoding='utf-8')

            # 检查是否已经注入
            if 'code-highlight.css' in content:
                skipped_count += 1
                continue

            # 注入CSS（在</head>之前）
            if '</head>' in content:
                # 计算相对路径深度
                depth = len(html_file.relative_to(NOTES_DIR).parts) - 1
                prefix = "../" * depth

                css_link_adjusted = f'<link rel="stylesheet" href="{prefix}../assets/css/code-highlight.css">'
                js_script_adjusted = f'<script defer src="{prefix}../assets/js/code-highlight.js"></script>'

                # 注入到</head>之前
                content = content.replace('</head>', f'{css_link_adjusted}\n{js_script_adjusted}\n</head>')

                # 写回文件
                html_file.write_text(content, encoding='utf-8')
                updated_count += 1

                if updated_count % 50 == 0:
                    print(f"已处理 {updated_count} 个文件...")

        except Exception as e:
            print(f"处理文件 {html_file} 时出错: {e}")

    print(f"\n完成！")
    print(f"  更新文件: {updated_count}")
    print(f"  跳过文件: {skipped_count}")

if __name__ == "__main__":
    print("开始注入代码高亮功能...")
    inject_code_highlight()
