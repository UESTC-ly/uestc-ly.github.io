#!/usr/bin/env python3
"""
为所有笔记页面注入 Prism.js 代码高亮
使用成熟的 Prism.js 库，避免自制正则的渲染错误
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"

def inject_prism_highlight():
    """在所有笔记HTML中注入 Prism.js CDN 和自定义脚本"""

    # Prism.js 核心 + 常用语言包（gzip 后约 20KB）
    prism_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" integrity="sha512-tN7Ec6zAFaVSG3TpNAKtk4DOHNpSwKHxxrsiw4GHKESGPs5njn/0sMCUMl2svV4wo4BK/rCP7juYz+zx+l6oeQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />'
    prism_js = '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js" integrity="sha512-7Z9J3l1+EYfeaPKcGXu3MS/7T+w19WtKQY/n+xzmw4hZhJ9tyYmcUS+4QqAlzhicE5LAfMQSF3iFTK9bQdTxXg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>'
    # 常用语言包
    prism_langs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-cpp.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>'

    # 自定义CSS和JS
    custom_css = '<link rel="stylesheet" href="../../assets/css/code-highlight.css">'
    custom_js = '<script defer src="../../assets/js/code-highlight.js"></script>'

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

            # 检查是否已经注入 Prism
            if 'prism.min.js' in content:
                skipped_count += 1
                continue

            # 移除旧的自制高亮CSS/JS（如果存在）
            content = re.sub(r'<link[^>]*code-highlight\.css[^>]*>\s*', '', content)
            content = re.sub(r'<script[^>]*code-highlight\.js[^>]*></script>\s*', '', content)

            # 计算相对路径深度
            depth = len(html_file.relative_to(NOTES_DIR).parts) - 1
            prefix = "../" * depth

            # 调整自定义文件路径
            custom_css_adjusted = f'<link rel="stylesheet" href="{prefix}../assets/css/code-highlight.css">'
            custom_js_adjusted = f'<script defer src="{prefix}../assets/js/code-highlight.js"></script>'

            # 注入到</head>之前（顺序：Prism CSS → 自定义CSS → Prism JS → 语言包 → 自定义JS）
            if '</head>' in content:
                injection = f'{prism_css}\n{custom_css_adjusted}\n{prism_js}\n{prism_langs}\n{custom_js_adjusted}\n'
                content = content.replace('</head>', f'{injection}</head>')

                # 写回文件
                html_file.write_text(content, encoding='utf-8')
                updated_count += 1

                if updated_count % 50 == 0:
                    print(f"已处理 {updated_count} 个文件...")

        except Exception as e:
            print(f"处理文件 {html_file} 时出错: {e}")

    print(f"\n✓ 完成！")
    print(f"  更新文件: {updated_count}")
    print(f"  跳过文件: {skipped_count}")
    print(f"\n使用 Prism.js 1.29.0（成熟稳定的语法高亮库）")
    print(f"  - 核心库: prism.min.js (~10KB gzip)")
    print(f"  - 语言包: Python, C++, Java, Bash, SQL")
    print(f"  - 自动语言检测 + 复制按钮")

if __name__ == "__main__":
    print("开始注入 Prism.js 代码高亮...")
    inject_prism_highlight()

