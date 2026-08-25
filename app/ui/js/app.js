/* ==========================================================================
   Manager Airdrop — frontend application (vanilla JS, no build step).
   Talks to the Python backend exclusively through window.pywebview.api.
   ========================================================================== */

// ---------------------------------------------------------------- API bridge
const api = {
  _ready: null,
  ready() {
    if (this._ready) return this._ready;
    this._ready = new Promise((resolve) => {
      if (window.pywebview && window.pywebview.api) {
        resolve();
      } else {
        window.addEventListener("pywebviewready", () => resolve(), { once: true });
      }
    });
    return this._ready;
  },
  async call(method, ...args) {
    await this.ready();
    return window.pywebview.api[method](...args);
  },
};

// -------------------------------------------------------------------- State
const state = { route: "dashboard" };

const PAGE_TITLES = {
  dashboard: "Dashboard",
  "main-list": "Main List",
  "secondary-list": "Secondary List",
  wallet: "Wallet",
  revenue: "Revenue",
};

// --------------------------------------------------------------- Utilities
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fmtMoney(n) {
  const num = Number(n) || 0;
  return "$" + num.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

function fmtDate(d) {
  if (!d) return "—";
  return d;
}

function statusBadge(status) {
  const map = { TGE: "badge-tge", CLAIMED: "badge-claimed", ONLINE: "badge-online" };
  const cls = map[status] || "badge-online";
  return `<span class="badge ${cls}">${escapeHtml(status)}</span>`;
}

function toast(message, type = "success") {
  const root = document.getElementById("toast-root");
  const el = document.createElement("div");
  el.className = "toast" + (type === "error" ? " error" : "");
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ------------------------------------------------------------------ Router
function navigate(route) {
  state.route = route;
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.route === route);
  });
  document.getElementById("page-title").textContent = PAGE_TITLES[route] || "";
  render();
}

async function render() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading-state">Đang tải…</div>';
  try {
    if (state.route === "dashboard") await renderDashboard(content);
    else if (state.route === "main-list") await renderProjectList(content, "MAIN");
    else if (state.route === "secondary-list") await renderProjectList(content, "SECONDARY");
    else if (state.route === "wallet") await renderWallet(content);
    else if (state.route === "revenue") await renderRevenue(content);
  } catch (err) {
    content.innerHTML = `<div class="error-banner">Đã xảy ra lỗi: ${escapeHtml(err.message || err)}</div>`;
  }
}

// --------------------------------------------------------------- Dashboard
async function renderDashboard(content) {
  const data = await api.call("get_dashboard");

  const tgeRows = data.upcoming_tge.length
    ? data.upcoming_tge
        .map(
          (p) => `
        <div class="tge-row">
          <span class="tge-name">${escapeHtml(p.name)}</span>
          <span class="tge-date">${p.event_date ? "TGE " + escapeHtml(p.event_date) : "TGE — chưa có ngày"}</span>
        </div>`
        )
        .join("")
    : '<div class="tge-empty">Không có dự án nào sắp TGE.</div>';

  content.innerHTML = `
    <div class="dashboard-grid">
      <div class="card">
        <p class="card-title">Revenue Summary</p>
        <div class="revenue-figure">${fmtMoney(data.total_revenue)}</div>
        <div class="revenue-sub">Tổng doanh thu từ các dự án đã Claim</div>
      </div>
      <div class="card check-news-card">
        <p class="card-title">Check News</p>
        <p class="check-news-desc">Tạo prompt kiểm tra tin tức mới nhất cho các dự án bạn chọn.</p>
        <button class="btn btn-primary" id="btn-check-news">🔔 Check News</button>
      </div>
    </div>
    <div class="card">
      <p class="card-title">Upcoming TGE Timeline</p>
      <div class="tge-panel">${tgeRows}</div>
    </div>
  `;

  document.getElementById("btn-check-news").addEventListener("click", openCheckNewsModal);
}

