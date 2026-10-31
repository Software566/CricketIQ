"""Application settings."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

PAGE_TITLE = os.getenv("CRICKETIQ_PAGE_TITLE", "CricketIQ")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
