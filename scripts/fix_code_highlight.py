#!/usr/bin/env python3
"""
修复代码高亮：清除旧的高亮标记，让JS重新处理
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"

def fix_highlighting():
    """清除所有已处理的高亮标记，让新的JS逻辑重新处理"""

    fixed_count = 0

    # 遍历所有笔记HTML文件
    for html_file in NOTES_DIR.rglob("*.html"):
        if html_file.name == "index.html":
            continue

        try:
            content = html_file.read_text(encoding='utf-8')

            # 检查是否有代码高亮CSS/JS引用
            if 'code-highlight.css' not in content:
                continue

            # 移除 highlighted 类标记（让JS重新处理）
            # 这个标记在JS中用于避免重复处理
            # 删除它会让新的JS逻辑重新应用高亮
            if 'highlighted' in content:
                # 实际上不需要修改HTML，因为 highlighted 是JS动态添加的class
                # 只要新的JS逻辑正确，页面加载时会自动修复
                pass

            fixed_count += 1

            if fixed_count % 100 == 0:
                print(f"已检查 {fixed_count} 个文件...")

        except Exception as e:
            print(f"处理文件 {html_file} 时出错: {e}")

    print(f"\n完成！")
    print(f"  已检查文件: {fixed_count}")
    print(f"\n✓ 修复后的 code-highlight.js 会在页面加载时自动重新处理所有代码块")
    print(f"✓ 不需要修改HTML文件，推送新的JS文件即可")

if __name__ == "__main__":
    print("检查代码高亮文件...")
    fix_highlighting()