// ------------------------------------------------------------- Project list
async function renderProjectList(content, listType) {
  const projects = await api.call("get_projects", listType);
  const label = listType === "MAIN" ? "Main List" : "Secondary List";

  const rows = projects.length
    ? projects
        .map(
          (p) => `
      <tr data-id="${p.id}">
        <td>
          <button class="play-btn" data-action="open-link" data-id="${p.id}" title="Mở link dự án">▶</button>
        </td>
        <td class="cell-name">${escapeHtml(p.name)}</td>
        <td class="cell-mono">${escapeHtml(p.x_handle || "—")}</td>
        <td>${statusBadge(p.status)}</td>
        <td class="cell-note">${escapeHtml(p.note || "")}</td>
        <td class="cell-actions">
          <button class="btn btn-sm" data-action="edit" data-id="${p.id}">Edit</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${p.id}">Delete</button>
        </td>
      </tr>`
        )
        .join("")
    : "";

  content.innerHTML = `
    <div class="list-toolbar">
      <span class="text-dim">${projects.length} dự án</span>
      <div class="list-toolbar-actions">
        <button class="btn btn-sm" id="btn-export-projects">Export</button>
        <button class="btn btn-sm" id="btn-import-projects">Import</button>
        <button class="btn btn-primary" id="btn-add-project">+ Thêm dự án</button>
      </div>
    </div>
    <div class="table-wrap">
      ${
        projects.length
          ? `<table>
        <thead><tr><th></th><th>Name</th><th>X Handle</th><th>Status</th><th>Note</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`
          : `<div class="empty-state">No projects found.</div>`
      }
    </div>
  `;

  document.getElementById("btn-add-project").addEventListener("click", () => openProjectModal(listType));

  document.getElementById("btn-export-projects").addEventListener("click", async () => {
    const res = await api.call("export_projects", listType);
    if (res.success) toast(`Đã export ${res.count} dự án${res.path ? " tới " + res.path : ""}.`);
    else if (res.error) toast(res.error, "error");
  });

  document.getElementById("btn-import-projects").addEventListener("click", async () => {
    const res = await api.call("import_projects", listType);
    if (res.success) {
      toast(`Đã import ${res.count} dự án.`);
      render();
    } else if (res.error) {
      toast(res.error, "error");
    }
  });

  content.querySelectorAll('[data-action="edit"]').forEach((btn) =>
    btn.addEventListener("click", () => {
      const p = projects.find((x) => x.id == btn.dataset.id);
      openProjectModal(listType, p);
    })
  );

  content.querySelectorAll('[data-action="delete"]').forEach((btn) =>
    btn.addEventListener("click", () => {
      const p = projects.find((x) => x.id == btn.dataset.id);
      confirmDialog(`Xóa dự án "${p.name}"? Hành động này không thể hoàn tác.`, async () => {
        const res = await api.call("delete_project", p.id);
        if (res.success) {
          toast("Đã xóa dự án.");
          render();
        } else {
          toast(res.error || "Xóa thất bại.", "error");
        }
      });
    })
  );

  content.querySelectorAll('[data-action="open-link"]').forEach((btn) =>
    btn.addEventListener("click", async () => {
      const p = projects.find((x) => x.id == btn.dataset.id);
      if (!p.web_link) {
        toast("Dự án chưa có Web Link.", "error");
        return;
      }
      const res = await api.call("open_project_link", p.web_link);
      if (!res.success) toast(res.error || "Không thể mở link.", "error");
    })
  );
}

