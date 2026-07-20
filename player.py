import pygame
import math
from constants import (
    PLAYER_BASE_W, PLAYER_BASE_H, PLAYER_ROLL_H,
    JUMP_VELOCITY, GRAVITY,
    LANE_LEFT, LANE_RIGHT,
    SCREEN_WIDTH, PLAYER_Y,
    WHITE, BLACK,
)
from renderer import lane_x_at_bottom


class Player:

    def __init__(self, sprite_path="assets/image.png"):
        self.lane:       float = 0.0
        self.alive:      bool = True
        self.is_jumping: bool = False
        self.is_rolling: bool = False

        self._jump_vel: float = 0.0
        self._jump_y:   float = 0.0

        self._visual_x: float = float(lane_x_at_bottom(0))
        self._target_x: float = self._visual_x
        self._anim_t: float = 0.0
        self._LERP_SPEED = 12.0

        # Cache sprite to avoid loading from disk every frame
        self._sprite = None
        self._sprite_path = sprite_path

    def _get_sprite(self):
        """Load and cache the sprite once."""
        if self._sprite is None and self._sprite_path:
            try:
                self._sprite = pygame.image.load(self._sprite_path).convert_alpha()
            except Exception:
                self._sprite = None
        return self._sprite

    def move_left(self):
        if self.lane > LANE_LEFT:
            self.lane -= 0.66
            self._target_x = float(lane_x_at_bottom(self.lane))

    def move_right(self):
        if self.lane < LANE_RIGHT:
            self.lane += 0.66
            self._target_x = float(lane_x_at_bottom(self.lane))

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.is_rolling = False
            self._jump_vel = JUMP_VELOCITY

    def start_roll(self):
        if not self.is_jumping:
            self.is_rolling = True

    def end_roll(self):
        self.is_rolling = False

    def update(self, dt: float):
        self._anim_t += dt

        dx = self._target_x - self._visual_x
        self._visual_x += dx * min(1.0, self._LERP_SPEED * dt)

        if self.is_jumping:
            self._jump_vel += GRAVITY
            self._jump_y -= self._jump_vel
            if self._jump_y <= 0.0:
                self._jump_y = 0.0
                self._jump_vel = 0.0
                self.is_jumping = False

    def draw(self, surface: pygame.Surface, char_data: dict):
        w = PLAYER_BASE_W
        h = PLAYER_ROLL_H if self.is_rolling else PLAYER_BASE_H

        # Running bounce
        bounce = 0
        if not self.is_jumping and not self.is_rolling:
            bounce = int(abs(math.sin(self._anim_t * 10.0)) * 4)

        cx = int(self._visual_x)
        bottom_y = int(PLAYER_Y - self._jump_y) - bounce

        sprite = self._get_sprite()
        if sprite:
            img = pygame.transform.scale(sprite, (w, h))
            surface.blit(img, (cx - w // 2, bottom_y - h))
        else:
            # Fallback: draw a coloured rectangle
            body_rect = pygame.Rect(cx - w // 2, bottom_y - h, w, h)
            pygame.draw.rect(surface, char_data.get("body_color", (0,180,255)), body_rect, border_radius=7)
            pygame.draw.rect(surface, char_data.get("accent_color", (255,210,0)), body_rect, 2, border_radius=7)

    @property
    def hitbox(self) -> pygame.Rect:
        w = PLAYER_BASE_W - 12
        h = PLAYER_ROLL_H - 4 if self.is_rolling else PLAYER_BASE_H - 12
        cx = int(self._visual_x)
        cy = int(PLAYER_Y - self._jump_y)
        return pygame.Rect(cx - w // 2, cy - h, w, h)

    @property
    def jump_height(self) -> float:
        return self._jump_y
