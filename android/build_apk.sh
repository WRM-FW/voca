#!/usr/bin/env bash
# Voca Android build — manual pipeline (no Gradle): aapt2 -> javac -> d8 -> sign.
# Requires: JDK 17 (javac/keytool) and the Android SDK at $ANDROID_SDK_ROOT
# (default ~/workspace/tools/android-sdk) with platforms;android-34 and
# build-tools;34.0.0.
set -euo pipefail
cd "$(dirname "$0")"

SDK="${ANDROID_SDK_ROOT:-$HOME/workspace/tools/android-sdk}"
BT="$SDK/build-tools/34.0.0"
AJAR="$SDK/platforms/android-34/android.jar"
KS="${VOCA_KEYSTORE:-$HOME/workspace/voca-v106/android-signing/voca.keystore}"
STOREPASS="${VOCA_STOREPASS:-vocaandroid}"
OUT=build
APK_OUT="${1:-$HOME/workspace/voca-v106/release/Voca_v1.1.2.apk}"

[ -f "$AJAR" ] || { echo "android.jar not found at $AJAR — install platforms;android-34 first"; exit 1; }
mkdir -p "$(dirname "$KS")"
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore "$KS" -alias voca -keyalg RSA -keysize 2048 \
    -validity 10000 -storepass "$STOREPASS" -keypass "$STOREPASS" \
    -dname "CN=Voca, OU=Personal, O=WRM-FW" > /dev/null 2>&1
  echo "generated signing keystore: $KS (keep it — losing it means future builds cannot update in place)"
fi

# Launcher icons are generated from the repo's master icon (kept out of git).
python3 - << 'PYEOF'
from PIL import Image
import os
src = Image.open('../assets/icons/icon_512.png').convert('RGBA')
for name, size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    d = 'res/mipmap-%s' % name
    os.makedirs(d, exist_ok=True)
    src.resize((size, size), Image.LANCZOS).save(os.path.join(d, 'ic_launcher.png'))
PYEOF

rm -rf "$OUT"
mkdir -p "$OUT/assets" "$OUT/gen" "$OUT/classes" "$OUT/dex"

# Assets: the assembled single-file web app (same build as the Windows app),
# the Agent import stub, and the bridge polyfill the host injects.
cp ../windows/app/index.html "$OUT/assets/index.html"
cp ../src/webapp/voca_auto_import.js "$OUT/assets/voca_auto_import.js"
cp bridge.js "$OUT/assets/bridge.js"

"$BT/aapt2" compile --dir res -o "$OUT/res.zip"
"$BT/aapt2" link -o "$OUT/base.apk" -I "$AJAR" --manifest AndroidManifest.xml \
  --java "$OUT/gen" -A "$OUT/assets" "$OUT/res.zip"

javac -source 8 -target 8 -encoding UTF-8 -cp "$AJAR" -d "$OUT/classes" \
  $(find src "$OUT/gen" -name '*.java')
"$BT/d8" --lib "$AJAR" --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')

cp "$OUT/base.apk" "$OUT/unsigned.apk"
(cd "$OUT/dex" && zip -q "../unsigned.apk" classes.dex)
"$BT/zipalign" -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$STOREPASS" --key-pass "pass:$STOREPASS" \
  --out "$APK_OUT" "$OUT/aligned.apk"
"$BT/apksigner" verify --print-certs "$APK_OUT" | head -3
echo "APK built: $APK_OUT"