function openProjectModal(listType, project = null) {
  const isEdit = !!project;
  const p = project || { name: "", web_link: "", x_handle: "", status: "ONLINE", note: "", event_date: "" };

  const body = `
    <div class="form-group">
      <label>Tên dự án *</label>
      <input type="text" id="f-name" value="${escapeHtml(p.name)}" placeholder="VD: ABC Protocol" />
    </div>
    <div class="form-group">
      <label>Web Link</label>
      <input type="text" id="f-web-link" value="${escapeHtml(p.web_link)}" placeholder="https://..." />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>X Handle</label>
        <input type="text" id="f-x-handle" value="${escapeHtml(p.x_handle)}" placeholder="@abc_project" />
      </div>
      <div class="form-group">
        <label>Ngày sự kiện (TGE)</label>
        <input type="date" id="f-event-date" value="${escapeHtml(p.event_date)}" />
      </div>
    </div>
    <div class="form-group">
      <label>Status</label>
      <div class="status-picker" id="status-picker">
        ${["TGE", "CLAIMED", "ONLINE"]
          .map(
            (s) =>
              `<div class="status-option status-${s} ${p.status === s ? "selected" : ""}" data-status="${s}">${s}</div>`
          )
          .join("")}
      </div>
    </div>
    <div class="form-group">
      <label>Note</label>
      <textarea id="f-note">${escapeHtml(p.note)}</textarea>
    </div>
  `;

  const modal = openModal({
    title: isEdit ? "Sửa dự án" : `Thêm dự án — ${listType === "MAIN" ? "Main List" : "Secondary List"}`,
    body,
    footer: `<button class="btn btn-ghost" data-close>Hủy</button>
             <button class="btn btn-primary" id="f-save">${isEdit ? "Lưu" : "Thêm"}</button>`,
  });

  let selectedStatus = p.status;
  modal.querySelectorAll(".status-option").forEach((opt) =>
    opt.addEventListener("click", () => {
      selectedStatus = opt.dataset.status;
      modal.querySelectorAll(".status-option").forEach((o) => o.classList.remove("selected"));
      opt.classList.add("selected");
    })
  );

  modal.querySelector("#f-save").addEventListener("click", async () => {
    const data = {
      name: modal.querySelector("#f-name").value.trim(),
      web_link: modal.querySelector("#f-web-link").value.trim(),
      x_handle: modal.querySelector("#f-x-handle").value.trim(),
      event_date: modal.querySelector("#f-event-date").value,
      status: selectedStatus,
      note: modal.querySelector("#f-note").value.trim(),
    };
    if (!data.name) {
      toast("Tên dự án là bắt buộc.", "error");
      return;
    }
    const res = isEdit
      ? await api.call("update_project", p.id, data)
      : await api.call("create_project", listType, data);
    if (res.success) {
      toast(isEdit ? "Đã cập nhật dự án." : "Đã thêm dự án.");
      closeModal();
      render();
    } else {
      toast(res.error || "Có lỗi xảy ra.", "error");
    }
  });
}

// ------------------------------------------------------------------- Wallet
async function renderWallet(content) {
  const wallets = await api.call("get_wallets");

  const rows = wallets.length
    ? wallets
        .map(
          (w) => `
      <tr data-id="${w.id}">
        <td class="cell-name">${escapeHtml(w.name)}</td>
        <td class="cell-mono">${escapeHtml(w.address)}</td>
        <td class="cell-note">${escapeHtml(w.note || "")}</td>
        <td class="cell-actions">
          <button class="btn btn-sm" data-action="copy" data-id="${w.id}">Copy</button>
          <button class="btn btn-sm" data-action="edit" data-id="${w.id}">Edit</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${w.id}">Delete</button>
        </td>
      </tr>`
        )
        .join("")
    : "";

  content.innerHTML = `
    <div class="list-toolbar">
      <span class="text-dim">${wallets.length} ví</span>
      <button class="btn btn-primary" id="btn-add-wallet">+ Thêm ví</button>
    </div>
    <div class="table-wrap">
      ${
        wallets.length
          ? `<table>
        <thead><tr><th>Name</th><th>Address</th><th>Note</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`
          : `<div class="empty-state">No wallets found.</div>`
      }
    </div>
  `;

  document.getElementById("btn-add-wallet").addEventListener("click", () => openWalletModal());

  content.querySelectorAll('[data-action="copy"]').forEach((btn) =>
    btn.addEventListener("click", async () => {
      const w = wallets.find((x) => x.id == btn.dataset.id);
      const res = await api.call("copy_to_clipboard", w.address);
      if (res.success) toast("Đã copy địa chỉ ví.");
      else toast(res.error || "Copy thất bại.", "error");
    })
  );

  content.querySelectorAll('[data-action="edit"]').forEach((btn) =>
    btn.addEventListener("click", () => {
      const w = wallets.find((x) => x.id == btn.dataset.id);
      openWalletModal(w);
    })
  );

  content.querySelectorAll('[data-action="delete"]').forEach((btn) =>
    btn.addEventListener("click", () => {
      const w = wallets.find((x) => x.id == btn.dataset.id);
      confirmDialog(`Xóa ví "${w.name}"?`, async () => {
        const res = await api.call("delete_wallet", w.id);
        if (res.success) {
          toast("Đã xóa ví.");
          render();
        } else {
          toast(res.error || "Xóa thất bại.", "error");
        }
      });
    })
  );
}

