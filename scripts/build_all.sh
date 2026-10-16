#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "[1/5] Building Voca v1.0.3 multi-DPI Win32 icons and cross-platform WOFF2 font subsets..."
# Regenerating assets needs the original OpenType sources (Debian/Ubuntu: fonts-inter,
# fonts-noto-cjk) at the absolute paths hardcoded in build_assets_v103.py.
# assets/ already ships the generated WOFF2 subsets and icon frames, so this step is opt-in.
if [ "${VOCA_BUILD_ASSETS:-0}" = "1" ]; then
  python3 "$ROOT_DIR/scripts/build_assets_v103.py"
else
  echo "  skipped (set VOCA_BUILD_ASSETS=1 to regenerate assets/fonts and assets/icons from system OpenType sources)"
fi

echo "[2/5] Assembling Voca v1.0.3 offline frontend..."
VOCA_EMBEDDED_ASSETS="$ROOT_DIR/assets/embedded_assets.json" \
VOCA_CORE233_JSON="$ROOT_DIR/windows/data/voca_lexicon.json" \
VOCA_PACK_JSON="$ROOT_DIR/src/lexicon/v103_lexicon_payload.json" \
VOCA_OUT_HTML="$ROOT_DIR/windows/app/index.html" \
PYTHONPATH="$ROOT_DIR/src/webapp" python3 "$ROOT_DIR/src/webapp/make_html_v103_part3.py"

cp "$ROOT_DIR/windows/app/index.html" "$ROOT_DIR/src/webapp/index.html"
cp "$ROOT_DIR/windows/app/index.html" "$ROOT_DIR/src/android/app/src/main/assets/index.html"

echo "[3/5] Building Windows 64-bit PE32+ executable (Voca.exe) and Android v1.0.3 signed APK..."
# Paths go through the environment rather than shell interpolation so the script also
# works under MSYS/Git Bash, where $ROOT_DIR is a POSIX-style path Python cannot open.
VOCA_ASSETS_DIR="$ROOT_DIR/assets" \
VOCA_OUT_ICO="$ROOT_DIR/windows/voca.ico" \
VOCA_OUT_EXE="$ROOT_DIR/windows/Voca.exe" \
VOCA_OUT_APK="$ROOT_DIR/android/Voca_v1.0.3_release.apk" \
VOCA_APP_HTML="$ROOT_DIR/windows/app/index.html" \
PYTHONPATH="$ROOT_DIR/scripts" python3 -c "
import os
import build_exe_v103, build_apk_v103
build_exe_v103.create_ico_file(os.environ['VOCA_OUT_ICO'])
build_exe_v103.build_voca_exe(os.environ['VOCA_OUT_EXE'])
with open(os.environ['VOCA_APP_HTML'], 'rb') as f:
    build_apk_v103.build_signed_apk_v103(os.environ['VOCA_OUT_APK'], f.read())
"

echo "[4/5] Running AOSP binary & cryptographic verification..."
VOCA_VERIFY_APK="$ROOT_DIR/android/Voca_v1.0.3_release.apk" \
PYTHONPATH="$ROOT_DIR/scripts" python3 -c "
import os
import verify_apk_deep
verify_apk_deep.verify_apk_file(os.environ['VOCA_VERIFY_APK'])
"

echo "Voca v1.0.3 reproducible build and verification completed successfully."
