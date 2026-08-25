// MES Cable — Preload script (chạy trong context cô lập trước khi index.html load).
// Hiện chưa cần expose API nào cho renderer (app chỉ dùng Firebase REST/SDK qua CDN như bản web),
// giữ file này rỗng-an-toàn để electron-builder không cảnh báo thiếu file (đã khai trong
// package.json > build.files) và để sẵn chỗ nếu sau này cần expose thêm API gốc (contextBridge).
window.addEventListener('DOMContentLoaded', () => {
  // no-op — chỗ dự phòng cho contextBridge.exposeInMainWorld(...) nếu cần sau này
});
