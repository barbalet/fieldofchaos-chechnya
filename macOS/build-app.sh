#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
swift build -c release
bin_dir=$(swift build -c release --show-bin-path)
app_dir="$PWD/macOS/build/Field of Chaos.app"
mkdir -p "$app_dir/Contents/MacOS"
cp "$bin_dir/FieldOfChaos" "$app_dir/Contents/MacOS/FieldOfChaos"
cat > "$app_dir/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>FieldOfChaos</string>
<key>CFBundleIdentifier</key><string>org.fieldofchaos.chechnya</string>
<key>CFBundleName</key><string>Field of Chaos</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>14.0</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --sign - "$app_dir"
printf 'Built %s\n' "$app_dir"
