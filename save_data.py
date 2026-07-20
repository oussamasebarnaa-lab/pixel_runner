

import json
import os
from constants import SAVE_FILE


DEFAULT_DATA: dict = {
    "high_score":           0,
    "total_coins":          0,
    "unlocked_characters":  ["default"],
    "selected_character":   "default",
}


def load_save_data() -> dict:
   
    if not os.path.exists(SAVE_FILE):
        return DEFAULT_DATA.copy()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        
        for key, default_value in DEFAULT_DATA.items():
            data.setdefault(key, default_value)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[SaveData] Could not read save file ({exc}). Using defaults.")
        return DEFAULT_DATA.copy()


def write_save_data(data: dict) -> None:
    
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except OSError as exc:
        print(f"[SaveData] Could not write save file: {exc}")
