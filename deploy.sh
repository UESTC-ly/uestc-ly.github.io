#!/bin/bash

# GitHub Pages 部署脚本
# 使用方法：bash deploy.sh

set -e

echo "🚀 开始部署到 GitHub Pages..."

# 检查 Git 配置
if ! git config user.email > /dev/null 2>&1; then
    echo "⚠️  请先配置 Git 用户信息："
    echo "git config user.email \"your-email@example.com\""
    echo "git config user.name \"李杨\""
    exit 1
fi

# 查看修改
echo ""
echo "📝 修改的文件："
git status --short

# 确认提交
echo ""
read -p "确认提交并推送这些修改？(y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消部署"
    exit 0
fi

# 提交并推送
git add index.html assets/css/home-enhanced.css
git commit -m "优化主页布局：增强内容密度，改进专题展示

- 增加统计数据和技术栈标签
- 专题卡片网格布局，直接展示 6 个专题
- 改进视觉层次和按钮样式
- 完全响应式设计"

echo ""
echo "📤 推送到 GitHub..."
git push origin main

echo ""
echo "✅ 部署完成！"
echo "🔗 访问 https://uestc-ly.github.io/ 查看效果（等待 2-3 分钟构建）"
