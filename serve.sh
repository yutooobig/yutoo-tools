#!/usr/bin/env bash
# 本地预览：先构建，再起服务。避免"改了文件忘了 build"的坑。
set -e
cd "$(dirname "$0")"
PORT="${1:-8080}"

python3 build.py || python build.py

echo
echo "预览地址 http://localhost:${PORT}"
echo "改了 projects/ 里的文件后，重新跑一次 ./serve.sh（或另开终端执行 python3 build.py）"
echo
exec python3 -m http.server "$PORT"
