# assets/

This folder is where your real sprite assets should live once you have them.

## Recommended file names

| Character / Object | Suggested filename   |
|--------------------|----------------------|
| Default Skater     | `skater.png`         |
| Ninja              | `ninja.png`          |
| Robot MK-7         | `robot.png`          |
| Barrier obstacle   | `barrier.png`        |
| Sign obstacle      | `sign.png`           |
| Train obstacle     | `train.png`          |
| Coin               | `coin.png`           |
| Window icon        | `icon.png`           |

## How to swap in sprites

### Characters (`player.py`)
1. Set `"sprite_path": "assets/<name>.png"` in `character.py`.
2. In `player.py → Player.draw()`, replace the **TODO block** with:

```python
sprite = pygame.image.load(char_data["sprite_path"]).convert_alpha()
sprite = pygame.transform.scale(sprite, (w, h))
surface.blit(sprite, (cx - w // 2, bottom_y - h))
```

### Obstacles (`obstacle.py`)
Inside each `if self.obs_type == ...` branch there is a **TODO comment**.
Replace the `pygame.draw.*` calls with:

```python
img = pygame.image.load(f"assets/{self.obs_type}.png").convert_alpha()
img = pygame.transform.scale(img, (int(w), int(h)))
surface.blit(img, (int(sx) - int(w) // 2, int(sy) - int(h) // 2))
```

### Coins (`coin.py`)
Replace the ellipse drawing in `Coin.draw()` with:

```python
coin_img = pygame.image.load("assets/coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (base_r * 2, base_r * 2))
surface.blit(coin_img, (cx - base_r, cy - base_r))
```

## Exporting from Blender

For best results with the pseudo-3D perspective effect:
- Export your character **facing the camera** (front-facing orthographic render).
- Use a **transparent PNG background** (`RGBA` mode).
- Recommended export resolutions: `256×256` for characters, `256×128` for obstacles.
- The game will **scale these down automatically** using `pygame.transform.scale`
  based on the object's current depth in the scene.

> **Tip:** You can pre-generate multiple frame sizes in Blender and pick the
> closest one at runtime (mip-mapping) for sharper visuals at small scales.
