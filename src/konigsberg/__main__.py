from .app import App


def main() -> None:
    """Điểm vào chương trình khi chạy bằng `python -m konigsberg`.

    Quản lý vòng đời Pygame bằng context manager để đảm bảo giải phóng tài nguyên.
    """
    with App() as app:
        app.run()


if __name__ == "__main__":
    main()


