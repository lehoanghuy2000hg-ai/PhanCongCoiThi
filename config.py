from pathlib import Path

# ===========================
# THƯ MỤC GỐC
# ===========================

BASE_DIR = Path(__file__).resolve().parent

# ===========================
# THƯ MỤC DỮ LIỆU
# ===========================

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
ASSET_DIR = BASE_DIR / "assets"

# ===========================
# FILE DỮ LIỆU
# ===========================

RESULT_FILE = DATA_DIR / "ket_qua.xlsx"

# ===========================
# GIAO DIỆN
# ===========================

APP_TITLE = "HỆ THỐNG TRA CỨU PHÂN CÔNG COI THI"

PAGE_ICON = "📋"

LAYOUT = "wide"

# ===========================
# TẠO THƯ MỤC NẾU CHƯA CÓ
# ===========================

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
ASSET_DIR.mkdir(exist_ok=True)