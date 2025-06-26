@echo off
REM 本地构建脚本 - Windows版本
echo 🔥 哈尔滨太热了 - 本地构建脚本 (Windows)
echo ==================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python
    pause
    exit /b 1
)

echo 🐍 Python 版本:
python --version

REM 运行数据分析
if exist "tools\environment_analyzer.py" (
    echo 📊 运行数据分析...
    python tools\environment_analyzer.py . || echo ⚠️ 数据分析失败，继续构建...
) else (
    echo ⚠️ 数据分析工具不存在，跳过分析步骤
)

REM 清理并创建构建目录
echo 🏗️ 准备构建目录...
if exist "dist" rmdir /s /q dist
mkdir dist

REM 复制主要网站文件
echo 📄 复制网站文件...
if exist "index.html" (
    copy index.html dist\ >nul
    echo ✅ 已复制 index.html
) else (
    echo ❌ index.html 不存在
    pause
    exit /b 1
)

REM 复制资源文件
if exist "images" (
    xcopy images dist\images\ /e /i /q >nul
    echo 📷 已复制图片资源
) else (
    echo ℹ️ 无图片资源目录
)

REM 复制数据文件
if exist "data" (
    xcopy data dist\data\ /e /i /q >nul
    echo 📊 已复制数据文件
) else (
    echo ℹ️ 无数据目录
)

REM 创建API端点
echo 🔗 创建API端点...
mkdir dist\api 2>nul
if exist "data\environment_data.json" (
    copy data\environment_data.json dist\api\data.json >nul
    echo ✅ 已创建 API 数据端点
) else (
    echo ℹ️ 无数据JSON文件，创建空的API端点
    echo {"message": "数据征集中", "schools": [], "timestamp": "%date% %time%"} > dist\api\data.json
)

REM 生成站点地图
echo 🗺️ 生成站点地图...
(
echo https://hrbistohot.com/
echo https://hrbistohot.com/api/data.json
) > dist\sitemap.txt

REM 生成robots.txt
echo 🤖 生成robots.txt...
(
echo User-agent: *
echo Allow: /
echo Sitemap: https://hrbistohot.com/sitemap.txt
) > dist\robots.txt

REM 复制CNAME文件
if exist "dist\CNAME" (
    echo 🏷️ CNAME 文件已存在
) else if exist "CNAME" (
    copy CNAME dist\ >nul
    echo 🏷️ 已复制 CNAME 文件
)

REM 禁用Jekyll处理
echo. > dist\.nojekyll
echo 🚫 已禁用 Jekyll 处理

REM 生成构建信息
echo 📋 生成构建信息...
echo { > dist\build-info.json
echo   "buildTime": "%date% %time%", >> dist\build-info.json
echo   "buildType": "local-windows", >> dist\build-info.json
echo   "version": "%date:~0,4%.%date:~5,2%.%date:~8,2%.%time:~0,2%%time:~3,2%", >> dist\build-info.json
echo   "platform": "Windows" >> dist\build-info.json
echo } >> dist\build-info.json

echo.
echo ✅ 构建完成！
echo 📂 构建内容:
dir dist

echo.
echo 🌐 本地预览:
echo    在 dist 目录中启动 HTTP 服务器查看效果
echo    例如: cd dist ^&^& python -m http.server 8000
echo.
echo 🚀 部署:
echo    dist 目录中的所有文件可以直接部署到静态网站托管服务

REM 询问是否启动本地服务器
set /p choice="🤔 是否启动本地预览服务器？(y/N): "
if /i "%choice%"=="y" (
    echo 🌐 启动本地服务器 http://localhost:8000
    cd dist
    python -m http.server 8000
) else (
    echo 👋 构建完成，可手动启动服务器预览
    pause
)
