(() => {
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "CODESHIELD_ALERT") {
      showFloatingToast(request.message);
    } else if (request.type === "CODESHIELD_HUMANIZED_RESULT") {
      showHumanizedModal(request.humanizedCode, request.originalScore, request.newScore);
    }
  });

  function showFloatingToast(msg) {
    const toast = document.createElement("div");
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #0f111a;
      border: 1px solid #00f0ff;
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
      color: #f1f5f9;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
      font-size: 13px;
      padding: 12px 18px;
      border-radius: 8px;
      z-index: 99999999;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: codeshieldFadeIn 0.3s ease;
    `;
    toast.innerHTML = `<span>${msg}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.5s ease";
      setTimeout(() => toast.remove(), 500);
    }, 4500);
  }

  function showHumanizedModal(code, origScore, newScore) {
    const card = document.createElement("div");
    card.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 380px;
      background: #08090d;
      border: 1px solid #34d399;
      box-shadow: 0 0 25px rgba(52, 211, 153, 0.4);
      color: #f1f5f9;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 14px;
      border-radius: 10px;
      z-index: 99999999;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size: 13px; font-weight: 800; color: #34d399;">⚡ CodeShield AI Humanized</span>
        <span style="font-size: 11px; font-weight: 700; color: #10b981; background: rgba(52,211,153,0.15); padding: 2px 6px; border-radius: 4px;">
          ${origScore || 96}% ➔ ${newScore || 14}%
        </span>
      </div>
      <pre style="background: #0f111a; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 8px; font-family: monospace; font-size: 11px; max-height: 120px; overflow: auto; color: #6ee7b7; white-space: pre-wrap;">${escapeHtml(code)}</pre>
      <div style="display:flex; justify-content:flex-end; gap: 8px;">
        <button id="cs-copy-btn" style="background: #10b981; color: #000; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer;">📋 Copy Code</button>
        <button id="cs-close-btn" style="background: rgba(255,255,255,0.1); color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;">Close</button>
      </div>
    `;

    document.body.appendChild(card);

    card.querySelector("#cs-copy-btn").addEventListener("click", () => {
      navigator.clipboard.writeText(code).then(() => {
        const btn = card.querySelector("#cs-copy-btn");
        btn.textContent = "✓ Copied!";
        setTimeout(() => card.remove(), 1200);
      });
    });

    card.querySelector("#cs-close-btn").addEventListener("click", () => card.remove());
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
})();
