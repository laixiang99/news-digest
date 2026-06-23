# ============================================================
# 📱 WSL 本地构建 APK 脚本
# 使用方法：
#   1. 以管理员身份打开 PowerShell
#   2. 运行：wsl --install -d Ubuntu
#   3. 重启电脑
#   4. 运行本脚本
# ============================================================

echo "================================================"
echo "  📱  开始构建 Android APK"
echo "  每日新闻归纳助手"
echo "================================================"
echo ""

# 检查是否在 WSL 中
if ! grep -q Microsoft /proc/version 2>/dev/null; then
    echo "❌ 请在 WSL (Ubuntu) 中运行此脚本"
    echo "   在 PowerShell 中运行: wsl -d Ubuntu"
    exit 1
fi

echo "📦 1/6 更新系统包..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    git zip unzip openjdk-17-jdk \
    python3-pip python3-venv \
    autoconf libtool libffi-dev libssl-dev \
    libxml2-dev libxslt1-dev libncurses5-dev \
    ccache libtinfo5 libncurses5 automake cmake \
    curl wget libstdc++-12-dev

echo "📦 2/6 安装 Buildozer..."
pip3 install --upgrade buildozer cython virtualenv 2>&1 | tail -5

echo "📦 3/6 切换到项目目录..."
cd /mnt/d/codex/新闻归纳助手 || {
    echo "❌ 找不到项目目录"
    echo "   请检查路径是否正确"
    exit 1
}

echo "📦 4/6 清理旧的构建缓存（可选）..."
# 如果需要完全重新构建，取消下面注释
# rm -rf .buildozer bin

echo "📦 5/6 开始构建 APK（首次构建需要 20-40 分钟）..."
echo "   后续构建只需 2-5 分钟"
echo ""
buildozer android debug

echo ""
echo "================================================"
if [ -f bin/*.apk ]; then
    echo "  ✅ 构建成功！APK 文件在 bin/ 目录下"
    echo ""
    ls -lh bin/*.apk
    echo ""
    echo "  📱 将 APK 复制到手机安装即可使用"
else
    echo "  ❌ 构建失败，请检查上述错误信息"
fi
echo "================================================"
