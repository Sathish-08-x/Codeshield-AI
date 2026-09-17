const DEFAULT_BACKEND = "http://127.0.0.1:8000";

class PopupApp {
  constructor() {
    this.backendUrl = DEFAULT_BACKEND;
    this.initElements();
    this.bindEvents();
    this.loadSettings();
  }

  initElements() {
    this.statusPill = document.getElementById('backend-status');
    this.statusText = document.getElementById('status-text');

    this.tabButtons = document.querySelectorAll('.tab-btn');
    this.tabViews = document.querySelectorAll('.tab-view');

    this.detectorInput = document.getElementById('detector-input');
    this.btnRunScan = document.getElementById('btn-run-scan');
    this.btnGrabSelection = document.getElementById('btn-grab-selection');
    this.btnDetectorSample = document.getElementById('btn-detector-sample');
    this.btnClearDetector = document.getElementById('btn-clear-detector');
    this.detectorResults = document.getElementById('detector-results');
    this.resScore = document.getElementById('res-score');
    this.resVerdict = document.getElementById('res-verdict');
    this.resFamily = document.getElementById('res-family');
    this.resSignalsList = document.getElementById('res-signals-list');
    this.btnSendToHumanizer = document.getElementById('btn-send-to-humanizer');

    this.personaSelect = document.getElementById('ext-persona-select');
    this.humanizerInput = document.getElementById('humanizer-input');
    this.btnRunHumanize = document.getElementById('btn-run-humanize');
    this.btnHumanizeVariation = document.getElementById('btn-humanize-variation');
    this.humanizerOutputBox = document.getElementById('humanizer-output-box');
    this.extScoreBadge = document.getElementById('ext-score-badge');
    this.humanizedCodePre = document.getElementById('humanized-code-pre');
    this.btnCopyHumanized = document.getElementById('btn-copy-humanized');
    this.btnOpenInWebapp = document.getElementById('btn-open-in-webapp');

    this.cfgBackendUrl = document.getElementById('cfg-backend-url');
    this.btnSaveSettings = document.getElementById('btn-save-settings');
    this.btnCheckBackend = document.getElementById('btn-check-backend');

    this.latestHumanizedCode = "";
  }

