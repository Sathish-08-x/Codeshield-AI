# 🛡️ CodeShield AI — AI Code Detector & Humanizer

An advanced, cybernetic web application for detecting AI-generated code, providing an interactive *"Should I Humanize It?"* workflow with side-by-side diffing, recursive folder/snippet uploads, high-performance canvas visual effects, sound synthesizers, SQLite database persistence, deep visual theme customization, and an editable developer profile showcase.

---

## 🚀 Quick Start

### 1. Launch with One Click
Double click `run.bat` or run:
```bash
python run.py
```
This automatically initializes the SQLite database, launches the FastAPI server, and opens your browser at:
👉 **`http://127.0.0.1:8000`**

---

## ✨ Features Breakdown

### 1. 🔍 Multi-Metric AI Detection Engine
- **Token Perplexity & Uniformity**: Evaluates standard deviation of line lengths and syntactical clustering typical of LLMs.
- **AI Comment & Tutorial Tropes**: Detects `# Step 1:`, `# Helper function to...`, `# Example usage:`, conversational docstrings, and markdown code fence residue.
- **Identifier Heuristics**: Flags textbook robotic naming conventions (`calculate_total_sum`, `data_list`, `current_item`).
- **Scaffolding Heuristics**: Identifies stereotypical entry scaffolds and generic `except Exception as e:` boilerplate.
- **Burstiness Metric**: Evaluates token cadence variance across sliding windows (human code exhibits high burstiness; AI code is uniformly smooth).
- **Line-by-Line Heatmap Inspector**: Visualizes lines marked as **AI Generated (Red)**, **Mixed (Yellow)**, or **Human Written (Green)** with hover explanations.

### 2. ⚡ "Should I Humanize It?" Flow & Humanizer Engine
- When AI code is detected, a glowing holographic alert banner prompts:
  **"🚨 AI Code Detected! Should I humanize it?"**
- **Humanizer Modes**:
  - *Pragmatic Senior Dev*: Concise, clean naming, early returns, and natural developer comments.
  - *Clean Minimalist*: Strips all redundant comments and scaffolding, compact format.
  - *Production Grade*: Retains clean structure, standardizes error handling, refactors robotic docstrings.
- **Side-by-Side Diff Inspector**: Live red/green diff comparing original vs humanized code.
- **1-Click Re-scan**: Validates that the AI score drops into the human range.
- **Copy & Download**: Export clean `.py` or source file immediately.

### 3. 📁 Dual Ingestion: Snippet Editor & Folder Ingestion
- **Code Snippet Editor**: Direct text paste with language selection and 1-click test samples (Obvious ChatGPT code, Human code, Mixed code).
- **Recursive Folder Upload**: Drag-and-drop or use the folder picker (`webkitdirectory`) to scan entire project repositories.
- **Project File Tree**: Displays all scanned files with per-file AI percentage badges (`88% AI`, `12% Clean`), with on-click line inspector.

### 4. 🎨 Visual Customizer & VFX
- **6 Built-in Themes**:
  - *Cyberpunk Neon* (Cyan / Magenta / Void)
  - *Matrix Core* (Terminal Green / Black)
  - *Abyssal Space* (Deep Sky Blue / Indigo)
  - *Sunset Synthwave* (Neon Pink / Coral / Purple)
  - *Crimson Eclipse* (Red / Gunmetal / Ember)
  - *Minimal Slate* (Sleek Charcoal / Platinum)
- **Interactive Canvas VFX**: 4 modes (Infinite 3D Cyber Grid, Neural Constellation, Matrix Digital Rain, Warp Stardust) with particle density and mouse reactivity.
- **Holographic Scanlines & Neon Glow**: Adjustable slider and toggle.
- **Typography Selector**: JetBrains Mono, Fira Code, Orbitron, Inter.
- **Synthesized Sci-Fi Audio (Web Audio API)**: Scanning sweeps, alert pulses, humanize shimmers, and button clicks with a mute toggle.

### 5. 💾 SQLite Database (`code_detector.db`)
- Persistent history of all snippet and folder scans with files, metrics, and timestamps.
- Ability to reload, inspect past scans, and delete records.
- Stores user appearance preferences permanently.

### 6. 👤 Developer Profile Showcase & In-App Editor
- Cybernetic footer card with rotating holographic avatar ring, title, bio, tech stack pills, and social links (GitHub, LinkedIn, Email, Portfolio).
- Built-in **"Edit My Info"** modal allowing you to update your developer details directly to the database anytime.

---

## 📦 Project Structure

```
├── database.py              # SQLite schema, tables, and CRUD operations
├── engine/
│   ├── detector.py          # Multi-metric AI code detection algorithms
│   └── humanizer.py         # Code humanizer engine & diff generator
├── main.py                  # FastAPI REST backend & static router
├── run.py                   # Automatic browser launcher
├── run.bat                  # Windows batch launcher
└── static/
    ├── index.html           # Single-page cyberpunk HUD interface
    ├── css/
    │   └── style.css        # Master stylesheet with theme variables & VFX
    └── js/
        ├── vfx.js           # Canvas particle engine & Web Audio synthesizer
        └── app.js           # Frontend controller, drag & drop, diff viewer
```
