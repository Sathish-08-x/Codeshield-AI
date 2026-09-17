# CodeShield AI — Chrome Extension (Manifest V3)

A high-precision **AI Code Detector & Stealth Humanizer** extension for Google Chrome.
Scan code on ChatGPT, LeetCode, GitHub, Claude, or Canvas, and naturalize it with CS Student Safe zero-break AST transforms.

---

## 🚀 Method 1: Load Extension Locally in Chrome ("Load Unpacked")

1. Open Google Chrome and go to:
   ```
   chrome://extensions
   ```
2. Enable **Developer mode** toggle in the top-right corner.
3. Click the **"Load unpacked"** button in the top-left corner.
4. Select the `chrome-extension` folder:
   ```
   c:\Users\sathi\OneDrive\Desktop\CA1-EVS\code detector\chrome-extension
   ```
5. Click the **Puzzle Piece icon** in Chrome's top toolbar, find **CodeShield AI**, and pin it to your toolbar!

---

## 📦 Method 2: Package & Upload to Chrome Web Store

1. In the project root, run the packaging utility:
   ```bash
   python package_extension.py
   ```
   This generates:
   ```
   codeshield-chrome-extension.zip
   ```
2. Go to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devcenter).
3. Click **"Add new item"** and upload `codeshield-chrome-extension.zip`.
4. Fill in your store listing description and publish!

---

## ⚡ Connecting with the CodeShield Backend

The extension communicates with your local CodeShield FastAPI server via `http://127.0.0.1:8000`:
1. Start your local server at any time using:
   - Double-click **`run.bat`** OR run `python run.py`.
2. When the server is active, the extension popup displays:
   `🟢 Backend Live`
3. If you ever deploy CodeShield to a remote server or VPS, you can update the backend URL in the extension's **Settings (⚙️)** tab.

---

## 🛠️ Extension Features

- **🔍 In-Browser Code Scanner**:
  - Highlights AI probability, detection verdict, and flagged stylometric signals.
  - Automatically identifies AI model families (OpenAI GPT-4o, Claude 3.5, Gemini, DeepSeek).
- **⚡ Stealth Humanizer**:
  - **CS Student Persona**: Guaranteed AI score $\le 18\%$, strictly zero robotic comments, human loop rhythms.
  - **Senior / Production Persona**: Compact idiomatic Pythonic comprehensions.
  - **Organic Persona**: Realistic iteration development scars (`// TODO:`, spacing drift).
- **📋 Right-Click Context Menu**:
  - Highlight code on any web page (LeetCode, ChatGPT, Canvas, Gradescope).
  - Right-click $\rightarrow$ **"🛡️ Scan Code with CodeShield AI"** or **"⚡ Humanize Code (Student Safe)"**.
