const DEFAULT_API = "http://127.0.0.1:8000";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "codeshield-scan-selection",
    title: "🛡️ Scan Code with CodeShield AI",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "codeshield-humanize-selection",
    title: "⚡ Humanize Code (Student Safe < 18%)",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const selectedText = info.selectionText;
  if (!selectedText || !selectedText.trim()) return;

  const storage = await chrome.storage.local.get(["backendUrl"]);
  const backendUrl = storage.backendUrl || DEFAULT_API;

  if (info.menuItemId === "codeshield-scan-selection") {
    try {
      const resp = await fetch(`${backendUrl}/api/scan/snippet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: selectedText, filename: "selected_snippet.py" })
      });
      if (resp.ok) {
        const data = await resp.json();
        const score = data.ai_score != null ? data.ai_score : 0;
        const verdict = data.verdict || "Scanned";
        
        chrome.action.setBadgeText({ text: `${Math.round(score)}%` });
        chrome.action.setBadgeBackgroundColor({ color: score > 60 ? "#ef4444" : "#10b981" });

        if (tab && tab.id) {
          chrome.tabs.sendMessage(tab.id, {
            type: "CODESHIELD_ALERT",
            message: `🛡️ CodeShield AI Scan: ${score}% AI Risk (${verdict})`
          });
        }
      }
    } catch (err) {
      console.warn("Scan failed from background:", err);
    }
  } else if (info.menuItemId === "codeshield-humanize-selection") {
    try {
      const resp = await fetch(`${backendUrl}/api/humanize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: selectedText, language: "python", persona: "student" })
      });
      if (resp.ok) {
        const data = await resp.json();
        const humanized = data.humanized_code;

        if (tab && tab.id) {
          chrome.tabs.sendMessage(tab.id, {
            type: "CODESHIELD_HUMANIZED_RESULT",
            humanizedCode: humanized,
            originalScore: data.original_score,
            newScore: data.new_score
          });
        }
      }
    } catch (err) {
      console.warn("Humanize failed from background:", err);
    }
  }
});
