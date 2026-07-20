import pygame
import math
import random
import os
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    INITIAL_SPEED, SPEED_INCREMENT, MAX_SPEED,
    SCORE_PER_SECOND,
    BG_COLOR,
    NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_PINK, NEON_BLUE,
    GOLD, SILVER, GRAY, WHITE,
    PLAYER_Y,
)
from save_data  import load_save_data, write_save_data
from character  import get_character
from renderer   import BackgroundRenderer, draw_sky, draw_road
from player     import Player
from obstacle   import ObstacleManager
from coin       import CoinManager
from menu       import MainMenu, ShopMenu,SettingsMenu, GameOverScreen

STATE_MENU      = "menu"
STATE_SHOP      = "shop"
STATE_PLAYING   = "playing"
STATE_SETTINGS  = "settings"
STATE_GAME_OVER = "game_over"

class GameManager:

    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.clock   = pygame.time.Clock()
        self.state   = STATE_MENU
        self.running = True
        self.is_paused = False  
        pygame.font.init()

        # Custom pixel font for the neon theme
        font_path = "assets/PressStart2P.ttf"
        try:
            self.font_lg = pygame.font.Font(font_path, 36)
            self.font_md = pygame.font.Font(font_path, 22)
            self.font_sm = pygame.font.Font(font_path, 16)
        except (FileNotFoundError, pygame.error):
            try:
                self.font_lg = pygame.font.SysFont("segoeui", 52, bold=True)
                self.font_md = pygame.font.SysFont("segoeui", 28)
                self.font_sm = pygame.font.SysFont("segoeui", 20)
            except Exception:
                self.font_lg = pygame.font.Font(None, 52)
                self.font_md = pygame.font.Font(None, 28)
                self.font_sm = pygame.font.Font(None, 20)

        self.save_data = load_save_data()
        self.bg = BackgroundRenderer()

        self.player      = Player()
        self.obs_mgr     = ObstacleManager()
        self.coin_mgr    = CoinManager()

        self.main_menu   = MainMenu(self.font_lg, self.font_md, self.font_sm)
        self.shop_menu   = ShopMenu(self.font_lg, self.font_md, self.font_sm)
        self.settings_menu = SettingsMenu(self.font_lg, self.font_md, self.font_sm)
        self.gameover    = GameOverScreen(self.font_lg, self.font_md, self.font_sm)

        self.score:        float = 0.0
        self.world_speed:  float = INITIAL_SPEED
        self._dash_offset: float = 0.0  
        self._particles: list[dict] = []

        
        pygame.mixer.init()
        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        
        sound_files = {
            "coin": "assets/coin_collect.wav",
            "jump": "assets/jump.wav",
            "roll": "assets/roll.wav",
            "game_over": "assets/game_over.wav",
            "pause": "assets/pause.wav",
            "crash": "assets/crash.wav",
            "music": "assets/main_menu_music.mp3",
            "woosh": "assets/woosh.wav"
        }
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    self.sounds[name] = None
            except Exception:
                self.sounds[name] = None

        # Fallback: use woosh for roll if roll.wav missing
        if "roll" in self.sounds and self.sounds["roll"] is None and self.sounds.get("woosh"):
            self.sounds["roll"] = self.sounds["woosh"]
        # Fallback: use woosh for pause if pause.wav missing
        if "pause" in self.sounds and self.sounds["pause"] is None and self.sounds.get("woosh"):
            self.sounds["pause"] = self.sounds["woosh"]

    def _play_sound(self, name: str):
        if not self.save_data.get("sound", True):
            return
    
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def run(self):
        while self.running:
            dt        = self.clock.tick(FPS) / 1000.0
            dt        = min(dt, 0.05)         
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self._handle_event(event, mouse_pos)

            self._update(dt, mouse_pos)
            self._draw()
            pygame.display.flip()

    def _handle_event(self, event: pygame.event.Event, mouse_pos: tuple):

        if self.state == STATE_MENU:
            action = self.main_menu.handle_event(event, self.save_data)
            if action == "play":
                self._start_game()
    
            elif action == "shop":
                self.state = STATE_SHOP
    
            elif action == "settings":
                self.state = STATE_SETTINGS
    
            elif action == "quit":
                self.running = False
    
        elif self.state == STATE_SHOP:
            action = self.shop_menu.handle_event(event, self.save_data)
    
            if action == "menu":
                self.state = STATE_MENU
    
            elif action == "save":
                write_save_data(self.save_data)
    
        elif self.state == STATE_SETTINGS:
            action = self.settings_menu.handle_event(event, self.save_data)
    
            if action == "menu":
                self.state = STATE_MENU
            elif action == "save":
                write_save_data(self.save_data)
    
        elif self.state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.is_paused = not self.is_paused
                    self._play_sound("pause")
                    return
    
                if self.is_paused and event.key == pygame.K_q:
                    self.state = STATE_MENU
                    self.is_paused = False
                    return
    
            if not self.is_paused:
                self._handle_play_input(event)
    
        elif self.state == STATE_GAME_OVER:
            action = self.gameover.handle_event(event)
    
            if action == "retry":
                self._start_game()
    
            elif action == "menu":
                self.state = STATE_MENU
    def _handle_play_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k in (pygame.K_LEFT,  pygame.K_a): 
                self.player.move_left()
                self._play_sound("woosh")
            if k in (pygame.K_RIGHT, pygame.K_d): 
                self.player.move_right()
                self._play_sound("woosh")
            if k in (pygame.K_UP,    pygame.K_w): 
                self.player.jump()
                self._play_sound("jump")
            if k in (pygame.K_DOWN,  pygame.K_s): 
                self.player.start_roll()
                self._play_sound("roll")
        if event.type == pygame.KEYUP:
            k = event.key
            if k in (pygame.K_DOWN,  pygame.K_s): self.player.end_roll()

    def _update(self, dt: float, mouse_pos: tuple):

        if self.state == STATE_MENU:
            self.main_menu.update(dt, mouse_pos)
            self.bg.update(dt)
    
        elif self.state == STATE_SHOP:
            self.shop_menu.update(dt, mouse_pos)
    
        elif self.state == STATE_SETTINGS:
            self.settings_menu.update(dt, mouse_pos)
    
        elif self.state == STATE_PLAYING:
            if not self.is_paused:
                self._update_game(dt)
    
        elif self.state == STATE_GAME_OVER:
            self.gameover.update(dt, mouse_pos)

    def _update_game(self, dt: float):
        self.score      += SCORE_PER_SECOND * dt
        speed_bonus      = (int(self.score) // 10) * SPEED_INCREMENT
        self.world_speed = min(INITIAL_SPEED + speed_bonus, MAX_SPEED)

        self._dash_offset = (self._dash_offset + self.world_speed * dt) % 1.0

        self.player.update(dt)
        self.obs_mgr.update(self.world_speed, dt)
        coins_got = self.coin_mgr.update(self.world_speed, dt, self.player)
        self.bg.update(dt)

        if coins_got > 0:
            self._burst_particles(coins_got)
            self._play_sound("coin")  

        self._update_particles(dt)

        if self.obs_mgr.check_collisions(self.player):
            self._play_sound("crash")
            self._end_game()
        

    def _draw(self):

        if self.state == STATE_MENU:
            self.main_menu.draw(self.screen, self.save_data)
    
        elif self.state == STATE_SHOP:
            self.screen.fill(BG_COLOR)
            self.shop_menu.draw(self.screen, self.save_data)
    
        elif self.state == STATE_SETTINGS:
            self.screen.fill(BG_COLOR)
            self.settings_menu.draw(self.screen, self.save_data)
    
        elif self.state == STATE_PLAYING:
            self._draw_world()
            self._draw_hud()
    
            if self.is_paused:
                self._draw_pause_menu()
    
        elif self.state == STATE_GAME_OVER:
            self._draw_world()
            self._draw_hud()
    
            self.gameover.draw(
                self.screen,
                int(self.score),
                self.coin_mgr.session_coins,
                self.save_data
            )

    def _draw_pause_menu(self):
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165)) 
        self.screen.blit(overlay, (0, 0))

       
        title_surf = self.font_lg.render("PAUSED", True, NEON_PINK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(title_surf, title_rect)

        
        resume_surf = self.font_md.render("Press ESC or P to Resume", True, WHITE)
        resume_rect = resume_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(resume_surf, resume_rect)

        quit_surf = self.font_sm.render("Press Q to Return to Main Menu", True, GRAY)
        quit_rect = quit_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65))
        self.screen.blit(quit_surf, quit_rect)

    def _draw_world(self):
        draw_sky(self.screen)
        self.bg.draw(self.screen)
        draw_road(self.screen, self._dash_offset)

        self.coin_mgr.draw(self.screen)
        self.obs_mgr.draw(self.screen)

        char_data = get_character(
            self.save_data.get("selected_character", "default"))
        self.player.draw(self.screen, char_data)

        self._draw_particles()

    def _draw_hud(self):
        bar = pygame.Surface((SCREEN_WIDTH, 46), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 130))
        self.screen.blit(bar, (0, 0))

        sc = self.font_md.render(f"SCORE  {int(self.score):,}", True, NEON_CYAN)
        self.screen.blit(sc, (14, 11))

        co = self.font_md.render(f"COINS  {self.coin_mgr.session_coins}", True, GOLD)
        self.screen.blit(co, co.get_rect(center=(SCREEN_WIDTH // 2, 23)))

        hs = self.font_sm.render(f"BEST  {self.save_data.get('high_score', 0):,}",
                                 True, GRAY)
        self.screen.blit(hs, (SCREEN_WIDTH - hs.get_width() - 12, 14))

        self._draw_speed_bar()
        self._draw_lane_indicator()
        self._draw_obstacle_hint()

    def _draw_speed_bar(self):
        bx, by = 14, SCREEN_HEIGHT - 30
        bw, bh = 110, 7
        frac   = max(0.0, (self.world_speed - INITIAL_SPEED) / (MAX_SPEED - INITIAL_SPEED))

        lbl = self.font_sm.render("SPEED", True, GRAY)
        self.screen.blit(lbl, (bx, by - 18))

        pygame.draw.rect(self.screen, (25, 25, 45), (bx, by, bw, bh), border_radius=3)
        fw = int(bw * frac)
        if fw > 0:
            col = (NEON_GREEN if frac < 0.55 else
                   NEON_YELLOW if frac < 0.82 else NEON_PINK)
            pygame.draw.rect(self.screen, col, (bx, by, fw, bh), border_radius=3)
        pygame.draw.rect(self.screen, GRAY, (bx, by, bw, bh), 1, border_radius=3)

    def _draw_lane_indicator(self):
        dot_y  = SCREEN_HEIGHT - 22
        dot_x0 = SCREEN_WIDTH // 2 - 28
        for i, lane in enumerate((-1, 0, 1)):
            active = (lane == self.player.lane)
            cx     = dot_x0 + i * 28
            col    = NEON_CYAN if active else GRAY
            r      = 7 if active else 5
            pygame.draw.circle(self.screen, col, (cx, dot_y), r)
            if active:
                pygame.draw.circle(self.screen, WHITE, (cx, dot_y), r, 2)

    def _draw_obstacle_hint(self):
        if self.score > 100:   
            return
        hint = self.font_sm.render(
            "Jump: W/↑   Duck: S/↓   Lane: A/D or ←/→",
            True, (45, 45, 65))
        self.screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 12,
                                 SCREEN_HEIGHT - 22))

    def _burst_particles(self, count: int = 1):
        px = self.player.hitbox.centerx
        py = self.player.hitbox.centery
        for _ in range(count * 10):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(50, 130)
            self._particles.append({
                "x": float(px), "y": float(py),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 55,
                "life": random.uniform(0.35, 0.65),
                "max_life": 0.65,
                "r": random.randint(3, 6),
            })

    def _update_particles(self, dt: float):
        for p in self._particles:
            p["x"]   += p["vx"] * dt
            p["y"]   += p["vy"] * dt
            p["vy"]  += 200.0 * dt    
            p["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

    def _draw_particles(self):
        for p in self._particles:
            t     = p["life"] / p["max_life"]
            r     = int(255 * t)
            g     = int(210 * t)
            b     = 0
            size  = max(1, int(p["r"] * t))
            pygame.draw.circle(self.screen, (r, g, b),
                               (int(p["x"]), int(p["y"])), size)

    def _start_game(self):
        self.score        = 0.0
        self.world_speed  = INITIAL_SPEED
        self._dash_offset = 0.0
        self._particles   = []
        self.player       = Player()
        self.obs_mgr.reset()
        self.coin_mgr.reset()
        self.is_paused    = False  
        self.state        = STATE_PLAYING

    def _end_game(self):
        self._play_sound("game_over")  
        run_score = int(self.score)
        run_coins = self.coin_mgr.session_coins

        if run_score > self.save_data.get("high_score", 0):
            self.save_data["high_score"] = run_score

        self.save_data["total_coins"] = \
            self.save_data.get("total_coins", 0) + run_coins

        write_save_data(self.save_data)

        self.gameover.reset()
        self.state = STATE_GAME_OVER