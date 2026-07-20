
import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    VANISHING_POINT_X, VANISHING_POINT_Y, PLAYER_Y,
    LANE_SPREAD, LANE_HORIZON_SPREAD,
    MIN_SCALE, MAX_SCALE,
    BG_COLOR, ROAD_COLOR,
    NEON_BLUE, NEON_GREEN, NEON_CYAN, NEON_PINK,
)


def perspective_transform(depth: float, lane: int) -> tuple[float, float, float]:
    vp_x  = VANISHING_POINT_X
    vp_y  = VANISHING_POINT_Y
    bot_y = PLAYER_Y

    lane_x_bottom  = SCREEN_WIDTH // 2 + lane * LANE_SPREAD
    lane_x_horizon = SCREEN_WIDTH // 2 + lane * LANE_HORIZON_SPREAD

    screen_x = lane_x_horizon + (lane_x_bottom - lane_x_horizon) * depth
    screen_y = vp_y           + (bot_y         - vp_y)           * depth
    scale    = MIN_SCALE      + (MAX_SCALE      - MIN_SCALE)      * depth

    return screen_x, screen_y, scale


def lane_x_at_bottom(lane: int) -> int:
    return SCREEN_WIDTH // 2 + lane * LANE_SPREAD


class _Building:

    _BODY_COLOURS = [
        (13, 13, 27), (18, 16, 34), (10, 10, 22), (20, 11, 30), (8, 14, 26),
    ]
    _WIN_COLOURS = [
        (0, 45, 80), (0, 60, 45), (80, 15, 45), (55, 50, 10),
    ]

    def __init__(self, side: str):
        self.side = side
        self._reset()

    def _reset(self):
        self.w     = 150
        self.h     = 230
        self.color = random.choice(self._BODY_COLOURS)
        self.win_color = random.choice(self._WIN_COLOURS)
        self.scroll_speed = random.uniform(20, 42)

        if self.side == "left":
            self.x = 250
        else:
            self.x = 500
        self.y = VANISHING_POINT_Y - self.h

    def update(self, dt: float):
        self.y += self.scroll_speed * dt
        if self.side == "left":
            self.x -= self.scroll_speed * dt/2
        else:
            self.x += self.scroll_speed * dt/2

    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, self.win_color, rect, 1)
        wx0 = self.x + 6
        wy  = self.y + 10
        while wy < self.y + self.h - 12:
            wx = wx0
            while wx < self.x + self.w - 8:
                if random.random() > 0.3:
                    pygame.draw.rect(surface, self.win_color, (wx, wy, 6, 8))
                wx += 14
            wy += 18

    @property
    def off_screen(self) -> bool:
        return self.y > SCREEN_HEIGHT


class BackgroundRenderer:

    def __init__(self):
        self._buildings: list[_Building] = []
        self._timer = 0.0
        for _ in range(8):
            b = _Building(random.choice(["left", "right"]))
            b.y = random.randint(VANISHING_POINT_Y - b.h, SCREEN_HEIGHT - 80)
            self._buildings.append(b)

    def update(self, dt: float):
        self._timer -= dt
        if self._timer <= 0:
            side = random.choice(["left", "right"])
            self._buildings.append(_Building(side))
            self._timer = random.uniform(3, 5.1)
        for b in self._buildings:
            b.update(dt)
        self._buildings = [b for b in self._buildings if not b.off_screen]

    def draw(self, surface: pygame.Surface):
        for b in self._buildings:
            b.draw(surface)


_VPX = VANISHING_POINT_X
_VPY = VANISHING_POINT_Y
_BOT = SCREEN_HEIGHT

_ROAD_POLY = [
    (_VPX - LANE_HORIZON_SPREAD - 5,  _VPY),
    (_VPX + LANE_HORIZON_SPREAD + 5,  _VPY),
    (_VPX + LANE_SPREAD + 70,         _BOT),
    (_VPX - LANE_SPREAD - 70,         _BOT),
]


def draw_sky(surface: pygame.Surface):
    for y in range(_VPY + 1):
        t = y / _VPY
        r = int(6  + t * 8)
        g = int(6  + t * 16)
        b = int(18 + t * 60)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))


def draw_road(surface: pygame.Surface, dash_offset: float = 0.0):
    pygame.draw.polygon(surface, ROAD_COLOR, _ROAD_POLY)

    pygame.draw.line(surface, NEON_BLUE,
                     (_VPX - LANE_HORIZON_SPREAD - 5, _VPY),
                     (_VPX - LANE_SPREAD          - 70, _BOT), 2)
    pygame.draw.line(surface, NEON_BLUE,
                     (_VPX + LANE_HORIZON_SPREAD + 5, _VPY),
                     (_VPX + LANE_SPREAD          + 70, _BOT), 2)

    _draw_lane_dashes(surface, dash_offset)

    _draw_horizon_glow(surface)


def _draw_lane_dashes(surface: pygame.Surface, offset: float):
    NUM_SEGS   = 16
    DASH_FRAC  = 0.45

    for lane_frac in (-0.22, 0.22):
        x_top = _VPX + lane_frac * LANE_HORIZON_SPREAD * 2
        x_bot = _VPX + lane_frac * (LANE_SPREAD * 2)

        for i in range(NUM_SEGS):
            t1 = ((i     + offset) / NUM_SEGS) % 1.0
            t2 = ((i + DASH_FRAC + offset) / NUM_SEGS) % 1.0

            pairs = [(t1, t2)] if t1 < t2 else [(t1, 1.0), (0.0, t2)]
            for ta, tb in pairs:
                if ta >= tb:
                    continue
                x1 = x_top + (x_bot - x_top) * ta
                x2 = x_top + (x_bot - x_top) * tb
                y1 = _VPY + (_BOT - _VPY) * ta
                y2 = _VPY + (_BOT - _VPY) * tb
                brightness = int(80 + 175 * ta)
                col = (min(brightness, NEON_GREEN[0]),
                       min(brightness, NEON_GREEN[1]),
                       min(brightness, NEON_GREEN[2]))
                pygame.draw.line(surface, col,
                                 (int(x1), int(y1)),
                                 (int(x2), int(y2)), 2)


def _draw_horizon_glow(surface: pygame.Surface):
    glow = pygame.Surface((SCREEN_WIDTH, 5), pygame.SRCALPHA)
    for i, a in enumerate([30, 80, 30, 15, 5]):
        pygame.draw.line(glow, (*NEON_CYAN, a), (0, i), (SCREEN_WIDTH, i), 1)
    surface.blit(glow, (0, _VPY - 2))
