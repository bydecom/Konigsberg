# Königsberg Graph - Pygame UI (vi)

Dự án Python tối giản để khởi tạo UI Pygame với 1 màn hình chính và 1 màn hình phụ bên trong. Phần này phục vụ nền tảng cho mô phỏng Bảy cây cầu ở Königsberg.

## Chạy dự án

1. Tạo virtualenv (khuyến nghị)
2. Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
# cách 1
python -m konigsberg

# cách 2
python run.py
```

## Cấu trúc

- `src/konigsberg/app.py`: Lớp `App` quản lý vòng đời Pygame và vòng lặp game
- `src/konigsberg/screens/`: Các màn hình `MainScreen` và `SubScreen`
- `src/konigsberg/__main__.py`: Điểm vào khi chạy bằng module

Nhấn phím `ESC` để thoát.

## Ghi chú quản lý tài nguyên

- Khởi tạo/hủy Pygame qua context manager: `with App() as app: app.run()`
- Tách màn hình thành lớp, không giữ `Surface` toàn cục; truyền `surface` cho hàm `draw`
- Giới hạn FPS bằng `Clock.tick(60)` để ổn định CPU
