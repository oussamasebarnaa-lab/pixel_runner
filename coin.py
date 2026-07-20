import pygame
import math
import random
from constants import (
    LANES,
    GOLD, WHITE,
    COIN_SPAWN_MIN, COIN_SPAWN_MAX,
    SPAWN_DEPTH, DESPAWN_DEPTH, COLLISION_DEPTH, COLLISION_END,
    COIN_VALUE,
)
from renderer import perspective_transform

_COIN_BASE_R = 13   
_PAT_LINE   = "line"
_PAT_ARC    = "arc"
_PAT_SINGLE = "single"


class Coin:

    def __init__(self, lane: int, depth: float = SPAWN_DEPTH):
        self.lane:      int   = lane
        self.depth:     float = depth
        self.collected: bool  = False
        self.active:    bool  = True
        self._spin:     float = random.uniform(0, math.pi * 2)   

    def update(self, speed: float, dt: float):
        self.depth += speed * dt
        self._spin += dt * 5.0          
        if self.depth >= DESPAWN_DEPTH:
            self.active = False

    def draw(self, surface: pygame.Surface):
        if self.collected:
            return
        sx, sy, scale = perspective_transform(self.depth, self.lane)
        base_r = max(3, int(_COIN_BASE_R * scale))
        cx, cy = int(sx), int(sy)

        spin_x = max(1, int(base_r * abs(math.sin(self._spin))))
        spin_y = base_r

        surf_w = spin_x * 2 + 6
        surf_h = spin_y * 2 + 6
        coin_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        pygame.draw.ellipse(coin_surf, GOLD,
                            (3, 3, spin_x * 2, spin_y * 2))
        pygame.draw.ellipse(coin_surf, (255, 240, 110),
                            (3, 3, max(1, spin_x), spin_y * 2))
        pygame.draw.ellipse(coin_surf, (195, 155, 10),
                            (3, 3, spin_x * 2, spin_y * 2), max(1, int(scale + 1)))

        surface.blit(coin_surf, (cx - spin_x - 3, cy - spin_y - 3))

    def check_collected(self, player) -> bool:
        if self.collected:
            return False
        if not (COLLISION_DEPTH <= self.depth <= COLLISION_END):
            return False
        return self.lane == player.lane


class CoinManager:

    def __init__(self):
        self.coins:         list[Coin] = []
        self._spawn_timer:  float      = COIN_SPAWN_MAX
        self.session_coins: int        = 0 

    def reset(self):
        self.coins         = []
        self._spawn_timer  = COIN_SPAWN_MAX
        self.session_coins = 0

    def update(self, speed: float, dt: float, player) -> int:
        self._spawn_timer -= dt
        if self._spawn_timer <= 0.0:
            self._spawn_pattern()
            self._spawn_timer = random.uniform(COIN_SPAWN_MIN, COIN_SPAWN_MAX)

        collected_now = 0
        for coin in self.coins:
            coin.update(speed, dt)
            if coin.check_collected(player):
                coin.collected = True
                coin.active    = False
                collected_now += COIN_VALUE

        self.coins          = [c for c in self.coins if c.active]
        self.session_coins += collected_now
        return collected_now

    def draw(self, surface: pygame.Surface):
        for coin in sorted(self.coins, key=lambda c: c.depth):
            coin.draw(surface)

    def _spawn_pattern(self):
        pattern = random.choices(
            [_PAT_LINE, _PAT_ARC, _PAT_SINGLE],
            weights=[40, 30, 30],
        )[0]

        if pattern == _PAT_LINE:
            lane  = random.choice(LANES)
            count = random.randint(4, 6)
            for i in range(count):
                self.coins.append(Coin(lane, SPAWN_DEPTH + i * 0.045))

        elif pattern == _PAT_ARC:
            for i, lane in enumerate(LANES):
                self.coins.append(Coin(lane, SPAWN_DEPTH + i * 0.06))

        elif pattern == _PAT_SINGLE:
            self.coins.append(Coin(random.choice(LANES)))