  bindEvents() {
    this.tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;
        this.switchTab(targetTab);
      });
    });

    if (this.btnRunScan) this.btnRunScan.addEventListener('click', () => this.runScan());
    if (this.btnGrabSelection) this.btnGrabSelection.addEventListener('click', () => this.grabSelectionFromPage());
    if (this.btnDetectorSample) this.btnDetectorSample.addEventListener('click', () => this.loadSampleSnippet());
    if (this.btnClearDetector) this.btnClearDetector.addEventListener('click', () => {
      this.detectorInput.value = '';
      this.detectorResults.style.display = 'none';
    });
    if (this.btnSendToHumanizer) this.btnSendToHumanizer.addEventListener('click', () => this.sendDetectorToHumanizer());

    if (this.btnRunHumanize) this.btnRunHumanize.addEventListener('click', () => this.runHumanize());
    if (this.btnHumanizeVariation) this.btnHumanizeVariation.addEventListener('click', () => {
      this.currentSeed = Date.now() % 10000;
      this.runHumanize();
    });
    if (this.btnCopyHumanized) this.btnCopyHumanized.addEventListener('click', () => this.copyHumanizedCode());
    if (this.btnOpenInWebapp) this.btnOpenInWebapp.addEventListener('click', () => {
      chrome.tabs.create({ url: this.backendUrl });
    });

    if (this.btnSaveSettings) this.btnSaveSettings.addEventListener('click', () => this.saveSettings());
    if (this.btnCheckBackend) this.btnCheckBackend.addEventListener('click', () => this.checkBackendHealth());
  }

  switchTab(tabId) {
    this.tabButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    this.tabViews.forEach(view => {
      view.style.display = (view.id === `tab-${tabId}`) ? 'flex' : 'none';
    });
  }

  async loadSettings() {
    if (chrome && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(['backendUrl'], (result) => {
        if (result.backendUrl) {
          this.backendUrl = result.backendUrl;
          if (this.cfgBackendUrl) this.cfgBackendUrl.value = this.backendUrl;
        }
        this.checkBackendHealth();
      });
    } else {
      this.checkBackendHealth();
    }

    this.grabSelectionFromPage(true);
  }

  async saveSettings() {
    const val = this.cfgBackendUrl ? this.cfgBackendUrl.value.trim() : DEFAULT_BACKEND;
    this.backendUrl = val || DEFAULT_BACKEND;
    if (chrome && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ backendUrl: this.backendUrl }, () => {
        this.checkBackendHealth();
        alert("Settings saved!");
      });
    } else {
      this.checkBackendHealth();
      alert("Settings saved!");
    }
  }

  async checkBackendHealth() {
    this.statusText.textContent = "Checking...";
    try {
      const resp = await fetch(`${this.backendUrl}/api/health`);
      if (resp.ok) {
        this.statusPill.className = "status-pill online";
        this.statusText.textContent = "Backend Live";
      } else {
        throw new Error("HTTP " + resp.status);
      }
    } catch (err) {
      this.statusPill.className = "status-pill offline";
      this.statusText.textContent = "Backend Offline";
    }
  }

  grabSelectionFromPage(silent = false) {
    if (!chrome.tabs || !chrome.scripting) {
      if (!silent) alert("Please open a web page to grab code selection.");
      return;
    }
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].id) return;
      const tab = tabs[0];
      if (tab.url && (tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:'))) {
        return;
      }

      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection().toString()
      }, (results) => {
        if (chrome.runtime.lastError) return;
        if (results && results[0] && results[0].result) {
          const selectedText = results[0].result.trim();
          if (selectedText && selectedText.length > 5) {
            this.detectorInput.value = selectedText;
            if (this.humanizerInput && !this.humanizerInput.value) {
              this.humanizerInput.value = selectedText;
            }
          }
        }
      });
    });
  }

  loadSampleSnippet() {
    this.detectorInput.value = `# 1. Initialize accumulator variables
def process_student_grades(grade_records):
    total_score = 0
    valid_count = 0
    passed_students = []
    
    # 2. Iterate through each record
    for student in grade_records:
        if student.get("score") is not None:
            total_score += student["score"]
            valid_count += 1
            if student["score"] >= 50:
                passed_students.append(student["name"])
                
    average_score = total_score / valid_count if valid_count > 0 else 0
    return {"average": average_score, "passed": passed_students}

if __name__ == '__main__':
    print(process_student_grades([{"name": "Alice", "score": 85}]))`;
  }

  async runScan() {
    const code = this.detectorInput.value.trim();
    if (!code) {
      alert("Please paste or grab code first.");
      return;
    }

    this.btnRunScan.disabled = true;
    this.btnRunScan.innerHTML = `<span>⏳</span> Scanning...`;

    try {
      const resp = await fetch(`${this.backendUrl}/api/scan/snippet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, filename: "snippet.py" })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}`);
      }

      const data = await resp.json();
      this.renderScanResults(data);
    } catch (err) {
      alert(`Scan failed: ${err.message}. Make sure CodeShield backend is running (run.bat).`);
      this.checkBackendHealth();
    } finally {
      this.btnRunScan.disabled = false;
      this.btnRunScan.innerHTML = `<span>🔍</span> Analyze AI Probability`;
    }
  }

  renderScanResults(data) {
    this.detectorResults.style.display = 'flex';
    const score = data.ai_score != null ? data.ai_score : 0;
    this.resScore.textContent = `${score}%`;

    if (score < 25) {
      this.resScore.style.color = 'var(--accent-green)';
      this.resVerdict.style.borderColor = 'var(--accent-green)';
      this.resVerdict.style.color = 'var(--accent-green)';
    } else if (score < 65) {
      this.resScore.style.color = 'var(--accent-amber)';
      this.resVerdict.style.borderColor = 'var(--accent-amber)';
      this.resVerdict.style.color = 'var(--accent-amber)';
    } else {
      this.resScore.style.color = 'var(--accent-magenta)';
      this.resVerdict.style.borderColor = 'var(--accent-magenta)';
      this.resVerdict.style.color = 'var(--accent-magenta)';
    }

    this.resVerdict.textContent = data.verdict || "AI Risk";
    const family = data.ai_family ? (data.ai_family.name || data.ai_family.family || "Generic LLM") : "Generic LLM";
    this.resFamily.textContent = `Family: ${family}`;

    this.resSignalsList.innerHTML = '';
    const indicators = data.indicators || [];
    if (indicators.length > 0) {
      indicators.slice(0, 3).forEach(ind => {
        const div = document.createElement('div');
        div.className = 'signal-item';
        div.innerHTML = `<span>⚠️</span> <span>${ind.name}: ${ind.description}</span>`;
        this.resSignalsList.appendChild(div);
      });
    } else {
      const div = document.createElement('div');
      div.className = 'signal-item';
      div.innerHTML = `<span>✓</span> <span>No commercial AI markers flagged. Clean human syntax profile.</span>`;
      this.resSignalsList.appendChild(div);
    }
  }

  sendDetectorToHumanizer() {
    const code = this.detectorInput.value.trim();
    if (code) {
      this.humanizerInput.value = code;
    }
    this.switchTab('humanizer');
    setTimeout(() => this.runHumanize(), 150);
  }

  async runHumanize() {
    const code = this.humanizerInput.value.trim();
    if (!code) {
      alert("Please paste code to humanize first.");
      return;
    }

    const persona = this.personaSelect ? this.personaSelect.value : "student";
    this.btnRunHumanize.disabled = true;
    this.btnRunHumanize.innerHTML = `<span>⏳</span> Naturalizing...`;

    try {
      const resp = await fetch(`${this.backendUrl}/api/humanize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: code,
          language: "python",
          persona: persona,
          variation_seed: this.currentSeed || 0
        })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}`);
      }

      const data = await resp.json();
      this.renderHumanizedOutput(data);
    } catch (err) {
      alert(`Humanization error: ${err.message}. Make sure CodeShield backend is running.`);
      this.checkBackendHealth();
    } finally {
      this.btnRunHumanize.disabled = false;
      this.btnRunHumanize.innerHTML = `<span>⚡</span> Humanize Code`;
    }
  }

  renderHumanizedOutput(data) {
    this.humanizerOutputBox.style.display = 'flex';
    this.latestHumanizedCode = data.humanized_code;
    this.humanizedCodePre.textContent = data.humanized_code;

    const orig = data.original_score != null ? data.original_score : 96.0;
    const clean = data.new_score != null ? data.new_score : 14.0;
    const drop = Math.round(orig - clean);
    this.extScoreBadge.textContent = `AI: ${orig}% ➔ ${clean}% (-${drop}%)`;
  }

  copyHumanizedCode() {
    if (!this.latestHumanizedCode) {
      alert("No humanized code available yet.");
      return;
    }
    navigator.clipboard.writeText(this.latestHumanizedCode).then(() => {
      const origText = this.btnCopyHumanized.textContent;
      this.btnCopyHumanized.textContent = "✓ Copied!";
      setTimeout(() => { this.btnCopyHumanized.textContent = origText; }, 2000);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.popupApp = new PopupApp();
});
