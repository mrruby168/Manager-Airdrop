# APP_SPEC.md

# Manager Airdrop — Application Specification

## 1. APP OVERVIEW

### 1.1 App Name

**Manager Airdrop**

### 1.2 App Goal

Ứng dụng desktop local dùng để quản lý các dự án Airdrop, theo dõi trạng thái dự án, ví, doanh thu và TGE.

Ứng dụng tập trung vào:

- Quản lý Main List.
- Quản lý Secondary List.
- Quản lý Wallet.
- Theo dõi Revenue.
- Tổng hợp thông tin quan trọng trên Dashboard.
- Tạo prompt kiểm tra News cho các dự án được chọn.
- Mở link dự án bằng Chrome Profile mặc định.

### 1.3 Target Platform

- Windows Desktop
- Local application
- Không yêu cầu server riêng.

### 1.4 Technology

- Python
- PyWebView
- SQLite
- Local Desktop

### 1.5 Technology Restrictions

Không sử dụng:

- HTTP API
- FastAPI
- Flask
- Backend server
- Database server
- Hệ thống lưu trữ online bắt buộc

Dữ liệu được lưu trữ local bằng SQLite.

---

# 2. APPLICATION STRUCTURE

Ứng dụng gồm các khu vực chính:

1. Dashboard
2. Main List
3. Secondary List
4. Wallet
5. Revenue
6. Settings

Navigation chính nằm ở sidebar bên trái.

---

# 3. UI/UX SPECIFICATION

## 3.1 Main Layout

Layout tổng thể:

```text
+-----------------------------------------------------------------------------------+
| Manager Airdrop      | Dashboard                              [⚙ Settings]        |
|                      +------------------------------------------------------------+
| [■] Dashboard        |                                                            |
| [≡] Main List        |              Main Content Area                             |
| [≡] Secondary List   |                                                            |
| [👝] Wallet          |                                                            |
| [📈] Revenue         |                                                            |
|                      |                                                            |
+-----------------------------------------------------------------------------------+
```

### Sidebar

Các navigation item:

- Dashboard
- Main List
- Secondary List
- Wallet
- Revenue

Settings được đặt ở khu vực header.

---

# 4. DASHBOARD

## 4.1 Revenue Summary

Dashboard hiển thị tổng doanh thu.

Nguồn dữ liệu:

```text
Revenue
   ↓
SUM(all revenue)
   ↓
Dashboard
```

Ví dụ:

```text
Doanh số: $100
```

Đơn vị mặc định: **USD**.

---

## 4.2 Check News

Dashboard có nút:

```text
[ 🔔 Check News ]
```

### User Flow

```text
Click Check News
↓
Mở dialog Check News
↓
Chọn danh sách cần kiểm tra
↓
Main List / Secondary List / Cả hai
↓
Tạo Prompt
↓
Hiển thị Prompt
↓
Hiển thị danh sách X Handle
↓
Copy Prompt
```

### Selection

User có thể chọn:

- Main List
- Secondary List
- Main + Secondary

### Prompt Logic

Prompt phải yêu cầu kiểm tra các bài viết trong **2 ngày gần nhất**.

Mục tiêu:

- Quét thông tin mới.
- Xác định thông tin quan trọng liên quan đến dự án.
- Tập trung vào các sự kiện như:
  - TGE
  - Snapshot
  - Mint
  - Claim
  - End
  - Deadline
  - Các thông tin quan trọng khác liên quan trực tiếp đến Airdrop.

### Output Requirement

Báo cáo phải ngắn gọn.

Ví dụ:

```text
ABC — TGE ngày 10/01/2026.
```

Không yêu cầu tạo báo cáo dài.

### Prompt UI

Dialog phải có:

```text
[ Chọn List ]

☐ Main List
☐ Secondary List
☐ Cả hai

[ Prompt ]

........................................
........................................

[ Copy Prompt ]

Selected Handles:
@abc
@projectxyz
@anotherproject
```

Danh sách handle phải lấy từ các project được tích chọn.

---

# 5. UPCOMING TGE

Dashboard có khu vực:

```text
Upcoming TGE Timeline
```

### Data Source

Lấy dữ liệu từ:

- Main List
- Secondary List

Điều kiện:

```text
status = TGE
```

### Display

Ví dụ:

```text
Upcoming TGE Timeline

• ABC — TGE ngày 30/08/2026
• XYZ — TGE ngày 02/09/2026
• Project A — TGE ngày 05/09/2026
```

### Multiple Items

Nếu có nhiều project:

- Khung có kích thước cố định.
- Nội dung bên trong có scroll.
- Không làm Dashboard tăng chiều cao không kiểm soát.

### Data Flow

```text
Main List ─────┐
               ├──> Filter status = TGE ──> Upcoming TGE
Secondary List ┘
```

---

# 6. MAIN LIST

Main List quản lý các dự án chính.

## 6.1 Project Fields

Mỗi project gồm:

| Field | Description |
|---|---|
| Name | Tên dự án |
| Web Link | Link website/project |
| X Handle | Handle X của dự án |
| Status | Trạng thái dự án |
| Note | Ghi chú |

## 6.2 Web Link

Web Link không cần hiển thị URL dài.

UI hiển thị dưới dạng nút Play/Triangle:

```text
▶
```

Khi click:

```text
Click ▶
↓
Lấy Web Link
↓
Lấy Chrome Profile mặc định từ Settings
↓
Mở link bằng Chrome Profile
```

Ứng dụng không tự quản lý nội dung website.

---

## 6.3 X Handle

Lưu handle của dự án.

Ví dụ:

```text
@ABC_Project
```

Handle được sử dụng cho Check News Prompt.

---

## 6.4 Status

Các status được hỗ trợ:

### TGE

Hiển thị màu đỏ.

```text
TGE
```

### CLAIMED

Hiển thị màu xanh lá.

```text
CLAIMED
```

### ONLINE

Hiển thị trạng thái Online.

```text
ONLINE
```

Status là dữ liệu quan trọng để Dashboard và Revenue lấy dữ liệu.

---

## 6.5 Note

Cho phép lưu ghi chú tùy ý cho project.

---

## 6.6 CRUD

Main List phải hỗ trợ:

- Create project
- Read project
- Update project
- Delete project

Không giới hạn việc thêm/sửa/xóa theo yêu cầu hiện tại.

---

# 7. SECONDARY LIST

Secondary List có cấu trúc và chức năng tương tự Main List.

## 7.1 Fields

- Name
- Web Link
- X Handle
- Status
- Note

## 7.2 Status

- TGE
- CLAIMED
- ONLINE

## 7.3 Web Link

Sử dụng nút Play:

```text
▶
```

Link được mở bằng Chrome Profile mặc định đã lưu trong Settings.

## 7.4 CRUD

Secondary List hỗ trợ:

- Create
- Read
- Update
- Delete

---

# 8. WALLET

Wallet quản lý thông tin ví local.

## 8.1 Fields

| Field | Description |
|---|---|
| Name | Tên ví |
| Address | Địa chỉ ví |
| Note | Ghi chú |

## 8.2 Address Copy

Bên cạnh địa chỉ có nút:

```text
[ Copy ]
```

Khi click:

```text
Wallet Address
↓
Copy to Clipboard
```

## 8.3 CRUD

Wallet hỗ trợ:

- Create
- Read
- Update
- Delete

---

# 9. REVENUE

Revenue quản lý doanh thu của các dự án đã Claim.

## 9.1 Automatic Status Flow

Khi project có:

```text
status = CLAIMED
```

project được đưa vào Revenue List.

Data flow:

```text
Main List ───────┐
                 ├──> status = CLAIMED ──> Revenue
Secondary List ──┘
```

## 9.2 Revenue Fields

Revenue UI gồm:

| Field | Description |
|---|---|
| Project Name | Tên dự án |
| Revenue | Doanh thu |
| Date | Ngày ghi nhận |

Ví dụ:

```text
| Tên dự án | Doanh thu | Date |
| ABC       | $100      | 30/08/2026 |
```

## 9.3 Total Revenue

Cuối Revenue List có:

```text
Tổng: $100
```

Tổng được tính từ toàn bộ revenue records.

Dashboard sử dụng cùng tổng này.

Data flow:

```text
Revenue Records
      ↓
SUM(Revenue)
      ↓
Total Revenue
      ↓
Dashboard
```

---

# 10. SETTINGS

Settings được mở từ:

```text
[⚙ Settings]
```

## 10.1 App Data Path

User có thể thiết lập đường dẫn lưu dữ liệu ứng dụng.