function openWalletModal(wallet = null) {
  const isEdit = !!wallet;
  const w = wallet || { name: "", address: "", note: "" };

  const body = `
    <div class="form-group">
      <label>Tên ví *</label>
      <input type="text" id="f-name" value="${escapeHtml(w.name)}" placeholder="VD: Ví MetaMask #1" />
    </div>
    <div class="form-group">
      <label>Địa chỉ *</label>
      <input type="text" id="f-address" value="${escapeHtml(w.address)}" placeholder="0x..." style="font-family: var(--font-mono);" />
    </div>
    <div class="form-group">
      <label>Note</label>
      <textarea id="f-note">${escapeHtml(w.note)}</textarea>
    </div>
  `;

  const modal = openModal({
    title: isEdit ? "Sửa ví" : "Thêm ví",
    body,
    footer: `<button class="btn btn-ghost" data-close>Hủy</button>
             <button class="btn btn-primary" id="f-save">${isEdit ? "Lưu" : "Thêm"}</button>`,
  });

  modal.querySelector("#f-save").addEventListener("click", async () => {
    const data = {
      name: modal.querySelector("#f-name").value.trim(),
      address: modal.querySelector("#f-address").value.trim(),
      note: modal.querySelector("#f-note").value.trim(),
    };
    if (!data.name || !data.address) {
      toast("Tên ví và Địa chỉ là bắt buộc.", "error");
      return;
    }
    const res = isEdit ? await api.call("update_wallet", w.id, data) : await api.call("create_wallet", data);
    if (res.success) {
      toast(isEdit ? "Đã cập nhật ví." : "Đã thêm ví.");
      closeModal();
      render();
    } else {
      toast(res.error || "Có lỗi xảy ra.", "error");
    }
  });
}

// ------------------------------------------------------------------ Revenue
async function renderRevenue(content) {
  const data = await api.call("get_revenue");

  const rows = data.records.length
    ? data.records
        .map(
          (r) => `
      <tr data-id="${r.id}">
        <td class="cell-name">${escapeHtml(r.project_name)}</td>
        <td class="cell-mono">${fmtMoney(r.amount)}</td>
        <td class="cell-mono">${fmtDate(r.date)}</td>
        <td class="cell-actions">
          <button class="btn btn-sm" data-action="edit" data-id="${r.id}">Edit</button>
        </td>
      </tr>`
        )
        .join("")
    : "";

  content.innerHTML = `
    <div class="table-wrap">
      ${
        data.records.length
          ? `<table>
        <thead><tr><th>Tên dự án</th><th>Doanh thu</th><th>Date</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`
          : `<div class="empty-state">No projects found.</div>`
      }
    </div>
    <div class="card mt-8" style="display:flex; align-items:center; justify-content:space-between;">
      <span class="card-title" style="margin:0;">Tổng</span>
      <span class="revenue-figure" style="font-size:22px;">${fmtMoney(data.total)}</span>
    </div>
  `;

  content.querySelectorAll('[data-action="edit"]').forEach((btn) =>
    btn.addEventListener("click", () => {
      const r = data.records.find((x) => x.id == btn.dataset.id);
      openRevenueModal(r);
    })
  );
}

