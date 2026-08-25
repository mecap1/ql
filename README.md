# MES Cable — Web App

Bản chuyển thể từ project **MES_CABLE** (Python/Streamlit + SQLAlchemy) sang **web app tĩnh 1 file** (`index.html`), dùng **Firebase Realtime Database** làm nơi lưu dữ liệu — theo đúng mô hình app "Quản Lý SX Đông Phương" đã dùng trước đây.

## Đã chuyển (bản v1.1)
- **Đăng nhập / phân quyền** (admin, quan_ly, thong_ke, van_hanh) — tài khoản mặc định `admin` / `admin123`
- **Master Data** (11 danh mục): Đơn vị tính, Nhà cung cấp, Khách hàng, Công đoạn, Ca, Màu, Máy, Công nhân, Vật tư, Kho, Sản phẩm
- **BOM**: theo Sản phẩm → Phiên bản (Revision) → Chi tiết định mức theo từng công đoạn (NVL hoặc BTP)
- **Routing**: theo Sản phẩm → Phiên bản Routing → các bước (Operation) theo thứ tự, đánh dấu bước bắt buộc
- **PO / LSX**: Đơn hàng sản xuất (gán cố định 1 phiên bản BOM + 1 phiên bản Routing), mỗi PO tách nhiều Lệnh sản xuất theo công đoạn
- **Báo công sản xuất**: ghi nhận sản lượng/phế theo LSX real-time, tự quy đổi kg↔mét theo hệ số suy từ BOM, kiểm tra "hard sequence-lock" (chặn nếu công đoạn trước bắt buộc chưa có sản lượng), tuỳ chọn tự động trừ NVL và tự động tiêu thụ BTP theo hệ số K
- **Kho**: sổ nhật ký giao dịch (Nhập/Xuất/Chuyển kho/Điều chỉnh/Tồn đầu kỳ) + bảng tồn kho tính realtime từ sổ nhật ký
- **WIP**: tự tính sản lượng "đang chờ" giữa 2 công đoạn liền kề (từ Routing + Báo công), có tổng quan điểm nghẽn (bottleneck) trên tất cả PO
- **Hệ số K**: bảng hệ số K giữa các công đoạn (lấy từ dòng BTP trong BOM) + tồn BTP thực tế theo từng LSX/PO
- **Báo cáo**: KPI tổng quan, tiến độ theo LSX, hiệu suất NVL, phân tích phế theo lý do — xem trực tiếp trên web, xuất Excel (nhiều sheet, dùng SheetJS) hoặc in/PDF (dùng khung in của trình duyệt)
- **Tích hợp ERP**: vì là web app tĩnh (không có server FastAPI riêng như bản Python), tích hợp thực hiện qua REST API có sẵn của Firebase Realtime Database — trang này liệt kê endpoint tương ứng cho từng chiều dữ liệu (ERP→MES, MES→ERP) và cho phép lưu ghi chú API Key/Secret

## Khác biệt kiến trúc so với bản Python
- Không còn API server FastAPI (`api.py`) riêng — ERP gọi thẳng Firebase REST API, bảo mật bằng Firebase Database Rules thay vì header `X-API-Key`.
- Không xuất PDF bằng fpdf2 — dùng khung in của trình duyệt (`Ctrl+P` → Lưu thành PDF) cho phần Báo cáo.
- Mật khẩu băm bằng SHA-256 (Web Crypto API) thay vì bcrypt, vì không có backend riêng để giữ bí mật salt/rounds an toàn hơn.

## Cài đặt lần đầu

Có 2 cách dùng:

**Cách 1 — Firebase (khuyến nghị nếu nhiều người/nhiều thiết bị cùng dùng):**
1. Tạo project Firebase tại https://console.firebase.google.com, bật **Realtime Database**.
2. Mở `index.html` → nhập **Database URL** (dạng `https://xxx-default-rtdb.<region>.firebasedatabase.app`) → Lưu & Tiếp tục.

