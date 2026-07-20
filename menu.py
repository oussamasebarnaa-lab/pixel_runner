
import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    NEON_BLUE, NEON_GREEN, NEON_PINK, NEON_CYAN, NEON_YELLOW,
    NEON_ORANGE, NEON_PURPLE, GOLD, SILVER, WHITE, BLACK, GRAY,
    BG_COLOR, DARK_PANEL,
)
from character import CHARACTERS, CHARACTER_ORDER, is_unlocked, can_afford, purchase_character




def _panel(surface: pygame.Surface, rect: pygame.Rect, alpha: int = 210):
    """Semi-transparent dark panel with a neon blue border."""
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s.fill((8, 8, 22, alpha))
    surface.blit(s, rect.topleft)
    pygame.draw.rect(surface, NEON_BLUE, rect, 2, border_radius=12)


def _button(surface: pygame.Surface, rect: pygame.Rect, text: str,
            font: pygame.font.Font, colour=NEON_BLUE, hover: bool = False):
    """Neon-outlined button; brightens and changes border colour on hover."""
    bg_alpha = 80 if hover else 30
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s.fill((*colour[:3], bg_alpha))
    surface.blit(s, rect.topleft)
    border = NEON_CYAN if hover else colour
    pygame.draw.rect(surface, border, rect, 2, border_radius=10)
    label = font.render(text, True, NEON_CYAN if hover else WHITE)
    surface.blit(label, label.get_rect(center=rect.center))


