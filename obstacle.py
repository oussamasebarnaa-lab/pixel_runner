import pygame
import random
from constants import (
    LANES,
    NEON_ORANGE, NEON_PINK, NEON_PURPLE, NEON_CYAN, SILVER, WHITE,
    OBS_SPAWN_MIN, OBS_SPAWN_MAX,
    SPAWN_DEPTH, DESPAWN_DEPTH, COLLISION_DEPTH, COLLISION_END,
    PLAYER_BASE_H,
)
from renderer import perspective_transform

OBS_BARRIER = "barrier"
OBS_SIGN    = "sign"
OBS_TRAIN   = "train"

_BASE_DIM = {
    OBS_BARRIER: (115, 26),
    OBS_SIGN:    (120, 36),
    OBS_TRAIN:   (88,  112),
}

_BODY_COLOUR = {
    OBS_BARRIER: NEON_ORANGE,
    OBS_SIGN:    NEON_PINK,
    OBS_TRAIN:   (50, 40, 75),
}
_ACCENT_COLOUR = {
    OBS_BARRIER: (255, 200, 100),
    OBS_SIGN:    (255, 110, 210),
    OBS_TRAIN:   NEON_PURPLE,
}


class Obstacle:

    def __init__(self, obs_type: str, lane: int):
        self.obs_type: str   = obs_type
        self.lane:     int   = lane
        self.depth:    float = SPAWN_DEPTH
        self.active:   bool  = True

    def update(self, speed: float, dt: float):
        self.depth += speed * dt
        if self.depth >= DESPAWN_DEPTH:
            self.active = False

    def draw(self, surface: pygame.Surface):
        sx, sy, scale = perspective_transform(self.depth, self.lane)
        bw, bh = _BASE_DIM[self.obs_type]
        w  = bw * scale
        h  = bh * scale
        cx = int(sx)
        cy = int(sy)
        body_col   = _BODY_COLOUR[self.obs_type]
        accent_col = _ACCENT_COLOUR[self.obs_type]
        border_px  = max(1, int(2 * scale))

        if self.obs_type == OBS_BARRIER:
            bar = pygame.Rect(cx - int(w // 2), cy - int(h)*3, int(w), int(h)*3)
            pygame.draw.rect(surface, body_col,   bar, border_radius=4)
            pygame.draw.rect(surface, accent_col, bar, border_px, border_radius=4)

            pillar_w = max(3, int(5 * scale))
            pillar_h = max(4, int(PLAYER_BASE_H * 0.55 * scale))
            for px in (cx - int(w * 0.4), cx + int(w * 0.4) - pillar_w):
                pillar = pygame.Rect(px, cy - int(h) - pillar_h,
                                     pillar_w, pillar_h)
                pygame.draw.rect(surface, accent_col, pillar)

            stripe_w = max(4, int(12 * scale))
            for i in range(3):
                sx_stripe = cx - int(w // 2) + int((i + 0.5) * w / 3) - stripe_w // 2
                stripe = pygame.Rect(sx_stripe, cy - int(h) + border_px,
                                     stripe_w, int(h) - border_px * 2)
                pygame.draw.rect(surface, (30, 30, 30), stripe)

        elif self.obs_type == OBS_SIGN:
            sign_y = cy - int(PLAYER_BASE_H * scale * 0.62)
            sign = pygame.Rect(cx - int(w // 2), sign_y-int(h)*2, int(w), int(h))
            pygame.draw.rect(surface, body_col,   sign, border_radius=6)
            pygame.draw.rect(surface, accent_col, sign, border_px, border_radius=6)

            dash_w = max(4, int(w * 0.55))
            dash_h = max(2, int(h * 0.25))
            dash = pygame.Rect(cx - dash_w // 2, sign_y + int(h // 2) - dash_h // 2,
                               dash_w, dash_h)

            cable_y_top = sign_y - max(4, int(38 * scale))
            for cable_x in (cx - int(w * 0.3), cx + int(w * 0.3)):
                pygame.draw.line(surface, accent_col,
                                 (cable_x, cable_y_top),
                                 (cable_x, sign_y), border_px)

        elif self.obs_type == OBS_TRAIN:
            car = pygame.Rect(cx - int(w // 2), cy - int(h), int(w), int(h))
            pygame.draw.rect(surface, body_col,   car, border_radius=max(3, int(7 * scale)))
            pygame.draw.rect(surface, accent_col, car, border_px,
                             border_radius=max(3, int(7 * scale)))

            win_w = max(4, int(18 * scale))
            win_h = max(4, int(13 * scale))
            win_y = cy - int(h * 0.72)
            for wx_off in (-int(w * 0.26), int(w * 0.26)):
                wr = pygame.Rect(cx + wx_off - win_w // 2, win_y, win_w, win_h)
                pygame.draw.rect(surface, (190, 215, 255), wr, border_radius=2)

            wheel_r = max(3, int(9 * scale))
            for wx_off in (-int(w * 0.3), int(w * 0.3)):
                pygame.draw.circle(surface, (40, 40, 55),
                                   (cx + wx_off, cy), wheel_r)
                pygame.draw.circle(surface, accent_col,
                                   (cx + wx_off, cy), wheel_r, border_px)

    def is_collision(self, player) -> bool:
        if not (COLLISION_DEPTH <= self.depth <= COLLISION_END):
            return False
        if self.lane != player.lane:
            return False

        if self.obs_type == OBS_BARRIER:
            return player.jump_height < 28

        elif self.obs_type == OBS_SIGN:
            return not player.is_rolling

        elif self.obs_type == OBS_TRAIN:
            return player.jump_height < 50

        return False


class ObstacleManager:

    def __init__(self):
        self.obstacles:    list[Obstacle] = []
        self._spawn_timer: float          = OBS_SPAWN_MAX

    def reset(self):
        self.obstacles    = []
        self._spawn_timer = OBS_SPAWN_MAX

    def update(self, speed: float, dt: float):
        self._spawn_timer -= dt
        if self._spawn_timer <= 0.0:
            self._spawn_one()
            self._spawn_timer = random.uniform(OBS_SPAWN_MIN, OBS_SPAWN_MAX)

        for obs in self.obstacles:
            obs.update(speed, dt)
        self.obstacles = [o for o in self.obstacles if o.active]

    def draw(self, surface: pygame.Surface):
        for obs in sorted(self.obstacles, key=lambda o: o.depth):
            obs.draw(surface)

    def check_collisions(self, player) -> bool:
        return any(obs.is_collision(player) for obs in self.obstacles)

    def _spawn_one(self):
        obs_type = random.choices(
            [OBS_BARRIER, OBS_SIGN, OBS_TRAIN],
            weights=[35, 35, 30],
        )[0]
        lane = random.choice(LANES)
        self.obstacles.append(Obstacle(obs_type, lane))