**Cách 2 — Lưu cục bộ (không cần Firebase, chỉ dùng trên 1 máy):**
- Ở màn hình thiết lập, bấm **"Bỏ qua — lưu cục bộ"**. Dữ liệu được lưu trong `localStorage` của trình duyệt/máy hiện tại — không đồng bộ giữa các thiết bị, và sẽ mất nếu người dùng xoá dữ liệu trình duyệt. Phù hợp để dùng thử hoặc chạy 1 máy duy nhất. Có thể đổi lại sang Firebase bất cứ lúc nào qua link "Đổi cách lưu trữ dữ liệu" ở màn đăng nhập (dữ liệu cũ của chế độ đang dùng vẫn được giữ nguyên, không tự động di chuyển sang chế độ mới).

Sau khi kết nối (Firebase hoặc cục bộ), đăng nhập bằng `admin` / `admin123`, rồi vào **Người dùng** để đổi mật khẩu và tạo tài khoản cho từng người.

## Cấu trúc thư mục

```
index.html            # Toàn bộ app web (SPA, Firebase RTDB)
manifest.json          # PWA manifest
sw.js                   # Service worker (cache offline + banner cập nhật)
version.json            # Số phiên bản hiện tại — banner "Có bản cập nhật" so sánh với APP_VERSION trong index.html
electron-app/            # Wrapper Electron để đóng gói bản Desktop (Windows)
  main.js                  # Entry point Electron — mở web/index.html trong 1 cửa sổ
  preload.js               # Preload script (contextIsolation) — hiện chưa expose API gì
  build/icon.ico           # Icon .exe (đa kích thước, sinh từ icon_src/gen_icon.py)
android-app/              # Wrapper Capacitor để đóng gói bản Android APK
  resources/icon.png       # Icon nguồn 1024×1024 cho @capacitor/assets
  resources/splash.png     # Splash screen nguồn cho @capacitor/assets
icon_src/gen_icon.py      # Script sinh toàn bộ icon (PWA + .ico + Android) từ 1 nguồn thống nhất
.github/workflows/         # GitHub Actions: build & publish Desktop/Android khi tạo tag
```

## Phát hành bản Desktop / Android

- Tạo tag `desktop-v1.0.0` → workflow build Windows Setup.exe, đăng lên GitHub Release.
- Tạo tag `android-v1.0.0` → workflow build APK, đăng lên GitHub Release.
- Hoặc chạy tay: mở tab **Actions** trên GitHub → chọn workflow "Build Android APK" / "Build Desktop (Windows)" → **Run workflow** (không cần tạo tag; bản build chỉ tải về từ Artifacts, không đăng Release).
- Muốn app trên máy tự báo có bản mới: tăng `version` trong `version.json` và tăng `APP_VERSION` trong `index.html` mỗi lần phát hành.
- Icon app (desktop + Android + PWA) lấy từ `icon_src/gen_icon.py` (nguồn `android-app/resources/icon.png` 1024×1024) — đổi icon thì sửa script này rồi chạy lại `python3 icon_src/gen_icon.py`, hoặc thay trực tiếp `android-app/resources/icon.png` + `android-app/resources/splash.png` bằng ảnh của bạn (không cần chạy script).
- APK phát hành hiện là **bản debug** (không cần khai báo keystore/secrets trên GitHub) — cài trực tiếp (sideload) được ngay, nhưng **không dùng để đăng Google Play** (Play yêu cầu bản release đã ký bằng keystore riêng + AAB). Cần bản release thật thì báo lại, sẽ bổ sung bước tạo keystore + ký bằng GitHub Secrets.
- Build Android dùng JDK 17 (khớp khuyến nghị của Capacitor 6 / Android Gradle Plugin hiện tại).

## Bảo mật cần lưu ý

- Mật khẩu người dùng hiện băm bằng SHA-256 phía client (không dùng bcrypt như bản Python) vì đây là web app tĩnh không có backend riêng — nên thiết lập **Firebase Realtime Database Rules** chặt chẽ (chỉ cho user đã đăng nhập Firebase Auth mới đọc/ghi, hoặc giới hạn theo IP nội bộ) trước khi dùng dữ liệu thật.
- Không commit thông số Firebase thật (API key, Database URL) vào các file public nếu dự án dùng rule mở — nên bật rule yêu cầu xác thực.
