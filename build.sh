#!/bin/bash
# 本地构建脚本 - 用于测试GitHub Actions构建流程

echo "🔥 哈尔滨太热了 - 本地构建脚本"
echo "=================================="

# 检查必要的工具
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python"
    exit 1
fi

echo "🐍 Python 版本: $(python --version)"

# 运行数据分析（如果工具存在）
if [ -f "tools/environment_analyzer.py" ]; then
    echo "📊 运行数据分析..."
    python tools/environment_analyzer.py . || echo "⚠️ 数据分析失败，继续构建..."
else
    echo "⚠️ 数据分析工具不存在，跳过分析步骤"
fi

# 清理并创建构建目录
echo "🏗️ 准备构建目录..."
rm -rf dist
mkdir -p dist

# 复制主要网站文件
echo "📄 复制网站文件..."
if [ -f "index.html" ]; then
    cp index.html dist/
    echo "✅ 已复制 index.html"
else
    echo "❌ index.html 不存在"
    exit 1
fi

# 复制资源文件
if [ -d "images" ]; then
    cp -r images dist/
    echo "📷 已复制图片资源"
else
    echo "ℹ️ 无图片资源目录"
fi

# 复制数据文件
if [ -d "data" ]; then
    cp -r data dist/
    echo "📊 已复制数据文件"
else
    echo "ℹ️ 无数据目录"
fi

# 创建API端点
echo "🔗 创建API端点..."
mkdir -p dist/api
if [ -f "data/environment_data.json" ]; then
    cp data/environment_data.json dist/api/data.json
    echo "✅ 已创建 API 数据端点"
else
    echo "ℹ️ 无数据JSON文件，创建空的API端点"
    echo '{"message": "数据征集中", "schools": [], "timestamp": "'$(date -Iseconds)'"}' > dist/api/data.json
fi

# 生成站点地图
echo "🗺️ 生成站点地图..."
cat > dist/sitemap.txt << EOF
https://hrbistohot.com/
https://hrbistohot.com/api/data.json
EOF

# 生成robots.txt
echo "🤖 生成robots.txt..."
cat > dist/robots.txt << EOF
User-agent: *
Allow: /
Sitemap: https://hrbistohot.com/sitemap.txt
EOF

# 复制CNAME文件（如果存在）
if [ -f "dist/CNAME" ]; then
    echo "🏷️ CNAME 文件已存在"
elif [ -f "CNAME" ]; then
    cp CNAME dist/
    echo "🏷️ 已复制 CNAME 文件"
fi

# 禁用Jekyll处理
touch dist/.nojekyll
echo "🚫 已禁用 Jekyll 处理"

# 生成构建信息
echo "📋 生成构建信息..."
cat > dist/build-info.json << EOF
{
  "buildTime": "$(date -Iseconds)",
  "buildType": "local",
  "version": "$(date +%Y.%m.%d.%H%M)",
  "files": [
    $(find dist -type f -name "*.html" -o -name "*.json" -o -name "*.txt" | sort | sed 's/dist\///' | sed 's/.*/"&"/' | paste -sd ',' -)
  ]
}
EOF

echo ""
echo "✅ 构建完成！"
echo "📂 构建内容:"
ls -la dist/

echo ""
echo "🌐 本地预览:"
echo "   在 dist/ 目录中启动 HTTP 服务器查看效果"
echo "   例如: cd dist && python -m http.server 8000"
echo ""
echo "🚀 部署:"
echo "   dist/ 目录中的所有文件可以直接部署到静态网站托管服务"

# 可选：启动本地服务器预览
read -p "🤔 是否启动本地预览服务器？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 启动本地服务器 http://localhost:8000"
    cd dist && python -m http.server 8000
fi
