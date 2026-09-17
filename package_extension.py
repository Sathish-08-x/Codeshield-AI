
"""
CodeShield AI — Chrome Extension Packager (Manifest V3)
Validates extension structure and packages codeshield-chrome-extension.zip
ready for upload to the Chrome Web Store Developer Dashboard or chrome://extensions.
"""

import os
import json
import zipfile
import sys

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def package_chrome_extension():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ext_dir = os.path.join(base_dir, "chrome-extension")
    zip_path = os.path.join(base_dir, "codeshield-chrome-extension.zip")

    print("=" * 60)
    print("  🛡️  CODESHIELD AI: CHROME EXTENSION PACKAGING UTILITY")
    print("=" * 60)

    if not os.path.exists(ext_dir):
        print(f"❌ Error: Extension directory not found at {ext_dir}")
        sys.exit(1)

    manifest_file = os.path.join(ext_dir, "manifest.json")
    if not os.path.exists(manifest_file):
        print("❌ Error: manifest.json is missing!")
        sys.exit(1)

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error: manifest.json is invalid JSON: {e}")
        sys.exit(1)

    assert manifest.get("manifest_version") == 3, "Expected manifest_version 3"
    assert manifest.get("name"), "Missing extension name"
    assert manifest.get("version"), "Missing extension version"
    print(f"  ✓ Validated Manifest V3: '{manifest['name']}' v{manifest['version']}")

    required_files = [
        "manifest.json",
        "popup.html",
        "popup.css",
        "popup.js",
        "background.js",
        "content.js",
        "icons/icon16.png",
        "icons/icon32.png",
        "icons/icon48.png",
        "icons/icon128.png"
    ]

    for rf in required_files:
        full_path = os.path.join(ext_dir, rf)
        if not os.path.exists(full_path):
            print(f"❌ Missing required file: {rf}")
            sys.exit(1)
        size = os.path.getsize(full_path)
        print(f"  ✓ {rf:<22} ({size} bytes)")

    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ext_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, ext_dir)
                zf.write(abs_path, rel_path)

    zip_size = os.path.getsize(zip_path) / 1024
    print("\n" + "=" * 60)
    print(f"  🎉 SUCCESS: Extension packaged into:")
    print(f"  📦 {zip_path} ({zip_size:.1f} KB)")
    print("=" * 60)
    print("\nReady for:")
    print("  1. 'Load unpacked' in chrome://extensions")
    print("  2. Direct ZIP upload to Chrome Web Store Developer Dashboard!")

if __name__ == "__main__":
    package_chrome_extension()