function openRevenueModal(record) {
  const body = `
    <div class="form-group">
      <label>Dự án</label>
      <input type="text" value="${escapeHtml(record.project_name)}" disabled />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Doanh thu (USD)</label>
        <input type="number" step="0.01" id="f-amount" value="${record.amount}" />
      </div>
      <div class="form-group">
        <label>Date</label>
        <input type="date" id="f-date" value="${escapeHtml(record.date)}" />
      </div>
    </div>
  `;

  const modal = openModal({
    title: "Sửa Revenue",
    body,
    footer: `<button class="btn btn-ghost" data-close>Hủy</button>
             <button class="btn btn-primary" id="f-save">Lưu</button>`,
  });

  modal.querySelector("#f-save").addEventListener("click", async () => {
    const data = {
      amount: modal.querySelector("#f-amount").value,
      date: modal.querySelector("#f-date").value,
    };
    const res = await api.call("update_revenue", record.id, data);
    if (res.success) {
      toast("Đã cập nhật doanh thu.");
      closeModal();
      render();
    } else {
      toast(res.error || "Có lỗi xảy ra.", "error");
    }
  });
}

// --------------------------------------------------------------- Check News
function openCheckNewsModal() {
  const body = `
    <div class="form-group">
      <label>Chọn List</label>
      <div class="scope-options">
        <label class="scope-option"><input type="radio" name="scope" value="MAIN" checked /> Main List</label>
        <label class="scope-option"><input type="radio" name="scope" value="SECONDARY" /> Secondary List</label>
        <label class="scope-option"><input type="radio" name="scope" value="BOTH" /> Cả hai</label>
      </div>
    </div>
    <div class="form-group">
      <label>Check Scope</label>
      <div class="scope-options">
        <label class="scope-option"><input type="radio" name="checkScope" value="NEWS" checked /> Check News (2 day)</label>
        <label class="scope-option"><input type="radio" name="checkScope" value="DEEP" /> Check Deep (10 day and pinned)</label>
      </div>
    </div>
    <button class="btn btn-primary btn-sm" id="btn-generate">Tạo Prompt</button>
    <div id="prompt-output" style="display:none; margin-top:14px;">
      <label class="text-dim" style="font-size:12px;">Prompt</label>
      <div class="prompt-box" id="prompt-text"></div>
      <button class="btn btn-sm mt-8" id="btn-copy-prompt">Copy Prompt</button>
      <label class="text-dim" style="font-size:12px; display:block; margin-top:14px;">Selected Handles</label>
      <div class="handle-list" id="handle-list"></div>
    </div>
  `;

  const modal = openModal({ title: "Check News", body, footer: `<button class="btn btn-ghost" data-close>Đóng</button>`, wide: true });

  let currentPrompt = "";

  modal.querySelector("#btn-generate").addEventListener("click", async () => {
    const scope = modal.querySelector('input[name="scope"]:checked').value;
    const checkScope = modal.querySelector('input[name="checkScope"]:checked').value;
    const res = await api.call("generate_news_prompt", scope, checkScope);
    currentPrompt = res.prompt;
    const output = modal.querySelector("#prompt-output");
    output.style.display = "block";
    modal.querySelector("#prompt-text").textContent = res.prompt || "Không có dự án nào có X Handle trong danh sách đã chọn.";
    modal.querySelector("#handle-list").innerHTML = res.handles.length
      ? res.handles.map((h) => `<span class="handle-chip">${escapeHtml(h)}</span>`).join("")
      : '<span class="text-faint" style="font-size:12px;">—</span>';
  });

  modal.querySelector("#btn-copy-prompt").addEventListener("click", async () => {
    if (!currentPrompt) {
      toast("Chưa có prompt để copy.", "error");
      return;
    }
    const res = await api.call("copy_to_clipboard", currentPrompt);
    if (res.success) toast("Đã copy prompt.");
    else toast(res.error || "Copy thất bại.", "error");
  });
}