Ví dụ:

```text
App Data Path:
[C:\...\Manager Airdrop] [Browse]
```

Database/configuration phải sử dụng đường dẫn dữ liệu đã cấu hình.

## 10.2 Chrome Profile

User có thể thiết lập Chrome Profile mặc định dùng để mở link dự án.

Thông tin cần lưu:

- Chrome User Data Path
- Profile Name

Ví dụ:

```text
Chrome User Data:
[C:\Users\...\Chrome\User Data]

Profile:
[Profile 1]
```

Khi mở Web Link:

```text
Stored Chrome User Data Path
+
Stored Profile Name
+
Project Web Link
↓
Launch Chrome
```

Ứng dụng không tự ý thay đổi Chrome Profile của user.

---

# 11. DATABASE

Database sử dụng:

**SQLite**

Database được lưu local.

## 11.1 Project Data

Main List và Secondary List cần được phân biệt bằng loại list.

Logical structure:

```text
Projects
├── Main
└── Secondary
```

Các trường chính:

```text
id
name
web_link
x_handle
status
note
list_type
created_at
updated_at
```

`list_type` xác định project thuộc:

```text
MAIN
SECONDARY
```

---

# 12. WALLET TABLE

Logical fields:

```text
id
name
address
note
created_at
updated_at
```

---

# 13. REVENUE TABLE

Logical fields:

```text
id
project_id
project_name
amount
date
created_at
updated_at
```

Revenue phải liên kết được với project tương ứng.

---

# 14. SETTINGS DATA

Settings phải lưu local các cấu hình:

```text
app_data_path
chrome_user_data_path
chrome_profile_name
```

---

# 15. STATUS MODEL

Project status chỉ gồm:

```text
TGE
CLAIMED
ONLINE
```

Status được sử dụng bởi các chức năng khác.

### TGE

```text
Project
↓
status = TGE
↓
Dashboard Upcoming TGE
```

### CLAIMED

```text
Project
↓
status = CLAIMED
↓
Revenue
↓
Total Revenue
↓
Dashboard
```

### ONLINE

Project vẫn nằm trong Main/Secondary List nhưng không xuất hiện trong Upcoming TGE hoặc Revenue theo các điều kiện trên.

---

# 16. DATA FLOW

## 16.1 Dashboard Revenue

```text
Revenue
↓
SUM(amount)
↓
Dashboard Revenue Summary
```

## 16.2 Dashboard TGE

```text
Main List
     ↓
Filter TGE
     ↓
     ├──────┐
            ├──> Upcoming TGE
     ┌──────┘
Secondary List
     ↓
Filter TGE
```

## 16.3 Revenue

```text
Main / Secondary
       ↓
status = CLAIMED
       ↓
Revenue
```

## 16.4 Check News

```text
Main / Secondary
       ↓
User selects list
       ↓
Get selected projects
       ↓
Get X Handles
       ↓
Generate Prompt
       ↓
Copy Prompt
```

## 16.5 Project Link

```text
Project Web Link
       ↓
Chrome Settings
       ↓
User Data Path + Profile Name
       ↓
Chrome
       ↓
Open Project Link
```

---

# 17. USER FLOWS

## 17.1 Add Project

```text
User clicks Add
→ Project Form opens
→ User enters data
→ Save
→ SQLite
→ Project appears in selected list
```

## 17.2 Edit Project

```text
User clicks Edit
→ Existing data loaded
→ User modifies data
→ Save
→ SQLite updated
→ List refreshed
```

## 17.3 Delete Project

```text
User clicks Delete
→ Confirmation dialog
→ Confirm
→ Project removed
→ List refreshed
```

## 17.4 Add Wallet

```text
User clicks Add Wallet
→ Wallet Form
→ Enter Name / Address / Note
→ Save
→ SQLite
→ Wallet List updated
```

## 17.5 Copy Wallet Address

```text
Click Copy
→ Address copied to clipboard
```

## 17.6 Check News

```text
Click Check News
→ Select Main / Secondary / Both
→ Generate Prompt
→ Display Prompt
→ Display selected X Handles
→ Click Copy Prompt
→ Prompt copied
```

## 17.7 Open Project Website

```text
Click ▶
→ Read Project Web Link
→ Read Chrome Settings
→ Launch Chrome with configured Profile
→ Open Web Link
```

