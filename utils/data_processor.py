"""Load bundled sample data."""
import json
from pathlib import Path
from config.settings import DATA_DIR


def load_sample(name):
    path = Path(DATA_DIR) / name
    if not path.is_file():
        raise FileNotFoundError(f"Sample dataset not found: {path}")
    with path.open(encoding="utf-8") as file:
        return json.load(file)
