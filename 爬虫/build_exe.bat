@echo off
chcp 65001 >nul
echo ============================================
echo 正在打包Cookie获取工具为可执行文件...
echo ============================================
echo.

REM 检查是否安装了pyinstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo 正在打包 get_cookie_simple.py...
pyinstaller --onefile --noconsole --name "获取淘宝Cookie" get_cookie_simple.py

echo.
echo ============================================
if exist "dist\获取淘宝Cookie.exe" (
    echo ✅ 打包成功！
    echo.
    echo 可执行文件位置: dist\获取淘宝Cookie.exe
    echo.
    echo 使用方法:
    echo 1. 双击运行 "获取淘宝Cookie.exe"
    echo 2. 按提示操作即可
) else (
    echo ❌ 打包失败，请检查错误信息
)
echo ============================================
pause