---

# 18. UI STATES

The application should handle at minimum:

### Empty State

When a list has no records:

```text
No projects found.
```

### Loading State

Used when an operation requires processing before displaying results.

### Success State

After successful:

- Create
- Update
- Delete
- Copy
- Save Settings

The UI should provide clear feedback.

### Error State

If an operation fails:

- Do not silently ignore the error.
- Display a clear error message.
- Preserve existing data where possible.

---

# 19. PROJECT STRUCTURE

Recommended logical structure:

```text
Manager-Airdrop/
│
├── main.py
├── requirements.txt
├── APP_SPEC.md
├── README.md
│
├── app/
│   ├── ui/
│   ├── services/
│   ├── database/
│   ├── models/
│   └── utils/
│
├── assets/
│
└── data/
```

### Responsibilities

#### `main.py`

Application entry point.

Responsible for:

- Starting Python application.
- Initializing PyWebView.
- Loading application UI.
- Connecting application components.

#### `app/ui/`

UI-related components.

#### `app/services/`

Application logic such as:

- Project management
- News prompt generation
- Chrome launcher
- Revenue calculation
- Settings management

#### `app/database/`

SQLite database:

- Connection
- Initialization
- Queries
- CRUD operations
- Migrations if required

#### `app/models/`

Data models for:

- Project
- Wallet
- Revenue
- Settings

#### `app/utils/`

Shared utilities.

#### `assets/`

Application assets.

---

# 20. ARCHITECTURE

Application architecture:

```text
┌──────────────────────────────┐
│          PyWebView UI        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Application Logic       │
├──────────────────────────────┤
│ Project Service              │
│ Wallet Service               │
│ Revenue Service              │
│ News Prompt Service          │
│ Chrome Service               │
│ Settings Service             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          SQLite DB           │
└──────────────────────────────┘
```

All application data remains local.

---

# 21. REQUIREMENTS

The implementation must satisfy all confirmed requirements:

1. Python + PyWebView + SQLite.
2. Local Desktop application.
3. No HTTP API/server.
4. Dashboard.
5. Main List.
6. Secondary List.
7. Wallet.
8. Revenue.
9. Settings.
10. Main/Secondary project CRUD.
11. Wallet CRUD.
12. Project status: TGE / CLAIMED / ONLINE.
13. TGE projects appear on Dashboard.
14. Claimed projects feed Revenue.
15. Revenue total appears on Dashboard.
16. Project website opens through configured Chrome Profile.
17. Check News supports Main / Secondary / Both.
18. Check News generates a short news-analysis prompt.
19. Prompt focuses on the previous two days.
20. Prompt checks important events including TGE, Snapshot, Mint, End and Claim.
21. Selected project X Handles appear below the prompt.
22. Copy Prompt button is required.
23. Upcoming TGE has fixed-size scrolling when many projects exist.
24. Settings stores App Data Path.
25. Settings stores Chrome User Data Path and Profile Name.
26. Data is stored locally.
27. No unauthorized features are added.

---

# 22. SCOPE LIMITATIONS

The following are explicitly outside the current specification unless separately requested:

- Automatic web scraping.
- Automatic X/Twitter API integration.
- Automatic News API integration.
- Automatic claim execution.
- Automatic TGE execution.
- Wallet transaction signing.
- Cloud synchronization.
- Multi-user accounts.
- Remote database.
- HTTP API.
- Authentication system.
- Unrequested analytics.
- Unrequested notification systems.

The Check News feature only defines **prompt generation** based on selected projects and their X Handles. It does not authorize automatic news scraping or external API integration.

---

# 23. SOURCE OF TRUTH

Implementation priority:

```text
USER REQUIREMENTS
        ↓
APP_SPEC.md
        ↓
CODE
```

If implementation differs from this specification, the difference must be analyzed before making changes.

No feature, architecture, database structure, technology, or UI behavior outside this specification may be added without authorization.

---

# 24. FINAL VERIFICATION REQUIREMENTS

Before the application is considered complete, verify:

```text
UI
↓
Navigation
↓
User Flow
↓
Application Logic
↓
SQLite
↓
CRUD
↓
Dashboard Data
↓
TGE Data
↓
Revenue Data
↓
Settings
↓
Chrome Profile Launch
```

All confirmed requirements must work consistently with the defined data flow.