def _glitch_title(surface: pygame.Surface, font: pygame.font.Font,
                  text: str, cy: int, timer: float):
    
    base = font.render(text, True, NEON_CYAN)
    rect = base.get_rect(center=(SCREEN_WIDTH // 2, cy))
    off  = int(math.sin(timer * 2.8) * 3)
    surface.blit(font.render(text, True, (255, 20,  80)), (rect.x - off, rect.y))
    surface.blit(font.render(text, True, (0,  160, 255)), (rect.x + off, rect.y))
    surface.blit(base, rect)


def _draw_char_silhouette(surface: pygame.Surface, char: dict,
                          cx: int, cy: int, scale: float = 1.0):
    
    w = int(54 * scale)
    h = int(88 * scale)
    body = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surface, char["body_color"], body, border_radius=8)
    stripe = pygame.Rect(cx - int(w * 0.12), cy - h // 2 + int(8 * scale),
                         int(10 * scale), h - int(20 * scale))
    pygame.draw.rect(surface, char["accent_color"], stripe, border_radius=3)
    pygame.draw.rect(surface, char["accent_color"], body, 2, border_radius=8)
    
    hr = int(18 * scale)
    hcy = cy - h // 2 - hr + int(3 * scale)
    pygame.draw.circle(surface, char["head_color"], (cx, hcy), hr)
    pygame.draw.circle(surface, char["accent_color"], (cx, hcy), hr, 2)




class _Starfield:
    def __init__(self, count: int = 100):
        self._stars = [
            (random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.randint(1, 3),
             random.uniform(4, 18))
            for _ in range(count)
        ]
        self._offsets = [0.0] * count

    def update(self, dt: float):
        for i, (x, y, r, speed) in enumerate(self._stars):
            self._offsets[i] += speed * dt

    def draw(self, surface: pygame.Surface):
        for i, (x, y, r, speed) in enumerate(self._stars):
            sy = int((y + self._offsets[i]) % SCREEN_HEIGHT)
            brightness = 60 + r * 40
            pygame.draw.circle(surface, (brightness,) * 3, (x, sy), 1 + (r == 3))



class MainMenu:
    _BTN_W = 280
    _BTN_H = 56

    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm
        self.timer = 0.0
        self._stars = _Starfield(110)
        self._hov = None

        cx = SCREEN_WIDTH // 2

        self.btn_play = pygame.Rect(cx - self._BTN_W // 2, 320, self._BTN_W, self._BTN_H)
        self.btn_shop = pygame.Rect(cx - self._BTN_W // 2, 390, self._BTN_W, self._BTN_H)
        self.btn_settings = pygame.Rect(cx - self._BTN_W // 2, 460, self._BTN_W, self._BTN_H)
        self.btn_quit = pygame.Rect(cx - self._BTN_W // 2, 530, self._BTN_W, self._BTN_H)

    def handle_event(self, event, save_data) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.btn_play.collidepoint(pos):
                return "play"

            if self.btn_shop.collidepoint(pos):
                return "shop"

            if self.btn_settings.collidepoint(pos):
                return "settings"

            if self.btn_quit.collidepoint(pos):
                return "quit"

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "play"

            if event.key == pygame.K_ESCAPE:
                return "quit"

        return None

    def update(self, dt: float, mouse_pos: tuple):
        self.timer += dt
        self._stars.update(dt)
        self._hov = None

        for name, btn in (
            ("play", self.btn_play),
            ("shop", self.btn_shop),
            ("settings", self.btn_settings),
            ("quit", self.btn_quit),
        ):
            if btn.collidepoint(mouse_pos):
                self._hov = name
                break

    def draw(self, surface: pygame.Surface, save_data: dict):
        surface.fill(BG_COLOR)
        self._stars.draw(surface)

        _glitch_title(surface, self.font_lg, "NEON RUSH", 215, self.timer)

        sub = self.font_sm.render(
            "Pseudo-3D Endless Runner",
            True,
            GRAY
        )
        surface.blit(
            sub,
            sub.get_rect(center=(SCREEN_WIDTH // 2, 265))
        )

        hs_surf = self.font_sm.render(
            f"High Score: {save_data['high_score']:,}",
            True,
            NEON_YELLOW
        )

        coin_surf = self.font_sm.render(
            f"Coins: {save_data['total_coins']:,}",
            True,
            GOLD
        )

        surface.blit(
            hs_surf,
            hs_surf.get_rect(center=(SCREEN_WIDTH // 2 - 110, 298))
        )

        surface.blit(
            coin_surf,
            coin_surf.get_rect(center=(SCREEN_WIDTH // 2 + 110, 298))
        )

        for label, btn, key, col in (
            ("PLAY", self.btn_play, "play", NEON_GREEN),
            ("SHOP", self.btn_shop, "shop", NEON_CYAN),
            ("SETTINGS", self.btn_settings, "settings", NEON_YELLOW),
            ("QUIT", self.btn_quit, "quit", NEON_PINK),
        ):
            _button(
                surface,
                btn,
                label,
                self.font_md,
                colour=col,
                hover=(self._hov == key)
            )

        hint = self.font_sm.render(
            "A / D or ← / → Switch lane     ↑ / W Jump     ↓ / S Roll",
            True,
            (55, 55, 75)
        )

        surface.blit(
            hint,
            hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 26))
        )

        char = CHARACTERS.get(
            save_data.get("selected_character", "default"),
            CHARACTERS["default"]
        )

        _draw_char_silhouette(
            surface,
            char,
            SCREEN_WIDTH // 2 - 300,
            410,
            scale=0.7
        )

        playing_as = self.font_sm.render(
            f"Playing as: {char['name']}",
            True,
            char["accent_color"]
        )

        surface.blit(
            playing_as,
            playing_as.get_rect(center=(SCREEN_WIDTH // 2 - 300, 466))
        )



class ShopMenu:
    _BTN_W = 230
    _BTN_H = 52

    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg   = font_lg
        self.font_md   = font_md
        self.font_sm   = font_sm
        self.timer     = 0.0
        self._stars    = _Starfield(70)
        self._sel_idx  = 0       
        self._message  = ""
        self._msg_t    = 0.0
        self._hov      = None

        cx = SCREEN_WIDTH // 2
        self.btn_prev   = pygame.Rect(cx - 280, 255, 72, 130)
        self.btn_next   = pygame.Rect(cx + 208, 255, 72, 130)
        self.btn_action = pygame.Rect(cx - self._BTN_W // 2, 490, self._BTN_W, self._BTN_H)
        self.btn_select = pygame.Rect(cx - self._BTN_W // 2, 552, self._BTN_W, self._BTN_H)
        self.btn_back   = pygame.Rect(cx - self._BTN_W // 2, 622, self._BTN_W, self._BTN_H)

    def _cid(self) -> str:
        return CHARACTER_ORDER[self._sel_idx]

    def _flash(self, msg: str):
        self._message = msg
        self._msg_t   = 2.5

    def handle_event(self, event, save_data) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_prev.collidepoint(pos):
                self._sel_idx = (self._sel_idx - 1) % len(CHARACTER_ORDER)
            elif self.btn_next.collidepoint(pos):
                self._sel_idx = (self._sel_idx + 1) % len(CHARACTER_ORDER)
            elif self.btn_action.collidepoint(pos):
                cid = self._cid()
                if is_unlocked(cid, save_data):
                    self._flash("Already owned!")
                elif not can_afford(cid, save_data):
                    self._flash(f"Need {CHARACTERS[cid]['cost'] - save_data['total_coins']:,} more coins!")
                else:
                    purchase_character(cid, save_data)
                    self._flash("Unlocked!")
                    return "save"
            elif self.btn_select.collidepoint(pos):
                cid = self._cid()
                if is_unlocked(cid, save_data):
                    save_data["selected_character"] = cid
                    self._flash("Character selected!")
                    return "save"
                else:
                    self._flash("Buy this character first!")
            elif self.btn_back.collidepoint(pos):
                return "menu"

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT,  pygame.K_a):
                self._sel_idx = (self._sel_idx - 1) % len(CHARACTER_ORDER)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._sel_idx = (self._sel_idx + 1) % len(CHARACTER_ORDER)
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def update(self, dt: float, mouse_pos: tuple):
        self.timer  += dt
        self._msg_t  = max(0.0, self._msg_t - dt)
        self._stars.update(dt)
        self._hov = None
        for name, btn in (("prev", self.btn_prev), ("next", self.btn_next),
                           ("action", self.btn_action), ("select", self.btn_select),
                           ("back", self.btn_back)):
            if btn.collidepoint(mouse_pos):
                self._hov = name
                break

    def draw(self, surface: pygame.Surface, save_data: dict):
        surface.fill(BG_COLOR)
        self._stars.draw(surface)

        
        title = self.font_lg.render("CHARACTER SHOP", True, NEON_CYAN)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 72)))

        
        bal = self.font_md.render(f"Your Coins:  {save_data['total_coins']:,}", True, GOLD)
        surface.blit(bal, bal.get_rect(center=(SCREEN_WIDTH // 2, 118)))

        cid      = self._cid()
        char     = CHARACTERS[cid]
        owned    = is_unlocked(cid, save_data)
        selected = save_data.get("selected_character") == cid

       
        card = pygame.Rect(SCREEN_WIDTH // 2 - 155, 152, 310, 298)
        _panel(surface, card)
        _draw_char_silhouette(surface, char, card.centerx, card.centery - 16, scale=1.05)

        
        name_col = NEON_GREEN if owned else GRAY
        n_surf = self.font_md.render(char["name"], True, name_col)
        surface.blit(n_surf, n_surf.get_rect(center=(card.centerx, card.bottom - 62)))

        
        if selected:
            lock_txt, lock_col = "SELECTED", NEON_GREEN
        elif owned:
            lock_txt, lock_col = "OWNED", NEON_CYAN
        else:
            lock_txt = f"LOCKED  {char['cost']:,} coins"
            lock_col = NEON_PINK
        ls = self.font_sm.render(lock_txt, True, lock_col)
        surface.blit(ls, ls.get_rect(center=(card.centerx, card.bottom - 32)))

        
        desc = self.font_sm.render(char["description"], True, GRAY)
        surface.blit(desc, desc.get_rect(center=(SCREEN_WIDTH // 2, card.bottom + 18)))

        
        _button(surface, self.btn_prev, "◀", self.font_md,
                colour=NEON_BLUE, hover=(self._hov == "prev"))
        _button(surface, self.btn_next, "▶", self.font_md,
                colour=NEON_BLUE, hover=(self._hov == "next"))

        
        if not owned:
            _button(surface, self.btn_action,
                    f"BUY  {char['cost']:,} coins", self.font_md,
                    colour=NEON_YELLOW, hover=(self._hov == "action"))
        else:
            
            _button(surface, self.btn_action, "ALREADY OWNED", self.font_sm,
                    colour=GRAY, hover=False)

        _button(surface, self.btn_select, "SELECT CHARACTER", self.font_md,
                colour=NEON_GREEN if owned else GRAY,
                hover=(self._hov == "select" and owned))
        _button(surface, self.btn_back, "BACK", self.font_md,
                colour=NEON_PINK, hover=(self._hov == "back"))

        
        if self._msg_t > 0:
            msg_col = NEON_GREEN if "!" not in self._message or "Unlock" in self._message else NEON_PINK
            ms = self.font_md.render(self._message, True, msg_col)
            surface.blit(ms, ms.get_rect(center=(SCREEN_WIDTH // 2, 468)))

        
        n = len(CHARACTER_ORDER)
        for i in range(n):
            col = NEON_CYAN if i == self._sel_idx else GRAY
            x   = SCREEN_WIDTH // 2 + (i - n // 2) * 24
            r   = 7 if i == self._sel_idx else 4
            pygame.draw.circle(surface, col, (x, 463), r)


class SettingsMenu:
    _BTN_W = 280
    _BTN_H = 56

    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm

        self._stars = _Starfield(90)
        self._hov = None

        cx = SCREEN_WIDTH // 2

        self.btn_sound = pygame.Rect(
            cx - self._BTN_W // 2,
            260,
            self._BTN_W,
            self._BTN_H
        )

        self.btn_music = pygame.Rect(
            cx - self._BTN_W // 2,
            340,
            self._BTN_W,
            self._BTN_H
        )

        self.btn_back = pygame.Rect(
            cx - self._BTN_W // 2,
            470,
            self._BTN_W,
            self._BTN_H
        )

    def handle_event(self, event, save_data):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.btn_sound.collidepoint(pos):
                save_data["sound"] = not save_data.get("sound", True)
                return "save"

            if self.btn_music.collidepoint(pos):
                save_data["music"] = not save_data.get("music", True)
                return "save"

            if self.btn_back.collidepoint(pos):
                return "menu"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def update(self, dt, mouse_pos):
        self._stars.update(dt)
        self._hov = None

        for name, btn in (
            ("sound", self.btn_sound),
            ("music", self.btn_music),
            ("back", self.btn_back)
        ):
            if btn.collidepoint(mouse_pos):
                self._hov = name
                break

    def draw(self, surface, save_data):
        surface.fill(BG_COLOR)
        self._stars.draw(surface)

        title = self.font_lg.render(
            "SETTINGS",
            True,
            NEON_CYAN
        )

        surface.blit(
            title,
            title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        )

        sound_text = (
            f"SOUND : {'ON' if save_data.get('sound', True) else 'OFF'}"
        )

        music_text = (
            f"MUSIC : {'ON' if save_data.get('music', True) else 'OFF'}"
        )

        _button(
            surface,
            self.btn_sound,
            sound_text,
            self.font_md,
            NEON_GREEN,
            self._hov == "sound"
        )

        _button(
            surface,
            self.btn_music,
            music_text,
            self.font_md,
            NEON_BLUE,
            self._hov == "music"
        )

        _button(
            surface,
            self.btn_back,
            "BACK",
            self.font_md,
            NEON_PINK,
            self._hov == "back"
        )


class GameOverScreen:
    _BTN_W = 268
    _BTN_H = 54

    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm
        self.timer   = 0.0
        self._hov    = None

        cx = SCREEN_WIDTH // 2
        self.btn_retry = pygame.Rect(cx - self._BTN_W // 2, 450, self._BTN_W, self._BTN_H)
        self.btn_menu  = pygame.Rect(cx - self._BTN_W // 2, 516, self._BTN_W, self._BTN_H)

    def reset(self):
        self.timer = 0.0

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_retry.collidepoint(event.pos): return "retry"
            if self.btn_menu.collidepoint(event.pos):  return "menu"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_r): return "retry"
            if event.key == pygame.K_ESCAPE:               return "menu"
        return None

    def update(self, dt: float, mouse_pos: tuple):
        self.timer += dt
        self._hov = None
        for name, btn in (("retry", self.btn_retry), ("menu", self.btn_menu)):
            if btn.collidepoint(mouse_pos):
                self._hov = name
                break

    def draw(self, surface: pygame.Surface, score: int,
             coins_run: int, save_data: dict):
       
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 185))
        surface.blit(ov, (0, 0))

        
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 230, 148, 460, 436)
        _panel(surface, panel, alpha=245)

     
        go = self.font_lg.render("GAME OVER", True, NEON_PINK)
        surface.blit(go, go.get_rect(center=(SCREEN_WIDTH // 2, 200)))

        
        pygame.draw.line(surface, NEON_PINK,
                         (panel.left + 24, 238), (panel.right - 24, 238), 2)

        is_hs = score >= save_data["high_score"]
        lbl   = "NEW HIGH SCORE!" if is_hs else "SCORE"
        lbl_c = NEON_YELLOW if is_hs else GRAY
        surface.blit(self.font_sm.render(lbl, True, lbl_c),
                     self.font_sm.render(lbl, True, lbl_c)
                         .get_rect(center=(SCREEN_WIDTH // 2, 262)))
        sc_surf = self.font_lg.render(f"{score:,}", True, NEON_YELLOW)
        surface.blit(sc_surf, sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))

        best = self.font_sm.render(f"Best:  {save_data['high_score']:,}", True, SILVER)
        surface.blit(best, best.get_rect(center=(SCREEN_WIDTH // 2, 344)))

        
        c_surf = self.font_md.render(f"+{coins_run} coins collected", True, GOLD)
        surface.blit(c_surf, c_surf.get_rect(center=(SCREEN_WIDTH // 2, 382)))

        bank = self.font_sm.render(
            f"Total bank:  {save_data['total_coins']:,}", True, (200, 165, 40))
        surface.blit(bank, bank.get_rect(center=(SCREEN_WIDTH // 2, 418)))

        
        _button(surface, self.btn_retry, "PLAY AGAIN", self.font_md,
                colour=NEON_GREEN, hover=(self._hov == "retry"))
        _button(surface, self.btn_menu,  "MAIN MENU",  self.font_md,
                colour=NEON_BLUE,  hover=(self._hov == "menu"))
