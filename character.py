from constants import NEON_BLUE, NEON_CYAN, NEON_PINK, GOLD, SILVER, BLACK


CHARACTERS: dict[str, dict] = {
    "default": {
        "name":         "Default Skater",
        "cost":         0,
        "body_color":   NEON_BLUE,
        "accent_color": GOLD,
        "head_color":   (220, 195, 155),      
        "description":  "The original runner. Fast and fearless.",
        "sprite_path":  "assets/image.png",
       
    },
    "ninja": {
        "name":         "Ninja",
        "cost":         1_000,
        "body_color":   (22, 18, 30),         
        "accent_color": NEON_PINK,
        "head_color":   (18, 14, 26),
        "description":  "Silent and deadly. Master of evasion.",
        "sprite_path":  None,
        
    },
    "robot": {
        "name":         "Robot MK-7",
        "cost":         5_000,
        "body_color":   SILVER,
        "accent_color": NEON_CYAN,
        "head_color":   (165, 165, 185),      
        "description":  "Titanium chassis. Built for maximum velocity.",
        "sprite_path":  None,
    },
}

CHARACTER_ORDER: list[str] = ["default", "ninja", "robot"]



def get_character(char_id: str) -> dict:
    return CHARACTERS.get(char_id, CHARACTERS["default"])


def is_unlocked(char_id: str, save_data: dict) -> bool:

    return char_id in save_data.get("unlocked_characters", [])


def can_afford(char_id: str, save_data: dict) -> bool:

    return save_data.get("total_coins", 0) >= CHARACTERS[char_id]["cost"]


def purchase_character(char_id: str, save_data: dict) -> bool:

    if is_unlocked(char_id, save_data):
        return False   
    if not can_afford(char_id, save_data):
        return False   
    save_data["total_coins"]          -= CHARACTERS[char_id]["cost"]
    save_data["unlocked_characters"].append(char_id)
    return True