// ----------------------------------------------------------------- Settings
async function openSettingsModal() {
  const settings = await api.call("get_settings");

  const body = `
    <div class="form-group">
      <label>App Data Path</label>
      <div style="display:flex; gap:8px;">
        <input type="text" id="f-app-data-path" value="${escapeHtml(settings.app_data_path)}" style="flex:1; font-family: var(--font-mono); font-size:12px;" />
        <button class="btn btn-sm" id="btn-browse-data">Browse</button>
      </div>
      <div class="form-hint">Nơi lưu database SQLite của ứng dụng. Dữ liệu cũ sẽ được sao chép tự động sang vị trí mới.</div>
    </div>
    <div class="form-group">
      <label>Chrome User Data Path</label>
      <div style="display:flex; gap:8px;">
        <input type="text" id="f-chrome-path" value="${escapeHtml(settings.chrome_user_data_path)}" placeholder="C:\\Users\\...\\Chrome\\User Data" style="flex:1; font-family: var(--font-mono); font-size:12px;" />
        <button class="btn btn-sm" id="btn-browse-chrome">Browse</button>
      </div>
    </div>
    <div class="form-group">
      <label>Chrome Profile</label>
      <input type="text" id="f-chrome-profile" value="${escapeHtml(settings.chrome_profile_name)}" placeholder="Profile 1" />
      <div class="form-hint">Dùng khi mở Web Link của dự án (nút ▶).</div>
    </div>
  `;

  const modal = openModal({
    title: "Settings",
    body,
    footer: `<button class="btn btn-ghost" data-close>Đóng</button>
             <button class="btn btn-primary" id="f-save">Lưu</button>`,
  });

  modal.querySelector("#btn-browse-data").addEventListener("click", async () => {
    const res = await api.call("browse_folder");
    if (res.success) modal.querySelector("#f-app-data-path").value = res.path;
  });
  modal.querySelector("#btn-browse-chrome").addEventListener("click", async () => {
    const res = await api.call("browse_folder");
    if (res.success) modal.querySelector("#f-chrome-path").value = res.path;
  });

  modal.querySelector("#f-save").addEventListener("click", async () => {
    const newDataPath = modal.querySelector("#f-app-data-path").value.trim();
    const chromePath = modal.querySelector("#f-chrome-path").value.trim();
    const chromeProfile = modal.querySelector("#f-chrome-profile").value.trim();

    if (newDataPath !== settings.app_data_path) {
      const r1 = await api.call("update_app_data_path", newDataPath);
      if (!r1.success) {
        toast(r1.error || "Không thể cập nhật App Data Path.", "error");
        return;
      }
    }
    const r2 = await api.call("update_chrome_settings", chromePath, chromeProfile);
    if (!r2.success) {
      toast(r2.error || "Không thể lưu Chrome settings.", "error");
      return;
    }
    toast("Đã lưu Settings.");
    closeModal();
    render();
  });
}

// -------------------------------------------------------------- Modal utils
function openModal({ title, body, footer, wide = false }) {
  closeModal();
  const root = document.getElementById("modal-root");
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal ${wide ? "modal-wide" : ""}">
      <div class="modal-header">
        <h2>${escapeHtml(title)}</h2>
        <button class="modal-close" data-close>✕</button>
      </div>
      <div class="modal-body">${body}</div>
      <div class="modal-footer">${footer}</div>
    </div>
  `;
  root.appendChild(overlay);

  overlay.querySelectorAll("[data-close]").forEach((el) => el.addEventListener("click", closeModal));
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  return overlay;
}

function closeModal() {
  const root = document.getElementById("modal-root");
  root.innerHTML = "";
}

function confirmDialog(message, onConfirm) {
  const modal = openModal({
    title: "Xác nhận",
    body: `<p class="text-dim" style="margin:0;">${escapeHtml(message)}</p>`,
    footer: `<button class="btn btn-ghost" data-close>Hủy</button>
             <button class="btn btn-danger" id="btn-confirm-yes">Xóa</button>`,
  });
  modal.querySelector("#btn-confirm-yes").addEventListener("click", async () => {
    closeModal();
    await onConfirm();
  });
}

// ------------------------------------------------------------------- Init
function init() {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => navigate(btn.dataset.route));
  });
  document.getElementById("btn-settings").addEventListener("click", openSettingsModal);
  navigate("dashboard");
}

document.addEventListener("DOMContentLoaded", init);
