# Manager Airdrop

Ứng dụng desktop local (Windows) để quản lý các dự án Airdrop: Main List,
Secondary List, Wallet, Revenue, Dashboard, và tạo prompt Check News.
Xem đầy đủ đặc tả tại [`APP_SPEC.md`](./APP_SPEC.md).

## Công nghệ

- Python 3.10+
- [PyWebView](https://pywebview.flowrl.com/) — cửa sổ desktop nhúng HTML/CSS/JS, không server/API
- SQLite (thư viện chuẩn `sqlite3`) — lưu dữ liệu local

## Cài đặt & chạy

```bash
pip install -r requirements.txt
python main.py
```

Lần chạy đầu tiên sẽ tự tạo database tại `data/manager_airdrop.db`.

## Cấu trúc project

```
Manager-Airdrop/
├── main.py                 # Entry point, khởi tạo PyWebView + DB
├── requirements.txt
├── APP_SPEC.md
├── README.md
├── app_config.json         # Tự tạo khi đổi App Data Path (Settings)
├── app/
│   ├── api.py               # Lớp Api — cầu nối JS ↔ Python (window.pywebview.api)
│   ├── ui/                  # HTML/CSS/JS frontend (PyWebView)
│   ├── services/             # Business logic (project, wallet, revenue, news, chrome, settings)
│   ├── database/             # Kết nối & schema SQLite
│   ├── models/                # Dataclass models: Project, Wallet, Revenue, Settings
│   └── utils/                  # paths.py — quản lý app_config.json / App Data Path
├── assets/
└── data/                    # Vị trí database mặc định
```

## Ghi chú triển khai / Assumptions

Theo Rule "Minimal Change — Maximum Preservation" và "No Unauthorized
Changes", các điểm dưới đây là suy luận hợp lý cho những chi tiết không
được đặc tả tường minh trong `APP_SPEC.md`, được thực hiện với sự cho phép
tiếp tục tự động của người dùng:

1. **`event_date` trên Project** — APP_SPEC mục 11.1 không liệt kê field
   ngày tháng, nhưng mục 5 (Upcoming TGE) hiển thị ví dụ cụ thể có ngày
   ("ABC — TGE ngày 30/08/2026"). Đã thêm field `event_date` (tùy chọn)
   trên Project để lưu ngày này, dùng cho hiển thị Upcoming TGE và làm
   ngày mặc định khi tạo Revenue record.

2. **Đồng bộ Revenue theo Status** — Khi status của project chuyển thành
   `CLAIMED`, một Revenue record được tự động tạo (amount mặc định = 0)
   theo đúng data flow ở mục 9.1/16.3. Người dùng chỉnh sửa amount/date
   trực tiếp trong tab Revenue. Nếu status đổi khỏi `CLAIMED`, record
   Revenue tương ứng bị xóa để tổng doanh thu luôn khớp với danh sách
   project đang ở trạng thái Claimed.

3. **App Data Path** — Vì cấu hình này quyết định database nằm ở đâu, nó
   được lưu trong `app_config.json` ở thư mục gốc project (không lưu
   trong chính SQLite DB). Khi đổi đường dẫn, database cũ được **copy**
   sang vị trí mới (không xóa dữ liệu cũ), đúng nguyên tắc "Preserve
   existing data where possible" (mục 18 — Error State).

4. **Tìm Chrome executable** — App tự dò các đường dẫn cài đặt Chrome phổ
   biến trên Windows, sau đó fallback sang `PATH`. Nếu không tìm thấy,
   hiển thị Error State rõ ràng thay vì lỗi âm thầm.

Không có tính năng nào ngoài phạm vi `APP_SPEC.md` mục 22 (Scope
Limitations) được thêm vào — không scraping, không gọi News/X API, không
tự động claim/TGE, không cloud sync, không đăng nhập.

## Kiểm thử

Business logic (project/wallet/revenue CRUD, đồng bộ revenue theo status,
tạo prompt Check News, quản lý settings) độc lập với lớp UI/PyWebView nên
có thể test trực tiếp bằng Python thuần (xem phần "Final Verification" ở
`APP_SPEC.md` mục 24).
