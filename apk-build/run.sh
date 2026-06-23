BUILD_DIR="D:/codex/新闻归纳助手/apk-build"
cd "$BUILD_DIR" || {
  BUILD_DIR2="/d/codex/新闻归纳助手/apk-build"
  cd "$BUILD_DIR2" || echo "Cannot find dir"
}
export npm_config_cache="$BUILD_DIR/.npm-cache"
export HOME="$BUILD_DIR"
echo "Current dir: $(pwd)"
echo "Ready to build"
