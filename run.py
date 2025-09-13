import os
import sys


def main() -> None:
    # Thêm thư mục src vào sys.path để có thể import gói konigsberg
    project_root = os.path.dirname(__file__)
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from konigsberg.__main__ import main as app_main  # noqa: WPS433 - import nội bộ theo runtime

    app_main()


if __name__ == "__main__":
    main()
    

