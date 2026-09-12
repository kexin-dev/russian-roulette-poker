"""
╔══════════════════════════════════════════════════════════════════════╗
║     BULLET CARDS — DOOMSDAY WESTERN EDITION (v4.0)              ║
║                                                                      ║
║  ▸ Two-player local duel, 50 gold each, hand 1~6                   ║
║  ▸ Flow: Select → Bribe → Betting(call/raise) → Reveal → Shoot     ║
║  ▸ Player 1 calls HIGH/LOW + bet; P2 can call or raise to flip    ║
║  ▸ Bribe dealer for intel; benefactor can make dealer lie/tell truth║
║  ▸ Loser shoots self: bullets = card value, hit chance = value/6   ║
║  ▸ All bet & bribe gold is DESTROYED every round                   ║
║  ▸ Snake (P1) vs Lizard (P2), mood portraits                       ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import pygame, random, sys, math, os

# ── Init ───────────────────────────────────────────────────────────
pygame.init()
W, H = 1280, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Bullet Cards — Doomsday Western")
clock = pygame.time.Clock()

# ── Audio Manager ───────────────────────────────────────────────────
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')

class AudioManager:
    def __init__(self):
        self.muted = False
        self.bgm_volume = 0.4
        self.sfx_volume = 0.7
        self.ambience_volume = 0.3
        self.sounds = {}
        self.bgm = None
        self.ambience = None
        self._load_all()

    def _load(self, name):
        path = os.path.join(AUDIO_DIR, name)
        if os.path.exists(path):
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self.sfx_volume)
                self.sounds[name] = snd
                return snd
            except Exception:
                pass
        return None

    def _load_all(self):
        try:
            pygame.mixer.init()
        except Exception:
            return
        # 音效
        for f in ['card_flip.wav', 'card_throw.wav', 'gold_drop.wav',
                  'gunshot.wav', 'empty_chamber.wav', 'cylinder_spin.wav',
                  'button_click.wav']:
            self._load(f)
        # 背景音乐
        bgm_path = os.path.join(AUDIO_DIR, 'bgm_accordion.wav')
        if os.path.exists(bgm_path):
            try:
                self.bgm = pygame.mixer.Sound(bgm_path)
                self.bgm.set_volume(self.bgm_volume)
            except Exception:
                pass
        # 环境音
        amb_path = os.path.join(AUDIO_DIR, 'ambience_rain.wav')
        if os.path.exists(amb_path):
            try:
                self.ambience = pygame.mixer.Sound(amb_path)
                self.ambience.set_volume(self.ambience_volume)
            except Exception:
                pass

    def play(self, name):
        if self.muted:
            return
        if name in self.sounds:
            self.sounds[name].play()

    def start_bgm(self):
        if self.bgm and not self.muted:
            self.bgm.play(loops=-1, fade_ms=2000)

    def start_ambience(self):
        if self.ambience and not self.muted:
            self.ambience.play(loops=-1, fade_ms=1500)

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            if self.bgm:
                self.bgm.stop()
            if self.ambience:
                self.ambience.stop()
        else:
            self.start_bgm()
            self.start_ambience()

    def stop_all(self):
        if self.bgm:
            self.bgm.stop()
        if self.ambience:
            self.ambience.stop()

audio = AudioManager()

# ── Fonts ──────────────────────────────────────────────────────────
def _font(size, bold=False, italic=True):
    candidates = [
        "georgia", "timesnewroman", "garamond", "bookantiqua",
        "palatinolinotype", "cambria", "serif"
    ]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold, italic=italic)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

FONT   = _font(20)
FONT_B = _font(22, bold=True)
FONT_T = _font(28, bold=True)
FONT_H = _font(44, bold=True)
FONT_S = _font(16)
FONT_XS = _font(13)

# ── Palette ────────────────────────────────────────────────────────
C_SAND      = (196, 164, 110)
C_SAND_DK   = (120,  92,  56)
C_LEATHER   = ( 90,  58,  32)
C_LEATHER_D = ( 58,  36,  18)
C_BLOOD     = (150,  24,  24)
C_BONE      = (228, 214, 186)
C_GOLD      = (218, 178,  66)
C_GOLD_L    = (248, 224, 130)
C_GOLD_D    = (168, 128,  36)
C_RUST      = (138,  74,  38)
C_BROWN     = ( 60,  40,  24)
C_BLOOD     = (150,  24,  24)
C_BLOOD_L   = (210,  60,  60)
C_PARCHMENT = (232, 220, 196)
C_SHADOW    = ( 20,  12,   8)
C_GREEN     = ( 60, 120,  60)

# ── Asset Loading ──────────────────────────────────────────────────
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

def load_img(name, scale_to=None):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if scale_to:
            img = pygame.transform.smoothscale(img, scale_to)
        return img
    return None

IMG_BG_MENU   = load_img('background_menu.png', (W, H))
IMG_BG_GAME   = load_img('background_saloon.png', (W, H))
CARD_W, CARD_H = 90, 126
IMG_CARDS = {}
for n in range(1, 7):
    IMG_CARDS[n] = load_img(f'card_{n}.png', (CARD_W, CARD_H))
IMG_CARD_BACK = load_img('card_back.png', (CARD_W, CARD_H))
CHAR_W, CHAR_H = 150, 200
def _load_char(animal, mood):
    return load_img(f'{animal}_{mood}.png', (CHAR_W, CHAR_H))
IMG_SNAKE = {m: _load_char('snake', m) for m in ['normal','scared','dead','survivor','victory']}
IMG_LIZARD = {m: _load_char('lizard', m) for m in ['normal','scared','dead','survivor','victory']}
IMG_DEALER = load_img('dealer_owl.png', (160, 200))
IMG_ROULETTE = load_img('roulette_cylinder.png', (140, 140))

# ═════════════════════════════════════════════════════════════════════
#  Utilities
# ═════════════════════════════════════════════════════════════════════
def draw_rounded(surf, rect, radius, color, border=None, bw=2):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border, rect, bw, border_radius=radius)

def draw_text(surf, text, font, color, x, y, center=False, shadow=True):
    if shadow:
        shadow_img = font.render(str(text), True, C_SHADOW)
        sr = shadow_img.get_rect()
        if center: sr.center = (x+2, y+2)
        else: sr.topleft = (x+2, y+2)
        surf.blit(shadow_img, sr)
    img = font.render(str(text), True, color)
    r = img.get_rect()
    if center: r.center = (x, y)
    else: r.topleft = (x, y)
    surf.blit(img, r)
    return r

def make_alpha_surf(w, h, color, alpha):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    return s

# ═════════════════════════════════════════════════════════════════════
#  Card Drawing
# ═════════════════════════════════════════════════════════════════════
def draw_card(surf, number, x, y, face_up=True, selected=False, scale=1.0, hover=False, flip_progress=0.0):
    """
    flip_progress: 0.0=正面, 0.5=侧面(不可见), 1.0=反面
    hover: 鼠标悬停时上浮+放大+发光
    """
    if hover:
        x -= 3; y -= 12; scale = min(1.15, scale * 1.08)
    cw, ch = int(CARD_W*scale), int(CARD_H*scale)
    # 翻牌动画：x方向缩放模拟翻转
    if flip_progress > 0 and flip_progress < 1:
        flip_scale = abs(math.cos(flip_progress * math.pi))
        cw = max(1, int(cw * flip_scale))
        if flip_progress > 0.5:
            face_up = not face_up
    rect = pygame.Rect(x, y, cw, ch)
    shadow = make_alpha_surf(cw+6, ch+6, (0,0,0), 140)
    surf.blit(shadow, (x+3, y+3))
    if hover:
        glow = make_alpha_surf(cw+16, ch+16, C_GOLD_L, 35)
        surf.blit(glow, (x-8, y-8))
    if face_up and number in IMG_CARDS and IMG_CARDS[number]:
        img = IMG_CARDS[number]
        if scale != 1.0 or cw != CARD_W:
            img = pygame.transform.smoothscale(img, (cw, ch))
        surf.blit(img, rect.topleft)
    else:
        if IMG_CARD_BACK:
            img = IMG_CARD_BACK
            if scale != 1.0 or cw != CARD_W:
                img = pygame.transform.smoothscale(img, (cw, ch))
            surf.blit(img, rect.topleft)
        else:
            draw_rounded(surf, rect, 8, C_BLOOD, C_LEATHER_D, 3)
    if selected:
        pygame.draw.rect(surf, C_GOLD_L, rect, 4, border_radius=8)
        glow = make_alpha_surf(cw+12, ch+12, C_GOLD_L, 50)
        surf.blit(glow, (x-6, y-6))
    return rect

# ═════════════════════════════════════════════════════════════════════
#  Particles
# ═════════════════════════════════════════════════════════════════════
class Particles:
    def __init__(self): self.parts = []
    def emit(self, x, y, color, count=30, speed=6, life=40, gravity=0.15, size_range=(2,5)):
        for _ in range(count):
            ang = random.uniform(0, math.pi*2)
            sp = random.uniform(1, speed)
            self.parts.append({
                "x":x,"y":y,"vx":math.cos(ang)*sp,"vy":math.sin(ang)*sp-random.uniform(0,2),
                "life":random.randint(life//2, life),"max_life":life,
                "color":color[:3],"size":random.randint(*size_range),"gravity":gravity,"kind":"circle"
            })
    def emit_gold(self, x, y, count=15, target_x=None, target_y=None):
        """金币粒子：飞向目标或四散"""
        for _ in range(count):
            if target_x is not None:
                dx, dy = target_x - x, target_y - y
                dist = max(1, math.hypot(dx, dy))
                sp = random.uniform(4, 8)
                vx, vy = dx/dist*sp, dy/dist*sp
            else:
                ang = random.uniform(-math.pi*0.8, -math.pi*0.2)
                sp = random.uniform(3, 7)
                vx, vy = math.cos(ang)*sp, math.sin(ang)*sp
            self.parts.append({
                "x":x,"y":y,"vx":vx,"vy":vy,
                "life":random.randint(30, 55),"max_life":55,
                "color":C_GOLD[:3],"size":random.randint(4,7),"gravity":0.12,"kind":"gold",
                "rot":random.uniform(0, math.pi*2),"rot_spd":random.uniform(-0.3, 0.3)
            })
    def emit_dust(self, x, y, count=5):
        """背景尘土：缓慢飘动的半透明粒子"""
        for _ in range(count):
            self.parts.append({
                "x":x+random.uniform(-30,30),"y":y+random.uniform(-20,20),
                "vx":random.uniform(-0.3, 0.6),"vy":random.uniform(-0.4, -0.1),
                "life":random.randint(120, 200),"max_life":200,
                "color":(180,155,110),"size":random.randint(1,3),"gravity":0,"kind":"dust"
            })
    def emit_spark(self, x, y, count=20):
        """枪口火花：快速飞溅的亮黄色粒子"""
        for _ in range(count):
            ang = random.uniform(-math.pi*0.3, math.pi*0.3)
            sp = random.uniform(6, 14)
            self.parts.append({
                "x":x,"y":y,"vx":math.cos(ang)*sp,"vy":math.sin(ang)*sp,
                "life":random.randint(10, 25),"max_life":25,
                "color":(255,random.randint(180,230),60),"size":random.randint(2,4),
                "gravity":0.2,"kind":"spark"
            })
    def emit_smoke(self, x, y, count=10):
        """射击后烟雾：缓慢上升扩散的灰色粒子"""
        for _ in range(count):
            self.parts.append({
                "x":x+random.uniform(-10,10),"y":y+random.uniform(-5,5),
                "vx":random.uniform(-0.5,0.5),"vy":random.uniform(-1.2,-0.6),
                "life":random.randint(40, 70),"max_life":70,
                "color":(120,110,100),"size":random.randint(6,12),"gravity":-0.02,"kind":"smoke"
            })
    def update(self):
        for p in self.parts:
            p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=p.get("gravity",0.15); p["life"]-=1
            if p.get("kind")=="gold":
                p["rot"]=p.get("rot",0)+p.get("rot_spd",0)
                p["vx"]*=0.98
            if p.get("kind")=="smoke":
                p["size"]+=0.15
                p["vx"]*=0.99
        self.parts = [p for p in self.parts if p["life"]>0]
    def draw(self, surf):
        for p in self.parts:
            alpha = int(255 * min(1, p["life"]/max(1,p.get("max_life",p["life"]))))
            kind = p.get("kind","circle")
            if kind == "gold":
                col = tuple(min(255, c+30) for c in p["color"])
                pygame.draw.circle(surf, col, (int(p["x"]),int(p["y"])), p["size"])
                pygame.draw.circle(surf, (255,240,180), (int(p["x"]-1),int(p["y"]-1)), max(1,p["size"]//2))
            elif kind == "dust":
                s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["color"], alpha//3), (p["size"],p["size"]), p["size"])
                surf.blit(s, (int(p["x"]-p["size"]), int(p["y"]-p["size"])))
            elif kind == "smoke":
                s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["color"], alpha//4), (p["size"],p["size"]), p["size"])
                surf.blit(s, (int(p["x"]-p["size"]), int(p["y"]-p["size"])))
            elif kind == "spark":
                pygame.draw.circle(surf, p["color"], (int(p["x"]),int(p["y"])), p["size"])
                pygame.draw.line(surf, p["color"], (int(p["x"]),int(p["y"])),
                                 (int(p["x"]-p["vx"]*1.5), int(p["y"]-p["vy"]*1.5)), 1)
            else:
                pygame.draw.circle(surf, p["color"], (int(p["x"]),int(p["y"])), p["size"])

# ═════════════════════════════════════════════════════════════════════
#  UI Controls
# ═════════════════════════════════════════════════════════════════════
class Button:
    def __init__(self, x, y, w, h, text, font=None, col=C_LEATHER, hot=C_RUST, txt_col=C_BONE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font or FONT_S
        self.col = col; self.hot = hot; self.txt_col = txt_col
        self.enabled = True
        self.pressed = False
        self.hover_anim = 0.0
    def draw(self, surf):
        mouse_pos = pygame.mouse.get_pos()
        hov = self.rect.collidepoint(mouse_pos) and self.enabled
        # 悬停动画渐变
        target = 1.0 if hov else 0.0
        self.hover_anim += (target - self.hover_anim) * 0.15
        # 按下效果
        pressed = hov and pygame.mouse.get_pressed()[0]
        self.pressed = pressed
        draw_rect = self.rect.copy()
        if pressed:
            draw_rect.inflate_ip(-4, -3)
            draw_rect.y += 2
        base = self.hot if hov else self.col
        # 悬停时轻微发光
        if hov and self.enabled:
            glow = make_alpha_surf(self.rect.w+12, self.rect.h+12, base, 40)
            surf.blit(glow, (self.rect.x-6, self.rect.y-6))
        draw_rounded(surf, draw_rect, 8, base, C_LEATHER_D, 2)
        # 顶部高光
        highlight = make_alpha_surf(draw_rect.w-8, 3, (255,255,255), int(60+self.hover_anim*40))
        surf.blit(highlight, (draw_rect.x+4, draw_rect.y+2))
        tc = self.txt_col if self.enabled else (120,120,120)
        draw_text(surf, self.text, self.font, tc, draw_rect.centerx, draw_rect.centery, center=True)
    def check(self, ev):
        return self.enabled and ev.type==pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(ev.pos)

class InputBox:
    def __init__(self, x, y, w, h, value=0, min_v=0, max_v=999, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = max(min_v, min(max_v, value))
        self.min_v, self.max_v = min_v, max_v
        self.label = label
        self.btn_w = 34
    def clamp(self):
        self.value = max(self.min_v, min(self.max_v, int(self.value)))
    def draw(self, surf):
        draw_rounded(surf, self.rect, 8, C_PARCHMENT, C_LEATHER, 2)
        if self.label:
            draw_text(surf, self.label, FONT_XS, C_LEATHER_D, self.rect.x+8, self.rect.y+4)
        draw_text(surf, str(self.value), FONT_T, C_LEATHER_D,
                  self.rect.centerx-10, self.rect.centery+4, center=True)
        r_plus  = pygame.Rect(self.rect.right-self.btn_w, self.rect.y, self.btn_w, self.rect.h//2)
        r_minus = pygame.Rect(self.rect.right-self.btn_w, self.rect.y+self.rect.h//2, self.btn_w, self.rect.h//2)
        draw_rounded(surf, r_plus,  0, C_RUST, None, 0)
        draw_rounded(surf, r_minus, 0, C_LEATHER, None, 0)
        draw_text(surf, "+", FONT_B, C_BONE, r_plus.centerx,  r_plus.centery,  center=True, shadow=False)
        draw_text(surf, "-", FONT_B, C_BONE, r_minus.centerx, r_minus.centery, center=True, shadow=False)
    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.rect.right-self.btn_w, self.rect.y, self.btn_w, self.rect.h//2).collidepoint(ev.pos):
                self.value+=1; self.clamp(); return True
            if pygame.Rect(self.rect.right-self.btn_w, self.rect.y+self.rect.h//2, self.btn_w, self.rect.h//2).collidepoint(ev.pos):
                self.value-=1; self.clamp(); return True
        return False

# ═════════════════════════════════════════════════════════════════════
#  Player
# ═════════════════════════════════════════════════════════════════════
class Player:
    def __init__(self, name, side, animal):
        self.name = name
        self.side = side
        self.animal = animal
        self.reset()
    def reset(self):
        self.gold = 50
        self.hand = [1,2,3,4,5,6]
        self.alive = True
        self.selected_card = None
        self.pending_play = None
        self.round_bet = 0       # 本轮累计下注
        self.bribe_amount = 0    # 本轮贿赂
        self.bribe_strategy = 'trick'  # trick / honest
        self.private_hint = "..."
        self.card_rects = []
        self.mood = "normal"
    @property
    def is_left(self): return self.side=='left'
    @property
    def cx(self): return 200 if self.is_left else W-200
    @property
    def char_images(self):
        return IMG_SNAKE if self.animal=='snake' else IMG_LIZARD
    def set_mood(self, mood):
        if mood in self.char_images and self.char_images[mood]:
            self.mood = mood
        else:
            self.mood = "normal"
    def draw(self, surf, is_active=False, reveal_cards=False, played_revealed=False, show_gold=True):
        cx, base_y = self.cx, 290
        panel_w, panel_h = 360, 470
        panel = pygame.Rect(cx-panel_w//2, base_y-30, panel_w, panel_h)
        draw_rounded(surf, panel, 14, (*C_LEATHER_D[:3], 210), C_LEATHER, 3)
        if is_active:
            glow = make_alpha_surf(panel_w+16, panel_h+16, C_GOLD_L, 40)
            surf.blit(glow, (panel.x-8, panel.y-8))
            draw_rounded(surf, panel, 14, (*C_LEATHER[:3],210), C_GOLD_L, 3)
        char_img = self.char_images.get(self.mood) or self.char_images.get('normal')
        if char_img:
            # 呼吸微动：存活时轻微上下浮动
            breath = 0
            if self.alive:
                breath = math.sin(pygame.time.get_ticks() * 0.003 + (0 if self.is_left else 1.5)) * 3
            # 恐惧时抖动
            if self.mood == 'scared' and self.alive:
                breath += random.uniform(-2, 2)
            surf.blit(char_img, (cx-CHAR_W//2, base_y-10 + int(breath)))
        else:
            pygame.draw.circle(surf, C_SAND, (cx, base_y+80), 60)
        draw_text(surf, self.name, FONT_T, C_GOLD_L, cx, base_y+CHAR_H+8, center=True)
        sy = base_y + CHAR_H + 34
        if show_gold:
            draw_text(surf, f"Gold: {self.gold}", FONT_B, C_GOLD, cx-110, sy, center=False)
        else:
            draw_text(surf, "Gold: ???", FONT_B, (150,150,150), cx-110, sy, center=False)
        draw_text(surf, f"Cards: {len(self.hand)}", FONT_B, C_BONE, cx+30, sy, center=False)
        if self.round_bet > 0:
            draw_text(surf, f"Bet: {self.round_bet}", FONT_B, C_RUST, cx-80, sy+28, center=False)
        if self.selected_card is not None:
            sx, sy2 = cx-CARD_W//2, base_y-50
            draw_card(surf, self.selected_card, sx, sy2, face_up=played_revealed)
        # private hint (only visible when active)
        if is_active and self.private_hint != "..." and self.alive:
            hy = base_y + CHAR_H + 66
            hint_rect = pygame.Rect(cx-150, hy, 300, 36)
            draw_rounded(surf, hint_rect, 6, (*C_BROWN[:3],200), C_GOLD, 1)
            draw_text(surf, f"Dealer: {self.private_hint}", FONT_XS, C_GOLD_L, cx, hy+18, center=True)
        # hand cards
        self.card_rects = []
        n = len(self.hand)
        # 动态计算卡牌间距：牌多时缩小，确保6张牌能在面板内完整显示
        panel_inner_w = panel_w - CARD_W - 20  # 左右各留10px边距
        max_spacing = panel_inner_w / max(1, n - 1) if n > 1 else 96
        spacing = min(96, max_spacing)
        total_w = max(0, (n - 1) * spacing)
        start_x = cx - total_w // 2
        hand_y = base_y + panel_h - CARD_H - 14
        show_face = is_active or reveal_cards
        mouse_pos = pygame.mouse.get_pos()
        for i, num in enumerate(self.hand):
            rx = start_x + i*spacing - CARD_W//2
            ry = hand_y
            sel = (self.pending_play == num)
            # 悬停检测：只有在自己的回合且手牌明牌时才响应
            hover = is_active and show_face and pygame.Rect(rx, ry, CARD_W, CARD_H).collidepoint(mouse_pos)
            draw_card(surf, num, rx, ry, face_up=show_face, selected=sel, hover=hover)
            self.card_rects.append((pygame.Rect(rx, ry, CARD_W, CARD_H), num))
        if not self.alive:
            overlay = make_alpha_surf(panel_w, panel_h, (20,10,10), 160)
            surf.blit(overlay, panel.topleft)
            draw_text(surf, "DEAD", FONT_H, C_BLOOD, cx, base_y+panel_h//2, center=True)

# ═════════════════════════════════════════════════════════════════════
#  Dealer (greedy owl — intel broker)
# ═════════════════════════════════════════════════════════════════════
class Dealer:
    def __init__(self):
        self.reset()
    def reset(self):
        self.gold = 0
        self.bribes = {}
        self.benefactor = None
        self.speech = "Lay yer gold on the table... tonight, I decide who lives."
        self.hints = {}
    def beg(self, round_num):
        lines = [
            "Want to live? Gold buys yer way outta the grave...",
            "I got intel, and it goes to the highest bidder.",
            "Heh heh... time to fill my pockets again.",
            "Fate? Fate can be purchased with enough gold.",
            "Who pays the most gets the truth from me.",
            "The cards are dealt... but the truth? That's extra.",
        ]
        self.speech = random.choice(lines)

    def _card_hint_true(self, card_val):
        """生成关于某张牌的真实情报"""
        if card_val <= 2:
            return random.choice([
                "Opponent's card is light... real light.",
                "I seen his card. Barely a bullet in there.",
                "Small card. He's bluffing if he acts tough.",
            ])
        elif card_val <= 4:
            return random.choice([
                "Opponent's card is middling. Nothing fancy.",
                "Average card. Could go either way.",
                "Nothing special in his hand, I'll tell ya.",
            ])
        else:
            return random.choice([
                "Opponent's card is heavy... real heavy.",
                "That's a big bullet he's carrying. Careful.",
                "Large card. He might be dangerous.",
            ])

    def _card_hint_false(self, card_val):
        """生成关于某张牌的假情报（与真实相反，三档信号都可能出现）"""
        if card_val <= 2:
            # 真实是 small → 假情报随机说 medium 或 large
            return random.choice([
                "Opponent's card is middling. Nothing fancy.",
                "Average card. Could go either way.",
                "Opponent's card is huge! He's loaded for bear.",
                "Big card, real big. I'd be scared if I were you.",
                "He's packin' serious heat. Watch yourself.",
            ])
        elif card_val <= 4:
            # 真实是 medium → 假情报随机说 small 或 large
            return random.choice([
                "Opponent's card is tiny. Practically empty.",
                "Small card. He's got nothing.",
                "Light as a feather, that one.",
                "Opponent's card is heavy... real heavy.",
                "That's a big bullet he's carrying. Careful.",
                "Large card. He might be dangerous.",
            ])
        else:
            # 真实是 large → 假情报随机说 small 或 medium
            return random.choice([
                "Opponent's card is tiny. Nothing to fear.",
                "Small card. He's bluffing if he acts tough.",
                "Barely a bullet in there. You'll be fine.",
                "Opponent's card is middling. Average at best.",
                "Nothing special in his hand, I'll tell ya.",
                "Middle of the road. Nothing to write home about.",
            ])

    def _card_hint_vague(self):
        """模糊情报（双方都没贿赂或贿赂相当时）"""
        return random.choice([
            "This round's deep water. Swim careful.",
            "I only see gold, not cards. Pay up and I'll look.",
            "Someone's gonna die tonight. Maybe both, who knows?",
            "The cards hold secrets... secrets cost gold.",
            "I ain't no prophet. But I know who paid.",
            "Trust no one. Especially not me. Heh heh.",
        ])

    def collect_and_resolve(self, p1, p2):
        """收集贿赂，生成双方情报"""
        self.bribes = {}
        for p in (p1, p2):
            if p.bribe_amount > 0 and p.alive:
                self.bribes[p] = p.bribe_amount
                self.gold += p.bribe_amount

        self.hints = {}
        if not self.bribes:
            # 没人贿赂，双方都得到模糊情报
            for p in (p1, p2):
                self.hints[p] = self._card_hint_vague()
            self.benefactor = None
            self.speech = random.choice([
                "No gold tonight? Then may the odds be ever in yer favor.",
                "A bunch of misers... fate decides then.",
                "Hmph. No one wants to buy their life?"])
            return

        # 找出金主
        sorted_b = sorted(self.bribes.items(), key=lambda kv: kv[1], reverse=True)
        top, top_amt = sorted_b[0]
        self.benefactor = top

        # 金主总是得到真实情报（关于对手的牌）
        opponent = p2 if top == p1 else p1
        self.hints[top] = self._card_hint_true(opponent.selected_card)

        # 对手得到的情报取决于金主的策略
        if top.bribe_strategy == 'trick':
            self.hints[opponent] = self._card_hint_false(top.selected_card)
        else:
            # honest：给对手真实情报（反向心理）
            self.hints[opponent] = self._card_hint_true(top.selected_card)

        # 荷官公开台词
        self.speech = self._compose_speech(p1, p2, top, top_amt)

    def _compose_speech(self, p1, p2, top, top_amt):
        lines = []
        # 不再泄露金主身份和出价比例，只说模糊的氛围话
        lines.append(random.choice([
            "Gold changes hands tonight... and so does fate.",
            "The owl sees all... but only tells what he's paid to tell.",
            "Somebody's buyin' secrets. Whether they're worth it... heh.",
            "Coins clink, cards whisper. Who's lyin'? Who's tellin'?",
            "I got gold in my pocket and secrets in my head. Life is good.",
            "The highest bidder gets my ear. The rest get my smile.",
        ]))

        # 模糊评论下注
        if p1.round_bet > 0 or p2.round_bet > 0:
            diff = abs(p1.round_bet - p2.round_bet)
            if diff >= 10:
                leader = p1 if p1.round_bet > p2.round_bet else p2
                lines.append(f"{leader.name.split('—')[0].strip()} bets big... real hand or just blowin' smoke?")
            elif p1.round_bet == p2.round_bet and p1.round_bet > 0:
                lines.append("Both equally flush... both confident?")

        # 评论手牌数量
        for p in (p1, p2):
            if len(p.hand) == 1:
                lines.append(f"{p.name.split('—')[0].strip()} down to their last card... desperate times.")
            elif len(p.hand) == 2:
                lines.append(f"{p.name.split('—')[0].strip()} runnin' low on bullets...")

        if not lines[1:]:
            lines.append(random.choice([
                "The air is thick with lies tonight.",
                "Somebody's hidin' something. I can smell it.",
                "Gold talks, and I'm all ears.",
            ]))
        return " ".join(lines)

    def betting_commentary(self, p1, p2, current_mode, current_bet, raise_count):
        """加注阶段的实时评论"""
        mode_name = "HIGH" if current_mode == 'big' else "LOW"
        comments = []
        if raise_count == 0:
            comments.append(f"{p1.name.split('—')[0].strip()} calls {mode_name} with {current_bet} gold.")
            comments.append(random.choice([
                "Is he bluffin'? Or packin' heat?",
                "The first move is always the boldest.",
                "He's puttin' his gold where his mouth is.",
            ]))
        elif raise_count == 1:
            comments.append(f"{p2.name.split('—')[0].strip()} raises! Flips to {mode_name} with {current_bet} gold!")
            comments.append(random.choice([
                "Oh! A challenge! Things heatin' up!",
                "He don't like the odds. He's changin' 'em!",
                "Big money, big stones. Or big bluff?",
            ]))
        else:
            comments.append(f"Back to {p1.name.split('—')[0].strip()}! {mode_name} at {current_bet} gold!")
            comments.append(random.choice([
                "A war of gold and nerves! Who blinks first?",
                "This is gettin' expensive. Someone's gonna bleed.",
                "Raise after raise... egos or cards?",
            ]))
        self.speech = " ".join(comments)

    def hint_for(self, player):
        return self.hints.get(player, "...")

    def draw(self, surf):
        bx, by = W//2, 65
        # 荷官轻微晃动
        bob = math.sin(pygame.time.get_ticks() * 0.002) * 2
        by += int(bob)
        pygame.draw.ellipse(surf, (70,44,24), (bx-260, by+80, 520, 60))
        if IMG_DEALER:
            surf.blit(IMG_DEALER, (bx-80, by-10))
        else:
            pygame.draw.polygon(surf, C_LEATHER, [(bx-36,by+72),(bx+36,by+72),(bx+48,by-8),(bx-48,by-8)])
            pygame.draw.circle(surf, (200,172,132), (bx, by-22), 20)
        # 金币袋脉动
        gold_pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.004)
        pygame.draw.circle(surf, C_GOLD, (bx+70, by+50), int(16 * gold_pulse))
        draw_text(surf, str(self.gold), FONT_S, C_LEATHER_D, bx+70, by+50, center=True, shadow=False)
        bw, bh = 560, 96
        b = pygame.Rect(bx-bw//2, by+96, bw, bh)
        draw_rounded(surf, b, 12, (245,238,214), C_LEATHER, 2)
        pygame.draw.polygon(surf, (245,238,214), [(bx-8,by+92),(bx+8,by+92),(bx,by+102)])
        draw_text(surf, "Dealer", FONT_B, C_LEATHER_D, b.x+14, b.y+8)
        draw_text(surf, f"Gold: {self.gold}", FONT_B, C_BLOOD, b.right-120, b.y+10)
        words = self.speech.split()
        line, yy = "", b.y+40
        for w in words:
            if FONT.size(line+w)[0] > bw-28:
                draw_text(surf, line, FONT, C_LEATHER_D, b.x+14, yy, shadow=False)
                line, yy = w, yy+24
            else:
                line += (" " if line else "") + w
        if line:
            draw_text(surf, line, FONT, C_LEATHER_D, b.x+14, yy, shadow=False)

# ═════════════════════════════════════════════════════════════════════
#  Game State Machine
# ═════════════════════════════════════════════════════════════════════
PHASE_ORDER = ['menu','contract','select','bribe','betting','reveal','shooting','round_end','gameover']
MAX_RAISES = 3  # 最多加注次数

class Game:
    def __init__(self):
        self.reset_all()
    def reset_all(self):
        self.p1 = Player("Player 1 — Snake", 'left', 'snake')
        self.p2 = Player("Player 2 — Lizard", 'right', 'lizard')
        self.dealer = Dealer()
        self.particles = Particles()
        self.phase = 'menu'
        self.round_num = 0
        # ── 三局两胜换边制 ──
        self.match_round = 1          # 当前第几局
        self.p1_match_wins = 0       # P1胜场数
        self.p2_match_wins = 0       # P2胜场数
        self.match_round_winner = None  # 本局胜者（None=未结算/平局）
        self.match_final_over = False    # 是否最终分出胜负
        self.match_winner = None         # 最终胜者
        self.message = "Welcome to the deadliest saloon in the West. Press START to begin."
        self.message_timer = 0
        self.shoot_target = None
        self.shoot_anim = 0
        self.current_player = None
        self.bribe_input = None
        self.buttons = {}
        self.turn_announce_timer = 0
        # 加注阶段状态
        self.bet_current = 0       # 当前下注额
        self.bet_mode = None       # 当前规则 big/small
        self.bet_turn = None       # 当前叫价方
        self.raise_count = 0       # 加注次数
        self.bet_input = None
        self.flash_alpha = 0
        self.blood_alpha = 0
        self.screen_shake = 0
        self.muzzle_flash = 0
        # ── 动态效果增强状态 ──
        self.card_anims = {}          # 卡牌飞行动画 {player: {x,y,tx,ty,progress,card}}
        self.flip_anim = 0.0          # 翻牌动画进度 0~1
        self.flip_target = None       # 翻牌目标阶段
        self.cylinder_angle = 0       # 转轮旋转角度
        self.cylinder_spinning = False # 转轮是否在旋转
        self.cylinder_spin_speed = 0  # 转轮旋转速度
        self.bg_dust_timer = 0        # 背景尘土生成计时
        self.phase_fade = 0.0         # 阶段过渡淡入淡出 0~1
        self.phase_fade_dir = 0       # -1=淡出, 1=淡入, 0=无
        self.gold_burst_pos = None    # 金币爆发位置
        self.gold_burst_timer = 0
        self.dealer_bob = 0.0         # 荷官轻微晃动
        self.card_hover_player = None # 当前悬停卡牌的玩家
        self.slow_motion = 0          # 慢动作因子(命中时)

    def new_round(self):
        self.round_num += 1
        for p in (self.p1, self.p2):
            p.selected_card = None
            p.round_bet = 0
            p.bribe_amount = 0
            p.bribe_strategy = 'trick'
            p.pending_play = None
            p.private_hint = "..."
            p.set_mood("normal")
        self.dealer.reset()
        self.shoot_target = None
        self.shoot_anim = 0
        self.bet_current = 0
        self.bet_mode = None
        self.raise_count = 0
        self.flash_alpha = 0
        self.blood_alpha = 0
        self.screen_shake = 0
        self.card_anims = {}
        self.flip_anim = 0.0
        self.cylinder_angle = 0
        self.cylinder_spinning = False
        self.cylinder_spin_speed = 0
        self.gold_burst_pos = None
        self.gold_burst_timer = 0
        self.slow_motion = 0
        self._start_select()

    def _swap_and_next_match_round(self):
        """换边：交换P1/P2身份，重置状态，开始下一局"""
        # 交换p1和p2（先手变成后手，后手变成先手）
        self.p1, self.p2 = self.p2, self.p1
        # 设置座位：先手(P1)总是在左边，后手(P2)总是在右边
        self.p1.side = 'left'
        self.p2.side = 'right'
        # 重置玩家状态（每局都是50金币、6张牌）
        self.p1.reset()
        self.p2.reset()
        # 重置dealer
        self.dealer.reset()
        # 局数+1
        self.match_round += 1
        # 重置本局胜者标记
        self.match_round_winner = None
        # 重置回合数，开始新的一局
        self.round_num = 0
        self.message = f"Round {self.match_round} — Swap sides! {self.p1.name} goes first."
        self.new_round()

    def _announce_turn(self, player, action):
        self.current_player = player
        self.turn_announce_timer = 120
        self.message = f"{player.name}'s turn — {action}. Other player, look away!"

    # ── Select Phase ───────────────────────────────────────────────
    def _start_select(self):
        self.phase = 'select'
        self._announce_turn(self.p1, "choose a card to play")
        self.buttons = {}
        self.buttons['play_btn'] = Button(W//2-100, 720, 200, 50, "Confirm Play", font=FONT_B, col=C_RUST, hot=C_BLOOD)

    def _select_next(self):
        if self.current_player == self.p1:
            self._announce_turn(self.p2, "choose a card to play")
        else:
            self.current_player = None
            # 选牌结束，进入贿赂阶段（第1轮跳过贿赂）
            if self.round_num == 1:
                self.dealer.speech = "First round... no bribes needed. May the odds be ever in yer favor."
                for p in (self.p1, self.p2):
                    p.private_hint = self.dealer._card_hint_vague()
                self._start_betting()
            else:
                self._start_bribe()

    # ── Bribe Phase ────────────────────────────────────────────────
    def _start_bribe(self):
        self.phase = 'bribe'
        self.dealer.beg(self.round_num)
        self._announce_turn(self.p1, "enter your bribe (0 = skip)")
        self.bribe_input = InputBox(W//2-70, 640, 140, 56, 0, 0, self.p1.gold, "Bribe Gold")
        self.buttons = {}
        self.buttons['strat'] = Button(W//2+60, 710, 160, 40, "Strat: TRICK")
        self.buttons['bribe_ok'] = Button(W//2-100, 760, 200, 44, "Confirm Bribe", font=FONT_B, col=C_RUST, hot=C_BLOOD)

    def _bribe_next(self):
        if self.current_player == self.p1:
            amt = max(0, min(self.p1.gold, self.bribe_input.value))
            self.p1.bribe_amount = amt
            self.p1.gold -= amt
            if amt > 0:
                self.particles.emit_gold(self.p1.cx, 400, min(20, amt//2+5), W//2, 100)
            self._announce_turn(self.p2, "enter your bribe (0 = skip)")
            self.bribe_input = InputBox(W//2-70, 640, 140, 56, 0, 0, self.p2.gold, "Bribe Gold")
            self.buttons['strat'].text = "Strat: TRICK"
            self.p2.bribe_strategy = 'trick'
        else:
            amt = max(0, min(self.p2.gold, self.bribe_input.value))
            self.p2.bribe_amount = amt
            self.p2.gold -= amt
            if amt > 0:
                self.particles.emit_gold(self.p2.cx, 400, min(20, amt//2+5), W//2, 100)
            # 结算贿赂，生成情报
            self.dealer.collect_and_resolve(self.p1, self.p2)
            self.p1.private_hint = self.dealer.hint_for(self.p1)
            self.p2.private_hint = self.dealer.hint_for(self.p2)
            self.bribe_input = None
            self._start_betting()

    # ── Betting Phase (call/raise) ─────────────────────────────────
    def _start_betting(self):
        self.phase = 'betting'
        self.bet_turn = self.p1
        self.raise_count = 0
        self.bet_current = 0
        self.bet_mode = None
        self._build_bet_ui(opening=True)
        self.message = f"Betting: {self.bet_turn.name}'s turn — call HIGH/LOW + bet"

    def _build_bet_ui(self, opening=False):
        max_bet = self.bet_turn.gold
        if opening:
            # 开局叫价：选规则+下注（0金也能叫价，只是不下注）
            min_bet = 1 if max_bet > 0 else 0
            self.bet_input = InputBox(W//2-70, 620, 140, 52, min_bet, min_bet, max_bet, "Bet Gold")
            self.buttons['mode'] = Button(W//2-180, 690, 120, 40, "Mode: HIGH")
            self.buttons['call'] = Button(W//2-100, 750, 200, 50, "PLACE BET", font=FONT_B, col=C_RUST, hot=C_BLOOD)
        else:
            # 跟注/加注：加注必须大于当前下注
            min_raise = self.bet_current + 1
            self.bet_input = InputBox(W//2-70, 620, 140, 52, min_raise, min_raise, max_bet, "Raise To")
            self.buttons['call'] = Button(W//2-180, 700, 140, 50, "CALL", font=FONT_B, col=C_GREEN, hot=(80,140,80))
            self.buttons['raise'] = Button(W//2+40, 700, 140, 50, "RAISE & FLIP", font=FONT_B, col=C_RUST, hot=C_BLOOD)

    def _clear_bet_ui(self):
        self.bet_input = None
        for k in ('mode','call','raise'):
            self.buttons.pop(k, None)

    def _place_opening_bet(self):
        """玩家1开局叫价"""
        amt = max(0, min(self.bet_turn.gold, self.bet_input.value))
        mode = self.buttons['mode'].text.split(':')[1].strip().lower()
        self.bet_mode = 'big' if mode == 'high' else 'small'
        self.bet_current = amt
        self.bet_turn.gold -= amt
        self.bet_turn.round_bet += amt
        self.particles.emit_gold(self.p1.cx, 500, min(15, amt//3+3), W//2, 580)
        self.raise_count = 0
        # 荷官评论
        self.dealer.betting_commentary(self.p1, self.p2, self.bet_mode, self.bet_current, 0)
        # 轮到玩家2
        self.bet_turn = self.p2
        self._build_bet_ui(opening=False)
        self.message = f"{self.p1.name} calls {'HIGH' if self.bet_mode=='big' else 'LOW'} with {amt}g. {self.p2.name}: CALL or RAISE?"

    def _call_bet(self):
        """跟注：支付差额，接受当前规则"""
        owed = self.bet_current - self.bet_turn.round_bet
        owed = max(0, min(owed, self.bet_turn.gold))
        self.bet_turn.gold -= owed
        self.bet_turn.round_bet += owed
        if owed > 0:
            self.particles.emit_gold(self.bet_turn.cx, 500, min(12, owed//3+2), W//2, 580)
        self._finish_betting()

    def _raise_bet(self):
        """加注：支付到新金额，翻转规则"""
        new_amt = max(self.bet_current + 1, min(self.bet_turn.gold, self.bet_input.value))
        # 翻转规则
        self.bet_mode = 'small' if self.bet_mode == 'big' else 'big'
        # 支付差额
        owed = new_amt - self.bet_turn.round_bet
        owed = max(0, min(owed, self.bet_turn.gold))
        self.bet_turn.gold -= owed
        self.bet_turn.round_bet += owed
        if owed > 0:
            self.particles.emit_gold(self.bet_turn.cx, 500, min(15, owed//3+3), W//2, 580)
        self.bet_current = new_amt
        self.raise_count += 1
        # 荷官评论
        commentator = self.bet_turn
        self.dealer.betting_commentary(self.p1, self.p2, self.bet_mode, self.bet_current, self.raise_count)
        # 切换到对手
        self.bet_turn = self.p2 if self.bet_turn == self.p1 else self.p1
        # 检查是否达到最大加注次数
        if self.raise_count >= MAX_RAISES:
            # 强制跟注
            owed = self.bet_current - self.bet_turn.round_bet
            owed = max(0, min(owed, self.bet_turn.gold))
            self.bet_turn.gold -= owed
            self.bet_turn.round_bet += owed
            self.message = f"Max raises reached! {self.bet_turn.name} must call."
            self._finish_betting()
        else:
            self._build_bet_ui(opening=False)
            self.message = f"{commentator.name} raises to {new_amt}g and flips to {'HIGH' if self.bet_mode=='big' else 'LOW'}! {self.bet_turn.name}: CALL or RAISE?"

    def _finish_betting(self):
        self._clear_bet_ui()
        self.phase = 'reveal'
        self.message_timer = 150
        self.flip_anim = 0.0  # 启动翻牌动画
        mode_name = 'HIGH' if self.bet_mode == 'big' else 'LOW'
        total_destroyed = self.p1.round_bet + self.p2.round_bet + self.p1.bribe_amount + self.p2.bribe_amount
        self.message = f"REVEAL! Mode: {mode_name}. {total_destroyed}g destroyed to the crows."

    # ── Resolve Round ──────────────────────────────────────────────
    def _resolve_round(self):
        c1, c2 = self.p1.selected_card, self.p2.selected_card
        mode = self.bet_mode
        if (mode=='big' and c1>c2) or (mode=='small' and c1<c2):
            winner, loser = self.p1, self.p2
        elif (mode=='big' and c1<c2) or (mode=='small' and c1>c2):
            winner, loser = self.p2, self.p1
        else:
            self.message = f"TIE! Both played {c1}. Cards consumed, no one shoots."
            self.p1.set_mood("normal")
            self.p2.set_mood("normal")
            self.phase = 'round_end'
            return
        mode_name = 'HIGH' if mode == 'big' else 'LOW'
        self.message = (f"{winner.name} wins ({mode_name} mode)! {loser.name} points the gun at themselves "
                       f"({loser.selected_card} bullets, {loser.selected_card*100//6}% hit chance)")
        winner.set_mood("victory")
        loser.set_mood("scared")
        self.shoot_target = loser
        self.phase = 'shooting'
        self.shoot_anim = 180
        # 启动转轮旋转动画
        self.cylinder_spinning = True
        self.cylinder_spin_speed = 0.6
        self.cylinder_angle = 0
        audio.play('cylinder_spin.wav')

    def _check_gameover(self):
        return (not self.p1.alive) or (not self.p2.alive) or \
               (len(self.p1.hand)==0) or (len(self.p2.hand)==0)

    # ── Events ─────────────────────────────────────────────────────
    def handle(self, ev):
        if self.phase == 'menu':
            if 'start' in self.buttons and self.buttons['start'].check(ev):
                audio.play('button_click.wav')
                self.phase = 'contract'
                self.buttons = {}
        elif self.phase == 'contract':
            if 'accept' in self.buttons and self.buttons['accept'].check(ev):
                audio.play('button_click.wav')
                self.new_round()
        elif self.phase == 'bribe':
            if self.bribe_input: self.bribe_input.handle(ev)
            cp = self.current_player
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 'strat' in self.buttons and self.buttons['strat'].rect.collidepoint(ev.pos):
                    audio.play('button_click.wav')
                    cp.bribe_strategy = 'honest' if cp.bribe_strategy=='trick' else 'trick'
                    self.buttons['strat'].text = f"Strat: {'TRICK' if cp.bribe_strategy=='trick' else 'HONEST'}"
            if 'bribe_ok' in self.buttons and self.buttons['bribe_ok'].check(ev):
                audio.play('button_click.wav')
                self._bribe_next()
        elif self.phase == 'select':
            cp = self.current_player
            if ev.type == pygame.MOUSEBUTTONDOWN and cp and cp.alive:
                for rect, num in cp.card_rects:
                    if rect.collidepoint(ev.pos):
                        audio.play('card_flip.wav')
                        cp.pending_play = num if cp.pending_play != num else None
                        return
            if 'play_btn' in self.buttons and self.buttons['play_btn'].check(ev):
                if cp and cp.pending_play is not None:
                    audio.play('card_throw.wav')
                    cp.selected_card = cp.pending_play
                    # 启动飞牌动画：从手牌位置飞到桌面
                    hand_y = 290 + 470 - CARD_H - 14
                    start_x = cp.cx
                    target_x = W//2 - 200 if cp.is_left else W//2 + 110
                    self.card_anims[id(cp)] = {
                        "x": start_x, "y": hand_y,
                        "tx": target_x, "ty": 470,
                        "progress": 0.0, "card": cp.selected_card,
                        "player": cp, "face_up": False
                    }
                    cp.hand.remove(cp.pending_play)
                    cp.pending_play = None
                    self.message = f"{cp.name} has played a card."
                    self._select_next()
        elif self.phase == 'reveal':
            pass
        elif self.phase == 'betting':
            if self.bet_input: self.bet_input.handle(ev)
            if self.raise_count == 0 and self.bet_turn == self.p1:
                # 开局叫价
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if 'mode' in self.buttons and self.buttons['mode'].rect.collidepoint(ev.pos):
                        audio.play('button_click.wav')
                        cur = self.buttons['mode'].text
                        self.buttons['mode'].text = "Mode: LOW" if "HIGH" in cur else "Mode: HIGH"
                if 'call' in self.buttons and self.buttons['call'].check(ev):
                    audio.play('gold_drop.wav')
                    self._place_opening_bet()
            else:
                # 跟注/加注
                if 'call' in self.buttons and self.buttons['call'].check(ev):
                    audio.play('gold_drop.wav')
                    self._call_bet()
                elif 'raise' in self.buttons and self.buttons['raise'].check(ev):
                    audio.play('gold_drop.wav')
                    self._raise_bet()
        elif self.phase == 'round_end':
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                if self._check_gameover(): self.phase = 'gameover'
                else: self.new_round()
        elif self.phase == 'gameover':
            if 'restart' in self.buttons and self.buttons['restart'].check(ev):
                audio.play('button_click.wav')
                if self.match_final_over:
                    self.reset_all()
                else:
                    self._swap_and_next_match_round()
            # 最终结束后按 A 键查看数学真相
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_a and self.match_final_over:
                audio.play('button_click.wav')
                self.phase = 'analysis'
                self.analysis_page = 0
        elif self.phase == 'analysis':
            # 数学分析界面：按 A/D 或左右箭头翻页，按 ESC/空格返回
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_d, pygame.K_RIGHT):
                    self.analysis_page = min(55, self.analysis_page + 1)
                    audio.play('card_flip.wav')
                elif ev.key in (pygame.K_a, pygame.K_LEFT):
                    self.analysis_page = max(0, self.analysis_page - 1)
                    audio.play('card_flip.wav')
                elif ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    self.phase = 'gameover'
                    audio.play('button_click.wav')

    # ── Update ─────────────────────────────────────────────────────
    def update(self):
        # 慢动作因子：命中时减速
        dt = 0.35 if self.slow_motion > 0 else 1.0
        if self.slow_motion > 0:
            self.slow_motion -= 1

        self.particles.update()
        # 背景尘土持续生成
        self.bg_dust_timer += 1
        if self.bg_dust_timer >= 8:
            self.bg_dust_timer = 0
            self.particles.emit_dust(random.randint(100, W-100), random.randint(300, 600), 2)
        # 荷官轻微晃动
        self.dealer_bob = math.sin(pygame.time.get_ticks() * 0.002) * 3

        if self.turn_announce_timer > 0:
            self.turn_announce_timer -= 1
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.phase == 'reveal':
                self._resolve_round()

        # ── 卡牌飞行动画更新 ──
        anims_to_remove = []
        for key, anim in self.card_anims.items():
            anim["progress"] += 0.04 * dt
            if anim["progress"] >= 1.0:
                anim["progress"] = 1.0
                anims_to_remove.append(key)
            # 缓动函数：ease-out cubic
            t = anim["progress"]
            ease = 1 - (1 - t) ** 3
            anim["cur_x"] = anim["x"] + (anim["tx"] - anim["x"]) * ease
            # 抛物线弧度
            arc_height = -80 * math.sin(t * math.pi)
            anim["cur_y"] = anim["y"] + (anim["ty"] - anim["y"]) * ease + arc_height
            anim["cur_rot"] = (1 - ease) * 360  # 飞行中旋转
        for key in anims_to_remove:
            del self.card_anims[key]

        # ── 翻牌动画更新 ──
        if self.phase == 'reveal' and self.flip_anim < 1.0:
            self.flip_anim += 0.035 * dt
            if self.flip_anim > 1.0:
                self.flip_anim = 1.0

        # ── 转轮旋转动画更新 ──
        if self.cylinder_spinning:
            self.cylinder_angle += self.cylinder_spin_speed * dt
            self.cylinder_spin_speed *= 0.985  # 逐渐减速
            if self.cylinder_spin_speed < 0.05:
                self.cylinder_spinning = False
                self.cylinder_spin_speed = 0

        if self.phase == 'shooting' and self.shoot_target:
            self.shoot_anim -= 1
            t = 180 - self.shoot_anim
            if t == 25:
                self.muzzle_flash = 15
                self.screen_shake = 8
                # 枪口火花+烟雾
                gx = W//2 + (-180 if self.shoot_target.is_left else 180)
                self.particles.emit_spark(gx, 460, 25)
                self.particles.emit_smoke(gx, 450, 12)
            if t == 30:
                bullet = self.shoot_target.selected_card
                hit = random.random() < bullet/6.0
                if hit:
                    audio.play('gunshot.wav')
                    self.shoot_target.alive = False
                    self.shoot_target.set_mood("dead")
                    self.flash_alpha = 255
                    self.blood_alpha = 255
                    self.screen_shake = 25
                    self.slow_motion = 40  # 命中时慢动作
                    self.particles.emit(W//2, H//2-40, C_BLOOD, 120, 16, 70)
                    self.particles.emit(W//2, H//2-40, (200,50,50), 60, 10, 50)
                    self.message = f"{self.shoot_target.name} takes a bullet to the skull! DEAD"
                    other = self.p2 if self.shoot_target==self.p1 else self.p1
                    other.set_mood("victory")
                else:
                    audio.play('empty_chamber.wav')
                    self.shoot_target.set_mood("survivor")
                    self.screen_shake = 12
                    self.particles.emit(W//2, H//2-40, (220,200,120), 70, 12, 50)
                    self.particles.emit(W//2, H//2-40, (180,180,180), 40, 6, 40)
                    self.message = f"{self.shoot_target.name} survives by the skin of their teeth!"
                    other = self.p2 if self.shoot_target==self.p1 else self.p1
                    other.set_mood("normal")
            if self.shoot_anim <= 0:
                self.phase = 'round_end' if not self._check_gameover() else 'gameover'
        if self.flash_alpha > 0: self.flash_alpha = max(0, self.flash_alpha-12)
        if self.blood_alpha > 0: self.blood_alpha = max(0, self.blood_alpha-2)
        if self.screen_shake > 0: self.screen_shake = max(0, self.screen_shake-1)
        if self.muzzle_flash > 0: self.muzzle_flash -= 1

    # ── Draw ───────────────────────────────────────────────────────
    def draw(self, surf):
        canvas = pygame.Surface((W, H))
        canvas.fill((0,0,0))
        self._draw_bg(canvas)
        if self.phase == 'contract':
            self._draw_ui(canvas)
            surf.blit(canvas, (0,0))
            return
        self.dealer.draw(canvas)
        in_turn_phase = self.phase in ('bribe','select')
        p1_active = in_turn_phase and self.current_player == self.p1
        p2_active = in_turn_phase and self.current_player == self.p2
        reveal_cards = self.phase in ('reveal','gameover')
        played_revealed = self.phase in ('reveal','shooting','round_end','gameover')
        # 自己的金币可见，对手的金币隐藏（在非自己回合时）
        p1_show_gold = p1_active or self.phase in ('reveal','shooting','round_end','gameover','menu','betting')
        p2_show_gold = p2_active or self.phase in ('reveal','shooting','round_end','gameover','menu','betting')
        self.p1.draw(canvas, is_active=p1_active, reveal_cards=reveal_cards, played_revealed=played_revealed, show_gold=p1_show_gold)
        self.p2.draw(canvas, is_active=p2_active, reveal_cards=reveal_cards, played_revealed=played_revealed, show_gold=p2_show_gold)
        self._draw_table(canvas)
        # 绘制飞行中的卡牌
        for anim in self.card_anims.values():
            if "cur_x" in anim:
                cx, cy = anim["cur_x"], anim["cur_y"]
                rot = anim.get("cur_rot", 0)
                card_img = IMG_CARD_BACK  # 飞行中背面朝上
                if card_img:
                    rotated = pygame.transform.rotate(card_img, rot)
                    rw, rh = rotated.get_size()
                    canvas.blit(rotated, (int(cx - rw//2), int(cy - rh//2)))
                # 飞行轨迹粒子
                if random.random() < 0.3 and hasattr(self, 'particles'):
                    self.particles.emit_dust(cx, cy, 1)
        if self.muzzle_flash > 0 and self.shoot_target:
            gx = W//2 + (-180 if self.shoot_target.is_left else 180)
            mf_alpha = int(255 * (self.muzzle_flash / 15))
            mf = make_alpha_surf(120, 80, (255,220,100), mf_alpha)
            canvas.blit(mf, (gx-60, 440))
        if hasattr(self, 'particles'):
            self.particles.draw(canvas)
        self._draw_ui(canvas)
        self._draw_topbar(canvas)
        if self.turn_announce_timer > 0 and self.current_player:
            # 滑入动画：前30帧从左侧滑入
            slide_progress = min(1.0, (120 - self.turn_announce_timer) / 30.0)
            slide_offset = int((1 - slide_progress) * -W * 0.6)
            alpha = min(255, self.turn_announce_timer * 4)
            banner_y = H//2 - 40
            banner = make_alpha_surf(W, 80, C_BROWN, min(220, alpha))
            canvas.blit(banner, (slide_offset, banner_y))
            # 金色边框线
            pygame.draw.line(canvas, C_GOLD, (slide_offset, banner_y), (slide_offset+W, banner_y), 3)
            pygame.draw.line(canvas, C_GOLD, (slide_offset, banner_y+80), (slide_offset+W, banner_y+80), 3)
            name = self.current_player.name
            # 文字脉动
            text_scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.008)
            banner_font = pygame.font.SysFont("georgia", int(44 * text_scale), bold=True, italic=True)
            draw_text(canvas, f"{name}'S TURN", banner_font, C_GOLD_L, W//2 + slide_offset, H//2, center=True)
        if self.screen_shake > 0:
            ox = random.randint(-self.screen_shake, self.screen_shake)
            oy = random.randint(-self.screen_shake, self.screen_shake)
        else:
            ox, oy = 0, 0
        surf.blit(canvas, (ox, oy))
        if self.flash_alpha > 0:
            f = pygame.Surface((W,H)); f.fill((255,255,255))
            f.set_alpha(self.flash_alpha); surf.blit(f, (0,0))
        if self.blood_alpha > 0:
            b = pygame.Surface((W,H)); b.fill((120,10,10))
            b.set_alpha(self.blood_alpha); surf.blit(b, (0,0))

    def _draw_bg(self, surf):
        if self.phase == 'menu' and IMG_BG_MENU:
            surf.blit(IMG_BG_MENU, (0,0))
        elif IMG_BG_GAME:
            surf.blit(IMG_BG_GAME, (0,0))
            dim = make_alpha_surf(W, H, (10,5,2), 100)
            surf.blit(dim, (0,0))
        else:
            for y in range(0, 280, 4):
                t = y/280
                pygame.draw.rect(surf, (int(60+t*40), int(46+t*20), int(38+t*10)), (0,y,W,4))
            pygame.draw.rect(surf, C_SAND, (0,280,W,H-280))
        pygame.draw.ellipse(surf, (92,60,34), (60, 440, W-120, 300))
        pygame.draw.ellipse(surf, (120,82,46), (80, 450, W-160, 270))
        for i in range(6):
            yy = 480 + i*36
            pygame.draw.arc(surf, (78,50,28), (160, yy-8, W-320, 28), 0, math.pi, 2)

    def _draw_table(self, surf):
        cx = W//2
        # 转轮旋转动画
        if IMG_ROULETTE and self.phase in ('shooting','round_end','reveal','betting'):
            cyl_img = IMG_ROULETTE
            if self.cylinder_spinning or self.cylinder_angle != 0:
                cyl_img = pygame.transform.rotate(IMG_ROULETTE, math.degrees(self.cylinder_angle))
            rw, rh = cyl_img.get_size()
            surf.blit(cyl_img, (cx - rw//2, 370 + (140 - rh)//2))
            # 旋转时加发光
            if self.cylinder_spinning:
                glow = make_alpha_surf(rw+20, rh+20, C_GOLD_L, 30)
                surf.blit(glow, (cx - rw//2 - 10, 370 + (140-rh)//2 - 10))
        if self.phase in ('reveal','betting','shooting','round_end'):
            cards_up = self.phase in ('reveal','shooting','round_end')
            # 应用翻牌动画
            flip_p = self.flip_anim if self.phase == 'reveal' else 1.0
            if self.p1.selected_card is not None:
                draw_card(surf, self.p1.selected_card, cx-200, 470, face_up=cards_up, scale=1.1, flip_progress=0 if cards_up else 0)
            if self.p2.selected_card is not None:
                draw_card(surf, self.p2.selected_card, cx+110, 470, face_up=cards_up, scale=1.1, flip_progress=0 if cards_up else 0)
            # 翻牌动画期间，在桌面位置绘制翻转中的卡牌
            if self.phase == 'reveal' and 0 < flip_p < 1:
                if self.p1.selected_card is not None:
                    draw_card(surf, self.p1.selected_card, cx-200, 470, face_up=True, scale=1.1, flip_progress=flip_p)
                if self.p2.selected_card is not None:
                    draw_card(surf, self.p2.selected_card, cx+110, 470, face_up=True, scale=1.1, flip_progress=flip_p)
            if self.bet_mode and cards_up:
                mode_txt = "HIGH" if self.bet_mode=='big' else "LOW"
                # 模式文字脉动效果
                pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
                mode_font = pygame.font.SysFont("georgia", int(44 * pulse), bold=True, italic=True)
                draw_text(surf, mode_txt, mode_font, C_BLOOD, cx, 420, center=True)
        pot = self.p1.round_bet + self.p2.round_bet
        if pot > 0 or self.phase == 'betting':
            destroyed = self.p1.round_bet + self.p2.round_bet + self.p1.bribe_amount + self.p2.bribe_amount
            draw_text(surf, f"Pot: {pot}g bet + {self.p1.bribe_amount + self.p2.bribe_amount}g bribed = {destroyed}g DESTROYED",
                      FONT_B, C_GOLD, cx, 628, center=True)

    def _draw_topbar(self, surf):
        bar = pygame.Rect(10, 8, W-20, 52)
        draw_rounded(surf, bar, 10, (*C_BROWN[:3], 220), C_LEATHER, 2)
        draw_text(surf, f"R{self.match_round} | {self.p1_match_wins}-{self.p2_match_wins}", FONT_B, C_GOLD_L, 30, 34)
        phase_cn = {
            'menu':'Menu','bribe':'Bribe','select':'Select',
            'reveal':'Reveal','betting':'Betting','shooting':'Shooting',
            'round_end':'Round End','gameover':'Game Over'
        }
        draw_text(surf, f"Phase: {phase_cn.get(self.phase,'')}", FONT_B, C_BONE, 180, 34)
        draw_text(surf, self.message, FONT, C_BONE, W//2, 34, center=True)
        draw_text(surf, f"Dealer: {self.dealer.gold}g", FONT_S, C_GOLD, W-40, 34, center=True)
        # 静音提示
        if audio.muted:
            draw_text(surf, "[M] UNMUTE", FONT_XS, C_BLOOD, W-130, 34, center=True)

    def _draw_ui(self, surf):
        cx = W//2
        if self.phase == 'menu':
            # 菜单背景粒子
            if random.random() < 0.2:
                self.particles.emit_dust(random.randint(0, W), random.randint(400, 700), 1)
            self.buttons['start'] = Button(cx-140, H//2+80, 280, 72, "START GAME", font=FONT_H, col=C_RUST, hot=C_BLOOD)
            self.buttons['start'].draw(surf)
            # 标题脉动效果
            t = pygame.time.get_ticks()
            bullet_scale = 1.0 + 0.04 * math.sin(t * 0.004)
            bullet_font = pygame.font.SysFont("georgia", int(44 * bullet_scale), bold=True, italic=True)
            draw_text(surf, "BULLET", bullet_font, C_GOLD, cx, H//2-140, center=True)
            cards_scale = 1.0 + 0.04 * math.sin(t * 0.004 + 0.5)
            cards_font = pygame.font.SysFont("georgia", int(44 * cards_scale), bold=True, italic=True)
            draw_text(surf, "CARDS", cards_font, C_BLOOD, cx, H//2-70, center=True)
            draw_text(surf, "Doomsday Western — Two-Player Duel", FONT_T, C_BONE, cx, H//2-10, center=True)
            # 副标题闪烁
            sub_alpha = 180 + int(75 * math.sin(t * 0.003))
            sub_color = (min(255, C_GOLD_L[0]), min(255, C_GOLD_L[1]), min(255, C_GOLD_L[2]))
            draw_text(surf, "Snake vs Lizard  \u2022  Bribe  \u2022  Bluff  \u2022  Survive", FONT_B, sub_color, cx, H//2+30, center=True)
        elif self.phase == 'contract':
            paper = pygame.Rect(cx-420, 60, 840, 620)
            draw_rounded(surf, paper, 16, (210, 185, 140), C_BLOOD, 4)
            inner = pygame.Rect(paper.x+14, paper.y+14, paper.w-28, paper.h-28)
            pygame.draw.rect(surf, (180, 150, 105), inner, 2, border_radius=10)
            for bx, by, br in [(cx-380, 100, 18), (cx+360, 140, 14), (cx-340, 620, 12), (cx+380, 580, 16)]:
                pygame.draw.circle(surf, (*C_BLOOD[:3], 100), (bx, by), br)
            draw_text(surf, "~ BLOOD CONTRACT ~", FONT_H, C_BLOOD, cx, 90, center=True)
            draw_text(surf, "Doomsday Western Duel", FONT_T, C_LEATHER_D, cx, 138, center=True)
            pygame.draw.line(surf, C_BLOOD, (cx-220, 168), (cx+220, 168), 2)
            rules = [
                "1.  Each gunslinger rides in with 50 gold and six bullets (cards 1-6).",
                "2.  Turn-based: Player 1 (Snake) always draws first. The foe's hand stays",
                "    face-down — a real cowboy don't peek at another man's hand.",
                "3.  Each showdown: Pick yer card -> Bribe the dealer -> Call HIGH/LOW",
                "    -> Opponent CALLs or RAISEs to flip -> Reveal -> Loser shoots.",
                "4.  The loser points the revolver at his own skull. Bullets in the",
                "    chamber = card value.  Death comes calling at value / 6 odds.",
                "5.  Bribe the owl dealer. The highest bidder hears the truth straight,",
                "    and can order the dealer to LIE or tell the TRUTH to the fool.",
                "6.  All gold bet or bribed feeds the crows — never returned, never shared.",
                "7.  Opponent's total gold is secret. Only bets are public. Bribes are hidden.",
                "8.  A bullet to the brain, or an empty gun belt, means you're pushing up",
                "    daisies.  The last man standing walks away with the saloon.",
                "",
                "    Sign below if you're man enough to accept your fate...",
            ]
            ry = 188
            for line in rules:
                col = C_BLOOD if line.startswith("    Sign") else C_LEATHER_D
                f = FONT_B if line.startswith("    Sign") else FONT_S
                draw_text(surf, line, f, col, cx-390, ry, shadow=False)
                ry += 26
            self.buttons['accept'] = Button(cx-160, 640, 320, 56, "I ACCEPT THE CONTRACT",
                                              font=FONT_B, col=C_BLOOD, hot=(180,30,30), txt_col=C_BONE)
            self.buttons['accept'].draw(surf)
        elif self.phase == 'select':
            if 'play_btn' in self.buttons: self.buttons['play_btn'].draw(surf)
            draw_text(surf, "Click a card to select, then press 'Confirm Play'", FONT_B, C_BONE, cx, 770, center=True)
        elif self.phase == 'bribe':
            if self.bribe_input: self.bribe_input.draw(surf)
            if 'strat' in self.buttons: self.buttons['strat'].draw(surf)
            if 'bribe_ok' in self.buttons: self.buttons['bribe_ok'].draw(surf)
            draw_text(surf, f"\U0001f3a9 {self.dealer.speech}", FONT_B, C_GOLD, cx, 560, center=True)
            draw_text(surf, "TRICK = lie to opponent | HONEST = tell truth (reverse psychology)",
                      FONT_XS, C_BONE, cx, 800-24, center=True)
            draw_text(surf, "Bribe amount is SECRET — opponent only sees your public bets.",
                      FONT_XS, (180,160,130), cx, 800-8, center=True)
        elif self.phase == 'betting':
            if self.bet_input: self.bet_input.draw(surf)
            for k in ('mode','call','raise'):
                if k in self.buttons: self.buttons[k].draw(surf)
            if self.bet_turn:
                draw_text(surf, f"Current: {self.bet_turn.name}", FONT_T, C_GOLD, cx, 575, center=True)
            if self.bet_mode:
                mode_txt = "HIGH" if self.bet_mode=='big' else "LOW"
                draw_text(surf, f"Mode: {mode_txt} | Current Bet: {self.bet_current}g | Raises: {self.raise_count}/{MAX_RAISES}",
                          FONT_B, C_BLOOD, cx, 600, center=True)
            if self.raise_count == 0 and self.bet_turn == self.p1:
                draw_text(surf, "Choose HIGH/LOW, set bet amount, then PLACE BET",
                          FONT_S, C_BONE, cx, 770, center=True)
            else:
                draw_text(surf, "CALL = accept rule & pay difference | RAISE = flip rule & bet more",
                          FONT_S, C_BONE, cx, 770, center=True)
        elif self.phase == 'round_end':
            draw_text(surf, "Press [SPACE] for next round", FONT_T, C_GOLD, cx, H//2+120, center=True)
        elif self.phase == 'gameover':
            overlay = make_alpha_surf(W, H, (20,10,10), 180)
            surf.blit(overlay, (0,0))
            # 第一次进入时结算本局胜者
            if self.match_round_winner is None and not self.match_final_over:
                if not self.p1.alive:
                    self.match_round_winner = self.p2
                    round_reason = "Snake took a bullet"
                elif not self.p2.alive:
                    self.match_round_winner = self.p1
                    round_reason = "Lizard took a bullet"
                elif len(self.p1.hand) == 0 and len(self.p2.hand) == 0:
                    self.match_round_winner = None  # 平局
                    round_reason = "Both guns empty — DRAW!"
                elif len(self.p1.hand) == 0:
                    self.match_round_winner = self.p2
                    round_reason = "Snake ran out of cards"
                else:
                    self.match_round_winner = self.p1
                    round_reason = "Lizard ran out of cards"
                # 更新胜负计数
                if self.match_round_winner == self.p1:
                    self.p1_match_wins += 1
                elif self.match_round_winner == self.p2:
                    self.p2_match_wins += 1
                # 检查是否最终分出胜负（三局两胜）
                if self.p1_match_wins >= 2 or self.p2_match_wins >= 2:
                    self.match_final_over = True
                    self.match_winner = self.p1 if self.p1_match_wins >= 2 else self.p2
            # 金色粒子雨
            if random.random() < 0.3:
                self.particles.emit_gold(random.randint(100, W-100), -20, 2, random.randint(200, W-200), H+50)
            # 标题
            title_scale = 1.0 + 0.04 * math.sin(pygame.time.get_ticks() * 0.005)
            title_font = pygame.font.SysFont("georgia", int(40 * title_scale), bold=True, italic=True)
            if self.match_final_over:
                draw_text(surf, "MATCH OVER", title_font, C_BLOOD, cx, H//2-130, center=True)
                # 最终胜者
                winner_scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.006 + 1)
                winner_font = pygame.font.SysFont("georgia", int(44 * winner_scale), bold=True, italic=True)
                draw_text(surf, f"{self.match_winner.name} WINS THE MATCH!", winner_font, C_GOLD, cx, H//2-50, center=True)
                draw_text(surf, f"Final Score: {self.p1_match_wins} — {self.p2_match_wins}", FONT_T, C_BONE, cx, H//2+5, center=True)
                draw_text(surf, f"Best of 3 — {self.match_winner.name} takes the saloon.",
                          FONT_B, C_GOLD_L, cx, H//2+40, center=True)
                draw_text(surf, "Press [A] to reveal the mathematical truth...",
                          FONT_S, (180,160,130), cx, H//2+68, center=True)
                self.buttons['restart'] = Button(cx-130, H//2+95, 260, 60, "PLAY AGAIN", font=FONT_T, col=C_RUST, hot=C_BLOOD)
                self.buttons['restart'].draw(surf)
            else:
                # 局间休息：显示本局结果和大比分
                draw_text(surf, f"ROUND {self.match_round} OVER", title_font, C_BLOOD, cx, H//2-130, center=True)
                if self.match_round_winner:
                    rw_scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.006 + 1)
                    rw_font = pygame.font.SysFont("georgia", int(36 * rw_scale), bold=True, italic=True)
                    draw_text(surf, f"{self.match_round_winner.name} wins round {self.match_round}!", rw_font, C_GOLD, cx, H//2-55, center=True)
                else:
                    draw_text(surf, "DRAW! No winner this round.", FONT_T, C_GOLD_L, cx, H//2-55, center=True)
                # 大比分
                score_scale = 1.0 + 0.02 * math.sin(pygame.time.get_ticks() * 0.004)
                score_font = pygame.font.SysFont("georgia", int(48 * score_scale), bold=True, italic=True)
                draw_text(surf, f"{self.p1_match_wins}  —  {self.p2_match_wins}", score_font, C_GOLD_L, cx, H//2+5, center=True)
                draw_text(surf, f"{self.p1.name.split('—')[0].strip()} vs {self.p2.name.split('—')[0].strip()}",
                          FONT_B, C_BONE, cx, H//2+45, center=True)
                draw_text(surf, "Best of 3 — first to 2 wins. Swap sides next round.",
                          FONT_B, (180,160,130), cx, H//2+72, center=True)
                # 换边按钮
                self.buttons['restart'] = Button(cx-160, H//2+105, 320, 56, "NEXT ROUND — SWAP SIDES", font=FONT_B, col=C_RUST, hot=C_BLOOD)
                self.buttons['restart'].draw(surf)
        elif self.phase == 'analysis':
            # ═══ 数学真相揭示界面（56页深度分析） ═══
            overlay = make_alpha_surf(W, H, (8,4,2), 235)
            surf.blit(overlay, (0,0))
            page = getattr(self, 'analysis_page', 0)
            pages_total = 56

            # 顶部标题栏
            title_scale = 1.0 + 0.015 * math.sin(pygame.time.get_ticks() * 0.003)
            title_font = pygame.font.SysFont("georgia", int(26 * title_scale), bold=True, italic=True)
            draw_text(surf, "THE MATHEMATICAL TRUTH", title_font, C_BLOOD, cx, 28, center=True)
            pygame.draw.line(surf, C_GOLD_D, (cx-350, 55), (cx+350, 55), 1)
            draw_text(surf, f"Page {page+1} / {pages_total}", FONT_XS, (150,130,100), cx, 68, center=True)

            # 辅助：绘制纵向柱状图
            def draw_vbars(surf, x, y, w, h, data, colors, labels, max_val=100, unit="%"):
                pygame.draw.rect(surf, (20,12,6), (x, y, w, h), border_radius=6)
                n = len(data)
                bw = w // (n * 2)
                gap = bw // 2
                sx = x + (w - n*bw*2 - (n-1)*gap) // 2
                for i, v in enumerate(data):
                    bh = int(v / max_val * (h - 50))
                    bx = sx + i * (bw*2 + gap)
                    c = colors[i] if i < len(colors) else C_GOLD_D
                    pygame.draw.rect(surf, c, (bx, y+h-35-bh, bw, bh), border_radius=3)
                    draw_text(surf, f"{v}{unit}", FONT_XS, C_BONE, bx+bw//2, y+h-35-bh-14, center=True)
                    if labels and i < len(labels):
                        draw_text(surf, labels[i], FONT_XS, (160,140,110), bx+bw//2, y+h-18, center=True)

            # 辅助：绘制横向柱状图
            def draw_hbars(surf, x, y, w, h, data, colors, labels, max_val=100, unit="%"):
                pygame.draw.rect(surf, (20,12,6), (x, y, w, h), border_radius=6)
                n = len(data)
                bh = (h - 30) // n - 4
                sy = y + 15
                label_w = 180
                bar_max_w = w - label_w - 60
                for i, v in enumerate(data):
                    by = sy + i * (bh + 4)
                    c = colors[i] if i < len(colors) else C_GOLD_D
                    bw = int(v / max_val * bar_max_w)
                    if labels and i < len(labels):
                        draw_text(surf, labels[i], FONT_XS, (180,160,130), x+10, by+bh//2, center=False)
                    pygame.draw.rect(surf, c, (x+label_w, by, bw, bh), border_radius=2)
                    draw_text(surf, f"{v}{unit}", FONT_XS, C_BONE, x+label_w+bw+8, by+bh//2, center=False)

            # ═══════════════════════════════════════════════════════════
            # PAGE 0: 封面
            # ═══════════════════════════════════════════════════════════
            if page == 0:
                big_scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.004)
                big_font = pygame.font.SysFont("georgia", int(52 * big_scale), bold=True, italic=True)
                draw_text(surf, "350,000 GAMES", big_font, C_GOLD, cx, H//2-100, center=True)
                draw_text(surf, "SIMULATED. ANALYZED. SOLVED.",
                          pygame.font.SysFont("georgia", 24, bold=True), C_BLOOD_L, cx, H//2-40, center=True)
                pygame.draw.line(surf, C_GOLD_D, (cx-200, H//2-10), (cx+200, H//2-10), 2)
                draw_text(surf, "This is not a card game. Not a luck game.", FONT_T, C_BONE, cx, H//2+20, center=True)
                draw_text(surf, "It is a math problem about asymmetry,", FONT_T, C_BONE, cx, H//2+50, center=True)
                draw_text(surf, "wrapped in a western saloon.", FONT_T, C_GOLD_L, cx, H//2+80, center=True)
                draw_text(surf, "The real game is the moment you realize:", FONT_B, (200,180,150), cx, H//2+140, center=True)
                draw_text(surf, "nothing you did mattered.", FONT_H, C_BLOOD, cx, H//2+175, center=True)
                draw_text(surf, "Only where you sat mattered.", FONT_T, C_GOLD_L, cx, H//2+210, center=True)
                draw_text(surf, "And the seat was random.", FONT_B, (180,160,130), cx, H//2+240, center=True)
                draw_text(surf, "[A/D or ←/→] Begin the descent into truth", FONT_S, (150,130,100), cx, H-50, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 1: 胜率总览
            # ═══════════════════════════════════════════════════════════
            elif page == 1:
                draw_text(surf, "WIN RATE OVERVIEW — 7 EXPERIMENTS, 350,000 GAMES", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "P1 = Snake (left, commits first) | P2 = Lizard (right, decides final rule)",
                          FONT_XS, (180,160,130), cx, 115, center=True)
                p1_data = [48.8, 64.2, 36.7, 21.5, 19.9, 17.9, 0.0]
                p1_labels = ["No bribe (fair)", "P1 ascending", "P1 descending", "P1 optimal vs P2+intel",
                             "Random vs random", "P2 buys intel", "P1 all-in bribe"]
                p1_colors = [(82,196,26),(100,160,100),(200,160,60),(220,140,60),(200,100,60),(180,60,60),(139,0,0)]
                draw_hbars(surf, 60, 140, 1160, 420, p1_data, p1_colors, p1_labels, 100, "%")
                draw_text(surf, "↑ P1 (Snake) Win Rate by Scenario", FONT_B, C_GOLD, 640, 575, center=True)
                draw_text(surf, "KEY: Without bribes = 48.8% (almost fair). With bribes = P2 wins 80%+.",
                          FONT_B, C_BLOOD_L, cx, 610, center=True)
                draw_text(surf, "P1 all-in bribe = 0.0% — you pay to lose harder.",
                          FONT_B, (240,100,100), cx, 635, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 2: 胜率详情表
            # ═══════════════════════════════════════════════════════════
            elif page == 2:
                draw_text(surf, "DETAILED RESULTS TABLE", FONT_T, C_GOLD_L, cx, 90, center=True)
                tx, ty = 80, 130
                col_w = [340, 120, 120, 120, 120]
                headers = ["Experiment", "P1 Win%", "P2 Win%", "Avg Rounds", "Games"]
                for i, h in enumerate(headers):
                    draw_text(surf, h, FONT_B, C_GOLD, tx + sum(col_w[:i]) + col_w[i]//2, ty, center=True)
                pygame.draw.line(surf, C_GOLD_D, (tx, ty+22), (tx+sum(col_w), ty+22), 1)
                rows = [
                    ["No bribe (pure random)", "48.8%", "51.2%", "2.02", "50,000"],
                    ["P1 ascending vs P2 random", "64.2%", "35.8%", "2.37", "50,000"],
                    ["P1 descending vs P2 random", "36.7%", "63.3%", "1.73", "50,000"],
                    ["P1 optimal vs P2 optimal+1g", "21.5%", "78.5%", "2.03", "50,000"],
                    ["Random vs Random", "19.9%", "80.1%", "2.00", "50,000"],
                    ["P2 buys intel vs P1 no", "17.9%", "82.1%", "2.01", "50,000"],
                    ["P1 all-in vs P2 1 gold", "0.0%", "100.0%", "1.97", "50,000"],
                ]
                for ri, row in enumerate(rows):
                    ry = ty + 40 + ri * 42
                    if ri % 2 == 0:
                        pygame.draw.rect(surf, (25,15,8), (tx, ry-14, sum(col_w), 38), border_radius=4)
                    for ci, val in enumerate(row):
                        col = C_BLOOD_L if ci == 1 and float(val.replace('%','')) < 25 else C_BONE
                        if ci == 2 and float(val.replace('%','')) > 75: col = (240,100,100)
                        if ci == 0: col = (200,180,150)
                        draw_text(surf, val, FONT_S, col, tx + sum(col_w[:ci]) + col_w[ci]//2, ry, center=True)
                draw_text(surf, "FINDING: The asymmetry comes from the BRIBE system, not the cards.",
                          FONT_B, C_GOLD, cx, 500, center=True)
                draw_text(surf, "Remove bribes → 48.8% vs 51.2% (coin flip). Add bribes → P2 dictatorship.",
                          FONT_B, C_BLOOD_L, cx, 530, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 3: 平均轮次对比
            # ═══════════════════════════════════════════════════════════
            elif page == 3:
                draw_text(surf, "AVERAGE GAME LENGTH — THE 2-ROUND EXECUTION", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "The rulebook promises a 6-round epic. The math promises 2 rounds.",
                          FONT_XS, (180,160,130), cx, 115, center=True)
                round_data = [2.37, 2.03, 2.02, 2.01, 2.00, 1.97, 1.73]
                round_labels = ["P1 asc.", "P1 opt.", "No bribe", "P2 intel", "Random", "P1 all-in", "P1 desc."]
                round_colors = [(82,196,26),(100,160,100),(120,140,120),(180,160,60),(200,140,60),(200,100,60),(180,60,60)]
                draw_vbars(surf, 100, 145, 1080, 320, round_data, round_colors, round_labels, 3, "轮")
                line_y = 145 + 320 - 35 - int(6/3 * (320-50))
                pygame.draw.line(surf, C_BLOOD, (100, line_y), (1180, line_y), 2)
                draw_text(surf, "Theoretical max: 6 rounds", FONT_B, C_BLOOD_L, 1180, line_y-12, center=False)
                draw_text(surf, "ALL experiments average 1.7-2.4 rounds. None even close to 6.",
                          FONT_B, C_GOLD, cx, 500, center=True)
                draw_text(surf, "Your 'late-game strategy' never gets used. 97.9% of games end before round 6.",
                          FONT_B, C_BLOOD_L, cx, 530, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 4: 游戏长度分布
            # ═══════════════════════════════════════════════════════════
            elif page == 4:
                draw_text(surf, "GAME LENGTH DISTRIBUTION (Random vs Random, 50k games)", FONT_T, C_GOLD_L, cx, 90, center=True)
                dist_data = [48.4, 25.9, 12.8, 6.2, 3.2, 3.5]
                dist_labels = ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Round 6"]
                dist_colors = [(139,0,0),(180,40,40),(200,100,60),(200,160,60),(100,160,100),(82,196,26)]
                draw_vbars(surf, 100, 130, 1080, 300, dist_data, dist_colors, dist_labels, 50, "%")
                stats = [
                    ("Average rounds", "2.02"),
                    ("Round 1 death", "48.4%"),
                    ("End within 3 rounds", "87.1%"),
                    ("Full 6 rounds", "3.5%"),
                    ("Single-round death rate", "48.6%"),
                ]
                sx = 120
                for i, (k, v) in enumerate(stats):
                    bx = sx + (i % 3) * 360
                    by = 470 + (i // 3) * 50
                    pygame.draw.rect(surf, (25,15,8), (bx, by, 340, 42), border_radius=6)
                    draw_text(surf, k, FONT_XS, (160,140,110), bx+15, by+10, center=False)
                    draw_text(surf, v, FONT_H, C_GOLD_L, bx+325, by+21, center=False)
                draw_text(surf, "The '6-round epic' is a myth. This is an execution, not a war of attrition.",
                          FONT_B, C_BLOOD_L, cx, 590, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 5: 各牌值死亡率
            # ═══════════════════════════════════════════════════════════
            elif page == 5:
                draw_text(surf, "DEATH PROBABILITY BY CARD VALUE", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "The genius design: your attack power = your death sentence.",
                          FONT_XS, (180,160,130), cx, 115, center=True)
                draw_text(surf, "P(death | card = n) = n / 6", FONT_H, C_BLOOD_L, cx, 145, center=True)
                card_data = [16.7, 33.3, 50.0, 66.7, 83.3, 100.0]
                card_labels = ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5", "Card 6"]
                card_colors = [(82,196,26),(120,180,100),(200,180,60),(220,140,60),(200,80,60),(139,0,0)]
                draw_vbars(surf, 100, 180, 1080, 280, card_data, card_colors, card_labels, 100, "%")
                line_y = 180 + 280 - 35 - int(50/100 * (280-50))
                pygame.draw.line(surf, (200,200,200), (100, line_y), (1180, line_y), 1)
                draw_text(surf, "50% coin-flip line", FONT_XS, (200,200,200), 1180, line_y-12, center=False)
                draw_text(surf, "Card 6 wins HIGH mode... but if you lose, 6/6 = 100% GUARANTEED DEATH.",
                          FONT_B, C_BLOOD_L, cx, 500, center=True)
                draw_text(surf, "Card 1 is 'weak'... but if you lose, only 1/6 = 16.7% death.",
                          FONT_B, C_GOLD, cx, 530, center=True)
                draw_text(surf, "The strongest card is also the most dangerous. The weakest is the safest.",
                          FONT_B, (200,180,150), cx, 560, center=True)
                draw_text(surf, "This is the only design element that is genuinely brilliant — and fair.",
                          FONT_B, C_GOLD_L, cx, 590, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 6: 金币无用定理
            # ═══════════════════════════════════════════════════════════
            elif page == 6:
                draw_text(surf, "THEOREM 1: GOLD IS WORTHLESS (Formal Proof)", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "Theorem: For any two states S and S' differing only in gold amounts, U₁(S) = U₁(S').",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                proof = [
                    ("Proof by exhaustive check of all win/loss determinants:", C_GOLD_L, FONT_B),
                    ("", C_BONE, FONT_S),
                    ("1. Game over check: _check_gameover() returns (not alive) OR (hand empty).", C_BONE, FONT_S),
                    ("   Gold is NOT in this expression. □", (120,200,120), FONT_S),
                    ("", C_BONE, FONT_S),
                    ("2. Winner determination: gameover phase compares only 'alive' and 'hand'.", C_BONE, FONT_S),
                    ("   Gold is NEVER compared. □", (120,200,120), FONT_S),
                    ("", C_BONE, FONT_S),
                    ("3. Bet amount: only transfers gold between players. Does NOT affect HIGH/LOW.", C_BONE, FONT_S),
                    ("   Does NOT affect hit chance. □", (120,200,120), FONT_S),
                    ("", C_BONE, FONT_S),
                    ("4. Hit chance: P(death) = card_value / 6. Completely independent of gold. □", C_BONE, FONT_S),
                    ("", C_BONE, FONT_S),
                    ("5. Can't pay? owed = min(owed, gold). No fold, no all-in, no disqualification. □", C_BONE, FONT_S),
                    ("", C_BONE, FONT_S),
                    ("CONCLUSION: All 'bankroll destruction' tactics are mathematically invalid.", C_BLOOD_L, FONT_B),
                    ("Gold's only function: narrative deception. You THINK it matters.", C_GOLD_L, FONT_B),
                ]
                py = 145
                for line, col, f in proof:
                    draw_text(surf, line, f, col, cx, py, center=True)
                    py += 22 if line else 10

            # ═══════════════════════════════════════════════════════════
            # PAGE 7: 金币无用实证
            # ═══════════════════════════════════════════════════════════
            elif page == 7:
                draw_text(surf, "GOLD = 0: EMPIRICAL EVIDENCE", FONT_T, C_GOLD_L, cx, 90, center=True)
                cases = [
                    ("P1 gold = 0, bets 30", "P1 gold becomes 0 (clamped). Still plays. Still can win.", "No penalty"),
                    ("P2 gold = 0, wants to RAISE", "P2 raises with 0 gold. Rule flips anyway.", "Rule still flips"),
                    ("P1 has 40g, P2 has 5g, both out of cards", "Winner = P2 (P1 hand checked first). Gold ignored.", "P2 wins with 5g"),
                    ("P1 bets all 50g every round", "Gold reaches 0 by round 2. Win rate unchanged.", "No effect"),
                    ("P1 never bets (0 gold every round)", "Gold stays 50. Win rate = random level.", "No effect"),
                ]
                cy = 130
                for title, result, verdict in cases:
                    pygame.draw.rect(surf, (25,15,8), (80, cy, 1120, 72), border_radius=6)
                    pygame.draw.rect(surf, (80,55,30), (80, cy, 1120, 72), 1, border_radius=6)
                    draw_text(surf, title, FONT_B, C_GOLD, 100, cy+12, center=False)
                    draw_text(surf, result, FONT_S, C_BONE, 100, cy+36, center=False)
                    draw_text(surf, f"→ {verdict}", FONT_B, C_BLOOD_L, 1000, cy+36, center=False)
                    cy += 84
                draw_text(surf, "The gold system is the game's greatest lie. And its greatest joke.",
                          FONT_B, C_GOLD_L, cx, 580, center=True)
                draw_text(surf, "You were never playing poker. You were playing a shell game with fake money.",
                          FONT_B, (200,180,150), cx, 610, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 8: 贿赂真相（情报价值定理）
            # ═══════════════════════════════════════════════════════════
            elif page == 8:
                draw_text(surf, "THEOREM 2: INTEL ONLY HELPS THE RULE-DECIDER", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "Theorem: The value of opponent's card intel = 0 if you don't hold the final rule-flip.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "P2 (Lizard) — HOLDS final rule-flip", FONT_B, C_GOLD, cx, 155, center=True)
                p2_lines = [
                    "Knows P1's card C₁. Knows own card C₂.",
                    "If C₂ > C₁ → choose HIGH → P2 wins.",
                    "If C₂ < C₁ → choose LOW → P2 wins.",
                    "If C₂ = C₁ → tie, no one dies.",
                    "RESULT: With intel, P2 win rate → 100% (when C₁≠C₂).",
                ]
                ly = 180
                for line in p2_lines:
                    col = C_BLOOD_L if line.startswith("RESULT") else C_BONE
                    draw_text(surf, line, FONT_S, col, cx, ly, center=True)
                    ly += 20
                pygame.draw.line(surf, (80,55,30), (cx-300, 295), (cx+300, 295), 1)
                draw_text(surf, "P1 (Snake) — does NOT hold final rule-flip", FONT_B, C_BLOOD_L, cx, 320, center=True)
                p1_lines = [
                    "Knows P2's card C₂. But P1's card C₁ is ALREADY LOCKED.",
                    "Even if P1 knows C₂, the rule will be decided by P2.",
                    "P2 can always flip to the rule that makes P1 lose.",
                    "P1's intel cannot change C₁ (already played) or the rule (P2's).",
                    "RESULT: P1's intel value = 0. Strictly.",
                ]
                ly = 345
                for line in p1_lines:
                    col = C_BLOOD_L if line.startswith("RESULT") else C_BONE
                    draw_text(surf, line, FONT_S, col, cx, ly, center=True)
                    ly += 20
                draw_text(surf, "P2 pays 1 gold → buys the entire game.", FONT_B, C_GOLD, cx, 480, center=True)
                draw_text(surf, "P1 pays 50 gold → buys 0% win rate improvement.", FONT_B, C_BLOOD_L, cx, 510, center=True)
                draw_text(surf, "The bribe auction is rigged. Only one bidder can use the product.",
                          FONT_B, (200,180,150), cx, 550, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 9: 必输定理
            # ═══════════════════════════════════════════════════════════
            elif page == 9:
                draw_text(surf, "THEOREM 3: THE CERTAIN-LOSS THEOREM", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "Theorem: If C₁ ≠ C₂ AND P2 has true intel, P1 win rate = 0%.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "PROOF:", FONT_B, C_GOLD, cx, 155, center=True)
                proof_lines = [
                    "Given: P2 knows C₁ (P1's card) and C₂ (own card). C₁ ≠ C₂.",
                    "",
                    "Case 1: C₂ > C₁ (P2's card is bigger)",
                    "  P2 chooses (or flips to) HIGH mode.",
                    "  In HIGH mode, bigger card wins. C₂ > C₁ → P2 wins.",
                    "  P1 loses → P1 shoots → P1 may die.",
                    "",
                    "Case 2: C₂ < C₁ (P2's card is smaller)",
                    "  P2 chooses (or flips to) LOW mode.",
                    "  In LOW mode, smaller card wins. C₂ < C₁ → P2 wins.",
                    "  P1 loses → P1 shoots → P1 may die.",
                    "",
                    "In BOTH cases, P2 wins. P1 cannot win regardless of what P1 does.",
                    "Because P1's card is already locked, and P2 decides the rule.",
                    "",
                    "Q.E.D. — P1 win rate = 0% when C₁ ≠ C₂ and P2 has intel.",
                ]
                py = 180
                for line in proof_lines:
                    if line.startswith("Q.E.D."):
                        col, f = C_BLOOD_L, FONT_B
                    elif line.startswith("Case"):
                        col, f = C_GOLD, FONT_B
                    elif line.strip().startswith("In BOTH"):
                        col, f = C_GOLD_L, FONT_B
                    else:
                        col, f = C_BONE, FONT_S
                    draw_text(surf, line, f, col, cx, py, center=True)
                    py += 19 if line else 8

            # ═══════════════════════════════════════════════════════════
            # PAGE 10: 贿赂细节
            # ═══════════════════════════════════════════════════════════
            elif page == 10:
                draw_text(surf, "BRIBE MECHANICS: THE FINE PRINT", FONT_T, C_GOLD_L, cx, 90, center=True)
                sections = [
                    ("TIE-BREAKER: sorted() stability", C_GOLD, [
                        "When both bid the same amount, Python's sorted() is stable.",
                        "P1 is inserted into the dict first → P1 wins ties.",
                        "This is P1's ONLY counter: all-in every round to force ties.",
                        "But it's a war of attrition — P2 waits for P1 to run out, then 1-gold wins.",
                    ]),
                    ("THE DEALER IS A MOUTH (fixed in v5.0)", C_BLOOD_L, [
                        "Original code broadcast: 'sugar daddy' (>80%), 'paid well' (55-80%), 'both paid up'.",
                        "This leaked WHO bribed and HOW MUCH — destroying TRICK deception.",
                        "v5.0 removed all leak lines. The dealer now only speaks in vague atmosphere.",
                    ]),
                    ("THE MEDIUM BUG (fixed in v5.0)", C_BLOOD_L, [
                        "Original _card_hint_false() never produced 'medium' signal.",
                        "P2 hearing 'middling' = 100% certain it was TRUE intel.",
                        "v5.0 fix: false intel can produce all three signals (small/medium/large).",
                        "Now P2 cannot distinguish true from false by signal type alone.",
                    ]),
                ]
                sy = 125
                for title, col, lines in sections:
                    draw_text(surf, title, FONT_B, col, cx, sy, center=True)
                    sy += 22
                    for line in lines:
                        draw_text(surf, line, FONT_S, C_BONE, cx, sy, center=True)
                        sy += 18
                    sy += 12
                draw_text(surf, "Even with all fixes, the core asymmetry remains: P2's intel is worth more than P1's.",
                          FONT_B, C_GOLD_L, cx, 595, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 11: 暗门1（出牌顺序）
            # ═══════════════════════════════════════════════════════════
            elif page == 11:
                draw_text(surf, "HIDDEN DOOR #1: CARD SELECTION ORDER", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "The rulebook says: 'both players secretly select, reveal simultaneously.'",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "The code says:", FONT_B, C_GOLD, cx, 150, center=True)
                flow_y = 185
                boxes = [
                    ("P1 selects card\n(C₁ locked into system)", C_RUST),
                    ("P2 selects card\n(C₂ chosen AFTER C₁ locked)", C_GOLD_D),
                    ("Both revealed\n(simultaneously on screen)", C_BONE),
                ]
                bw, bh = 300, 60
                gap = 60
                total_w = len(boxes) * bw + (len(boxes)-1) * gap
                sx = (W - total_w) // 2
                for i, (text, col) in enumerate(boxes):
                    bx = sx + i * (bw + gap)
                    pygame.draw.rect(surf, (25,15,8), (bx, flow_y, bw, bh), border_radius=8)
                    pygame.draw.rect(surf, col, (bx, flow_y, bw, bh), 2, border_radius=8)
                    for li, line in enumerate(text.split('\n')):
                        draw_text(surf, line, FONT_S, C_BONE, bx+bw//2, flow_y+18+li*18, center=True)
                    if i < len(boxes)-1:
                        ax = bx + bw + 5
                        pygame.draw.polygon(surf, C_GOLD_D, [(ax, flow_y+bh//2-8), (ax+20, flow_y+bh//2), (ax, flow_y+bh//2+8)])
                analysis = [
                    "ON THE SURFACE: simultaneous reveal. Fair.",
                    "UNDER THE HOOD: P1's card is locked first. P2 chooses knowing the system has C₁.",
                    "",
                    "Does P2 actually SEE C₁ at selection time? No — not directly.",
                    "But the temporal ordering creates an information asymmetry in the BRIBE phase:",
                    "P1's card is ALREADY LOCKED when bribe intel arrives. P2's card is FLEXIBLE.",
                    "",
                    "P1 gets intel → can't change card (locked) → intel value = 0.",
                    "P2 gets intel → already chose card, but CAN choose rule → intel value = game-winning.",
                    "",
                    "The selection order doesn't cheat directly. It sets up the board so that P2's intel matters.",
                ]
                ay = 280
                for line in analysis:
                    if line.startswith("ON THE SURFACE"):
                        col, f = C_GOLD, FONT_B
                    elif line.startswith("UNDER THE HOOD"):
                        col, f = C_BLOOD_L, FONT_B
                    elif line.startswith("P1 gets intel") or line.startswith("P2 gets intel"):
                        col, f = C_BONE, FONT_B
                    else:
                        col, f = C_BONE, FONT_S
                    draw_text(surf, line, f, col, cx, ay, center=True)
                    ay += 20 if line else 8

            # ═══════════════════════════════════════════════════════════
            # PAGE 12: 暗门2（加注顺序）
            # ═══════════════════════════════════════════════════════════
            elif page == 12:
                draw_text(surf, "HIDDEN DOOR #2: BETTING ORDER — THE KILLER", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "This is the single most important line of code in the entire game.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                flow = [
                    ("P1 opens\nsets initial HIGH/LOW", "1st rule set"),
                    ("P2: CALL or RAISE\n(RAISE flips rule)", "1st flip — P2"),
                    ("P1: CALL or RAISE\n(RAISE flips rule)", "2nd flip — P1"),
                    ("P2: CALL or RAISE\n(RAISE flips rule)", "3rd flip — P2 (FINAL!)"),
                    ("P1: CALL\n(no more raises)", "LOCKED"),
                ]
                fy = 150
                bw, bh = 200, 55
                gap = 25
                total_w = len(flow) * bw + (len(flow)-1) * gap
                sx = (W - total_w) // 2
                for i, (text, tag) in enumerate(flow):
                    bx = sx + i * (bw + gap)
                    is_final = "FINAL" in tag
                    col = C_BLOOD if is_final else C_GOLD_D
                    pygame.draw.rect(surf, (25,15,8), (bx, fy, bw, bh), border_radius=6)
                    pygame.draw.rect(surf, col, (bx, fy, bw, bh), 2 if is_final else 1, border_radius=6)
                    for li, line in enumerate(text.split('\n')):
                        draw_text(surf, line, FONT_XS, C_BONE, bx+bw//2, fy+12+li*15, center=True)
                    tag_col = C_BLOOD_L if is_final else (160,140,110)
                    draw_text(surf, tag, FONT_XS, tag_col, bx+bw//2, fy+bh+12, center=True)
                draw_text(surf, "FLIP COUNT:", FONT_B, C_GOLD, cx, 250, center=True)
                draw_text(surf, "P1 can set/flip the rule: opening + 2nd raise = MAX 2 times",
                          FONT_S, C_BONE, cx, 275, center=True)
                draw_text(surf, "P2 can flip the rule: 1st raise + 3rd raise = the FINAL flip is ALWAYS P2's",
                          FONT_B, C_BLOOD_L, cx, 300, center=True)
                pygame.draw.line(surf, C_GOLD_D, (cx-300, 330), (cx+300, 330), 1)
                draw_text(surf, "WIN RATE BY WHO HOLDS THE FINAL FLIP:", FONT_B, C_GOLD, cx, 355, center=True)
                matrix = [
                    ("Coin flip (theoretical symmetry)", "44.2%", "55.8%"),
                    ("P2 holds final flip (CURRENT GAME)", "5.3%", "94.7%"),
                    ("P1 holds final flip (for comparison)", "92.1%", "7.9%"),
                    ("P2 also has true intel", "0.0%", "100.0%"),
                ]
                my = 385
                for scenario, p1r, p2r in matrix:
                    is_current = "CURRENT" in scenario
                    col = C_BLOOD_L if is_current else C_BONE
                    f = FONT_B if is_current else FONT_S
                    draw_text(surf, f"{scenario}:  P1={p1r}  P2={p2r}", f, col, cx, my, center=True)
                    my += 24
                draw_text(surf, "Not luck. Not skill. The SEAT decides 90% of the outcome.",
                          FONT_B, C_GOLD_L, cx, 500, center=True)
                draw_text(surf, "The last rule-flip is not a 'mechanic'. It is the entire game.",
                          FONT_B, C_BLOOD_L, cx, 530, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 13: 暗门3（阶段顺序）
            # ═══════════════════════════════════════════════════════════
            elif page == 13:
                draw_text(surf, "HIDDEN DOOR #3: PHASE ORDER — WHY P1'S INTEL IS WORTHLESS", FONT_T, C_BLOOD, cx, 90, center=True)
                phases = [
                    ("SELECT", "Both choose cards\nC₁ locked FIRST, then C₂", C_RUST),
                    ("BRIBE", "Auction for dealer intel\nWinner learns opponent's card", C_GOLD_D),
                    ("BETTING", "P1 opens → P2 raises → ...\nFinal rule-flip = P2", C_BLOOD),
                    ("REVEAL", "Cards shown\nRule applied", C_BONE),
                    ("SHOOT", "Loser points gun at self\nHit chance = card/6", C_BLOOD_L),
                ]
                py = 130
                bw, bh = 200, 65
                gap = 20
                total_w = len(phases) * bw + (len(phases)-1) * gap
                sx = (W - total_w) // 2
                for i, (name, desc, col) in enumerate(phases):
                    bx = sx + i * (bw + gap)
                    pygame.draw.rect(surf, (25,15,8), (bx, py, bw, bh), border_radius=6)
                    pygame.draw.rect(surf, col, (bx, py, bw, bh), 2, border_radius=6)
                    draw_text(surf, name, FONT_B, col, bx+bw//2, py+12, center=True)
                    for li, line in enumerate(desc.split('\n')):
                        draw_text(surf, line, FONT_XS, C_BONE, bx+bw//2, py+32+li*14, center=True)
                draw_text(surf, "THE TRAP:", FONT_B, C_BLOOD, cx, 225, center=True)
                trap = [
                    "Bribe happens AFTER Select. Intel arrives AFTER your card is locked.",
                    "",
                    "P1 receives intel: 'P2 played card 5 (large)'.",
                    "  But P1's card C₁ is ALREADY PLAYED. Can't change it.",
                    "  And the rule HIGH/LOW will be decided by P2 in the next phase.",
                    "  P1 cannot use this intel to change anything.",
                    "  → P1's intel value = 0. Strictly.",
                    "",
                    "P2 receives intel: 'P1 played card 3 (medium)'.",
                    "  P2's card C₂ is already played too — BUT P2 controls the rule.",
                    "  P2 can choose HIGH (if C₂ > 3) or LOW (if C₂ < 3) to win.",
                    "  → P2's intel value = game-winning.",
                    "",
                    "The phase order (Select → Bribe → Betting) is what makes the bribe asymmetric.",
                    "If Bribe happened BEFORE Select, both players could adjust their cards.",
                    "If P1 decided the final rule, P1's intel would matter.",
                    "But the code locks in exactly the order that maximizes P2's advantage.",
                ]
                ty = 255
                for line in trap:
                    if line.startswith("P1 receives") or line.startswith("P2 receives"):
                        col, f = C_GOLD, FONT_B
                    elif line.startswith("  →"):
                        col, f = C_BLOOD_L, FONT_B
                    elif line.startswith("The phase order"):
                        col, f = C_GOLD_L, FONT_B
                    else:
                        col, f = C_BONE, FONT_S
                    draw_text(surf, line, f, col, cx, ty, center=True)
                    ty += 17 if line else 7

            # ═══════════════════════════════════════════════════════════
            # PAGE 14: 博弈论（斯塔克尔伯格）
            # ═══════════════════════════════════════════════════════════
            elif page == 14:
                draw_text(surf, "GAME THEORY: STACKELBERG GAME", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "This is not a simultaneous-move game. It is a leader-follower game.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                pygame.draw.rect(surf, (25,15,8), (80, 145, 540, 200), border_radius=8)
                pygame.draw.rect(surf, C_RUST, (80, 145, 540, 200), 2, border_radius=8)
                draw_text(surf, "P1 (Snake)", FONT_H, C_RUST, 100, 160, center=False)
                draw_text(surf, "COMMITTER (Leader)", FONT_B, C_GOLD_L, 100, 190, center=False)
                p1_traits = ["Moves first in every phase", "Commits to card before intel arrives",
                             "Proposes initial rule", "Cannot make the final decision",
                             "Analogous to: the person who places the bet"]
                for ti, trait in enumerate(p1_traits):
                    draw_text(surf, f"• {trait}", FONT_S, C_BONE, 110, 220+ti*22, center=False)
                pygame.draw.rect(surf, (25,15,8), (660, 145, 540, 200), border_radius=8)
                pygame.draw.rect(surf, C_BLOOD, (660, 145, 540, 200), 2, border_radius=8)
                draw_text(surf, "P2 (Lizard)", FONT_H, C_BLOOD, 680, 160, center=False)
                draw_text(surf, "ADJUDICATOR (Follower)", FONT_B, C_GOLD_L, 680, 190, center=False)
                p2_traits = ["Moves second in every phase", "Chooses card after P1 commits",
                             "Responds to P1's rule proposal", "Holds the FINAL rule-flip",
                             "Analogous to: the person who WRITES the rules"]
                for ti, trait in enumerate(p2_traits):
                    draw_text(surf, f"• {trait}", FONT_S, C_BONE, 690, 220+ti*22, center=False)
                draw_text(surf, "STACKELBERG INSIGHT:", FONT_B, C_GOLD, cx, 370, center=True)
                stack = [
                    "In a standard Stackelberg game, the follower has an information advantage.",
                    "But here, the follower (P2) has BOTH information advantage AND rule-writing power.",
                    "",
                    "The leader (P1) commits first. The follower (P2) observes and responds.",
                    "But P2's response isn't just 'what card to play' — it's 'what RULE to play under'.",
                    "",
                    "This is Stackelberg squared: the follower doesn't just respond to the move.",
                    "The follower gets to REDEFINE THE GAME after seeing the leader's move.",
                    "",
                    "In such a game, the leader's optimal strategy is a mixed strategy (to avoid exploitation).",
                    "The follower's optimal strategy is: always use the final flip to choose the winning rule.",
                ]
                sy = 395
                for line in stack:
                    if line.startswith("In such a game") or line.startswith("The follower's optimal"):
                        col, f = C_GOLD_L, FONT_B
                    else:
                        col, f = C_BONE, FONT_S
                    draw_text(surf, line, f, col, cx, sy, center=True)
                    sy += 18 if line else 8

            # ═══════════════════════════════════════════════════════════
            # PAGE 15: 安全港定理
            # ═══════════════════════════════════════════════════════════
            elif page == 15:
                draw_text(surf, "SAFE HARBOR THEOREM: SAME CARD, OPPOSITE MEANING", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "A card's value is not determined by its number. It is determined by WHO holds it.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                headers = ["Card", "In P2's hand (rule-decider)", "In P1's hand (committer)"]
                tx = 100
                col_w = [120, 500, 500]
                ty = 150
                for i, h in enumerate(headers):
                    draw_text(surf, h, FONT_B, C_GOLD, tx + sum(col_w[:i]) + col_w[i]//2, ty, center=True)
                pygame.draw.line(surf, C_GOLD_D, (tx, ty+22), (tx+sum(col_w), ty+22), 1)
                rows = [
                    ("6", "SAFE HAVEN: Pair with HIGH → win rate → 0. P2 decides HIGH.\nThe 'strongest' card becomes unbeatable.",
                     "DEATH SENTENCE: P2 flips to LOW → 6/6 = 100% death.\nThe 'strongest' card becomes a suicide note."),
                    ("5", "Very strong with HIGH. 83.3% death if P2 somehow loses\n(but P2 controls rule, so P2 rarely loses).",
                     "Dangerous. If P2 flips LOW, 5/6 = 83.3% death.\nHigh attack = high risk when you don't control rules."),
                    ("3", "Balanced. Can win with HIGH or survive loss.\n50% death if loses — a coin flip.",
                     "The optimal mixed-strategy choice (87.5% of the time).\nNot too strong, not too weak — hardest to exploit."),
                    ("1", "SAFE HAVEN: Pair with LOW → win rate → 0.\nThe 'weakest' card becomes unbeatable in LOW mode.",
                     "CHEAP INSURANCE: If loses, only 1/6 = 16.7% death.\nThe 'weakest' card is actually the safest to lose with."),
                ]
                ry = ty + 35
                for card, p2_desc, p1_desc in rows:
                    rh = 80
                    if (ry - ty) // 100 % 2 == 0:
                        pygame.draw.rect(surf, (22,13,7), (tx, ry-10, sum(col_w), rh), border_radius=4)
                    draw_text(surf, card, FONT_H, C_GOLD_L, tx + col_w[0]//2, ry+rh//2-10, center=True)
                    for li, line in enumerate(p2_desc.split('\n')):
                        draw_text(surf, line, FONT_XS, C_BONE, tx + col_w[0] + col_w[1]//2, ry+15+li*16, center=True)
                    for li, line in enumerate(p1_desc.split('\n')):
                        draw_text(surf, line, FONT_XS, C_BLOOD_L if "death" in line.lower() or "DEATH" in line else C_BONE,
                                  tx + col_w[0] + col_w[1] + col_w[2]//2, ry+15+li*16, center=True)
                    ry += rh + 8
                draw_text(surf, "The card doesn't kill you. The seat kills you. The card is just the bullet.",
                          FONT_B, C_GOLD_L, cx, 575, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 16: 最优混合策略
            # ═══════════════════════════════════════════════════════════
            elif page == 16:
                draw_text(surf, "OPTIMAL MIXED STRATEGY (Nash Equilibrium)", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "Any deterministic strategy gets exploited. The only defense is randomness.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "P1 (Snake) Optimal First-Round Strategy:", FONT_B, C_GOLD, cx, 150, center=True)
                p1_strat = [("Play 3", "87.5%", (200,180,60)),
                             ("Play 1", "7.0%", (82,196,26)),
                             ("Play 6", "5.6%", (139,0,0))]
                sx = 250
                for name, pct, col in p1_strat:
                    pygame.draw.rect(surf, (25,15,8), (sx, 175, 240, 70), border_radius=6)
                    pygame.draw.rect(surf, col, (sx, 175, 240, 70), 2, border_radius=6)
                    draw_text(surf, name, FONT_B, C_BONE, sx+120, 195, center=True)
                    draw_text(surf, pct, FONT_H, col, sx+120, 220, center=True)
                    sx += 270
                draw_text(surf, "Why 3? It's the median — not too strong (P2 can't LOW you to death),",
                          FONT_S, C_BONE, cx, 265, center=True)
                draw_text(surf, "not too weak (you can still win in HIGH mode). Hardest for P2 to counter.",
                          FONT_S, C_BONE, cx, 287, center=True)
                draw_text(surf, "P2 (Lizard) Optimal First-Round Strategy:", FONT_B, C_BLOOD_L, cx, 325, center=True)
                p2_strat = [("Play 6 + HIGH", "91.3%", (139,0,0)),
                             ("Play 2 + LOW", "7.5%", (82,196,26)),
                             ("Other", "1.2%", (100,100,100))]
                sx = 250
                for name, pct, col in p2_strat:
                    pygame.draw.rect(surf, (25,15,8), (sx, 350, 240, 70), border_radius=6)
                    pygame.draw.rect(surf, col, (sx, 350, 240, 70), 2, border_radius=6)
                    draw_text(surf, name, FONT_B, C_BONE, sx+120, 370, center=True)
                    draw_text(surf, pct, FONT_H, col, sx+120, 395, center=True)
                    sx += 270
                draw_text(surf, "P2 plays 6+HIGH 91.3% of the time because: if P1 plays <6, P2 wins HIGH;",
                          FONT_S, C_BONE, cx, 440, center=True)
                draw_text(surf, "if P1 plays 6 (tie), no one dies. P2 risks nothing by playing 6.",
                          FONT_S, C_BONE, cx, 462, center=True)
                draw_text(surf, "WHY MIXED? WHY NOT JUST PLAY THE BEST CARD?", FONT_B, C_GOLD, cx, 500, center=True)
                mixed = [
                    "If P1 always plays 3: P2 learns this, always plays 4+HIGH, P1 loses every time.",
                    "If P1 always plays 1: P2 learns this, always plays 2+LOW, P1 loses every time.",
                    "If P2 always plays 6: P1 learns this, always plays 6 (tie), P2 can never win.",
                    "",
                    "The only unexploitable strategy is a MIXED strategy — random by design.",
                    "The probabilities are calculated so that no matter what the opponent does,",
                    "the expected payoff is the same. This is the definition of Nash equilibrium.",
                ]
                my = 525
                for line in mixed:
                    if line.startswith("The only unexploitable"):
                        col, f = C_GOLD_L, FONT_B
                    else:
                        col, f = C_BONE, FONT_S
                    draw_text(surf, line, f, col, cx, my, center=True)
                    my += 18 if line else 8

            # ═══════════════════════════════════════════════════════════
            # PAGE 17: 心理学（认知弧线）
            # ═══════════════════════════════════════════════════════════
            elif page == 17:
                draw_text(surf, "PSYCHOLOGY: THE PLAYER'S COGNITIVE ARC", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "Every player walks the same path from 'I can win this' to 'it was the seat'.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                arc = [
                    ("Game 1", "'Resource management! I need to budget my gold carefully.'", "Gold = 0"),
                    ("Game 2", "'I should bribe more to get intel.'", "Only P2's bribe matters"),
                    ("Game 3", "'Playing 6 is the strongest move!'", "6 in P1's hand = suicide"),
                    ("Game 5", "'If I save my gold, I can make a comeback late game.'", "You die by round 2.02"),
                    ("Game 8", "'Am I just unlucky? My decisions must matter somehow.'", "It's the seat, not luck"),
                    ("Game 10", "'...the outcome doesn't depend on what I do. It depends on where I sit.'", "✓ TRUTH REVEALED"),
                ]
                ay = 150
                for game, belief, truth in arc:
                    rh = 62
                    pygame.draw.rect(surf, (22,13,7), (80, ay, 1120, rh), border_radius=6)
                    is_truth = "TRUTH" in truth
                    col = C_GOLD_L if is_truth else (160,140,110)
                    draw_text(surf, game, FONT_B, C_GOLD, 100, ay+rh//2-8, center=False)
                    draw_text(surf, belief, FONT_S, C_BONE, 200, ay+15, center=False)
                    draw_text(surf, f"→ {truth}", FONT_B, col, 200, ay+38, center=False)
                    ay += rh + 8
                draw_text(surf, "The game's real mechanic is not the cards. It is the slow erosion of your illusions.",
                          FONT_B, C_GOLD_L, cx, 560, center=True)
                draw_text(surf, "You don't win by surviving. You win by understanding.",
                          FONT_B, C_BLOOD_L, cx, 590, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 18: 直觉陷阱
            # ═══════════════════════════════════════════════════════════
            elif page == 18:
                draw_text(surf, "8 INTUITION TRAPS THE GAME SETS FOR YOU", FONT_T, C_BLOOD, cx, 90, center=True)
                traps = [
                    ("'This is a resource management game. Gold matters.'", "Gold never enters any win/loss check. Gold = 0."),
                    ("'Playing 6 is the strongest move.'", "6 in P1's hand: if P2 flips LOW, 6/6 = 100% death."),
                    ("'Going first gives me an advantage.'", "Going first = committing first = being exploited. P1 = 5.3%."),
                    ("'Intel is valuable for both players.'", "P1's intel arrives after card is locked. Value = 0. Only P2's intel matters."),
                    ("'This is a long psychological war of attrition.'", "Average game = 2.02 rounds. 97.9% end before round 6."),
                    ("'The dealer is a neutral NPC.'", "Original code leaked who bribed and how much. (Fixed in v5.0.)"),
                    ("'Deception can be infinitely recursive (I know you know I know...).'", "medium bug + dealer leak collapsed deception to 1 layer. (Fixed in v5.0.)"),
                    ("'If I play optimally, I can win.'", "P1 optimal strategy → 21.5% win rate. Optimal ≠ winning."),
                ]
                ty = 125
                for i, (intuition, truth) in enumerate(traps):
                    rh = 52
                    if i % 2 == 0:
                        pygame.draw.rect(surf, (22,13,7), (80, ty, 1120, rh), border_radius=4)
                    draw_text(surf, f"{i+1}.", FONT_B, C_GOLD_D, 95, ty+rh//2-8, center=False)
                    draw_text(surf, intuition, FONT_XS, (180,160,130), 125, ty+10, center=False)
                    draw_text(surf, f"→ {truth}", FONT_XS, C_BLOOD_L, 125, ty+30, center=False)
                    ty += rh + 4
                draw_text(surf, "Every instinct you bring from other games is wrong here. That is the design.",
                          FONT_B, C_GOLD_L, cx, 575, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 19: 行为经济学
            # ═══════════════════════════════════════════════════════════
            elif page == 19:
                draw_text(surf, "BEHAVIORAL ECONOMICS: WHY YOU PLAY BADLY", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "Even if you understand the math, your brain will sabotage you.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                concepts = [
                    ("LOSS AVERSION", [
                        "Humans feel losses 2.5x more strongly than equivalent gains (Kahneman & Tversky).",
                        "In this game: losing a round feels terrible, so you avoid 'risky' plays.",
                        "You play small cards to 'minimize loss' — but small cards lose more often in HIGH mode.",
                        "Your loss aversion makes you play the exact strategy that loses the most.",
                    ]),
                    ("ENDOWMENT EFFECT", [
                        "You value your 50 gold more than it's worth because it's 'yours'.",
                        "You hesitate to bet/bribe because 'losing gold hurts'.",
                        "But gold = 0. Your attachment to it is purely psychological.",
                        "The game exploits this: you think you're managing resources, you're actually managing anxiety.",
                    ]),
                    ("ILLUSION OF CONTROL", [
                        "You believe your decisions affect the outcome (they do, but only 5-21% for P1).",
                        "You make elaborate plans for 'late game' — but 97.9% of games end by round 3.",
                        "The more you try to control, the more patterns you create, the more P2 exploits you.",
                        "The optimal P1 strategy is essentially: randomize, accept the seat, don't try too hard.",
                    ]),
                    ("GAMBLER'S FALLACY", [
                        "'I lost last round, so I'm due for a win this round.'",
                        "Each round is independent. The gun has no memory. The cards have no memory.",
                        "Your 'due for a win' feeling is statistically invalid — and dangerous when you bet on it.",
                    ]),
                ]
                cy = 145
                for title, lines in concepts:
                    draw_text(surf, title, FONT_B, C_BLOOD_L, cx, cy, center=True)
                    cy += 20
                    for line in lines:
                        draw_text(surf, line, FONT_XS, C_BONE, cx, cy, center=True)
                        cy += 15
                    cy += 8
                draw_text(surf, "The game doesn't just beat your strategy. It beats your brain.",
                          FONT_B, C_GOLD_L, cx, 595, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 20: 信息论
            # ═══════════════════════════════════════════════════════════
            elif page == 20:
                draw_text(surf, "INFORMATION THEORY: WHO KNOWS WHAT", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "Information is power. But only if you can act on it.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "INFORMATION STATE AT EACH PHASE:", FONT_B, C_GOLD, cx, 150, center=True)
                phases_info = [
                    ("After SELECT", "P1 knows: C₁. P2 knows: C₂.", "Neither knows opponent's card. Symmetric."),
                    ("After BRIBE", "Winner knows: opponent's card (small/med/large).", "P1's C₁ is LOCKED. P2 can still choose rule."),
                    ("After P1 opens betting", "P1 knows: C₁, initial rule. P2 knows: C₂, C₁ (if bribed), initial rule.", "P2 has strictly more information AND the next move."),
                    ("After P2's final raise", "P2 knows: everything. P1 knows: C₁, final rule (just learned).", "P2 decided the final rule based on full information."),
                    ("At REVEAL", "Both know: C₁, C₂, final rule.", "Too late to change anything."),
                ]
                py = 180
                for phase, knows, analysis in phases_info:
                    rh = 62
                    pygame.draw.rect(surf, (22,13,7), (80, py, 1120, rh), border_radius=4)
                    draw_text(surf, phase, FONT_B, C_GOLD_D, 100, py+10, center=False)
                    draw_text(surf, knows, FONT_XS, C_BONE, 100, py+30, center=False)
                    draw_text(surf, analysis, FONT_XS, C_BLOOD_L if "P2" in analysis and ("more" in analysis or "decided" in analysis) else (160,140,110),
                              100, py+48, center=False)
                    py += rh + 6
                draw_text(surf, "THE PRICE OF INFORMATION:", FONT_B, C_GOLD, cx, 510, center=True)
                pricing = [
                    "P2 pays 1 gold for opponent's card intel → Value: game-winning (100% win when C₁≠C₂).",
                    "P1 pays 50 gold for opponent's card intel → Value: 0 (card already locked, rule decided by P2).",
                    "",
                    "Information is not inherently valuable. Its value = (what you can DO with it) × (timing).",
                    "P2 can act on intel (choose rule). P1 cannot (card locked). Same information, opposite value.",
                ]
                py = 535
                for line in pricing:
                    if line.startswith("Information is not"):
                        col, f = C_GOLD_L, FONT_B
                    else:
                        col, f = C_BONE, FONT_XS
                    draw_text(surf, line, f, col, cx, py, center=True)
                    py += 16 if line else 8

            # ═══════════════════════════════════════════════════════════
            # PAGE 21: P2最优策略
            # ═══════════════════════════════════════════════════════════
            elif page == 21:
                draw_text(surf, "OPTIMAL STRATEGY: P2 (LIZARD) — 90%+ WIN RATE", FONT_T, C_BLOOD, cx, 90, center=True)
                draw_text(surf, "If you sit right, you are the house. The house always wins.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                steps = [
                    ("STEP 1: BRIBE 1 GOLD EVERY ROUND", [
                        "Spend exactly 1 gold on the bribe. Never more, never less.",
                        "This buys you P1's true card (small/medium/large).",
                        "1 gold is the minimum effective bid — any more is wasted.",
                        "You start with 50 gold. 1 gold/round × 6 rounds = 6 gold total. You'll never run out.",
                    ]),
                    ("STEP 2: CHOOSE YOUR CARD BASED ON INTEL", [
                        "If P1 played small (1-2): play a bigger card (4-6). You'll win in HIGH mode.",
                        "If P1 played large (5-6): play a smaller card (1-3). You'll win in LOW mode.",
                        "If P1 played medium (3-4): play 6. Most likely you'll win HIGH; if tie, no one dies.",
                        "Optimal first round: 91.3% play 6, 7.5% play 2.",
                    ]),
                    ("STEP 3: CONTROL THE RULE WITH YOUR FINAL FLIP", [
                        "P1 opens with some rule (HIGH or LOW).",
                        "If the rule favors you: CALL. Don't waste the flip.",
                        "If the rule favors P1: RAISE and flip it. You have the final say.",
                        "Remember: the 3rd raise (your second raise) is the LAST flip. It always belongs to you.",
                        "Never let P1's rule stand if it makes you lose. You have the power to rewrite it.",
                    ]),
                    ("STEP 4: WHEN IN DOUBT, PLAY 6 + HIGH", [
                        "6+HIGH wins against anything P1 plays except 6 (which is a tie).",
                        "If P1 plays <6, you win. If P1 plays 6, tie (no death). You risk nothing.",
                        "This is why P2's optimal first move is 91.3% 6+HIGH.",
                    ]),
                ]
                sy = 145
                for title, lines in steps:
                    draw_text(surf, title, FONT_B, C_GOLD, cx, sy, center=True)
                    sy += 20
                    for line in lines:
                        draw_text(surf, line, FONT_XS, C_BONE, cx, sy, center=True)
                        sy += 15
                    sy += 6
                draw_text(surf, "EXPECTED WIN RATE: 90%+ against any P1 strategy. 100% when P1 doesn't tie.",
                          FONT_B, C_BLOOD_L, cx, 595, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 22: P1最优策略
            # ═══════════════════════════════════════════════════════════
            elif page == 22:
                draw_text(surf, "OPTIMAL STRATEGY: P1 (SNAKE) — 21.5% MAX WIN RATE", FONT_T, C_RUST, cx, 90, center=True)
                draw_text(surf, "You are at a structural disadvantage. Your goal is not to win — it is to lose slowly.",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                steps = [
                    ("STEP 1: NEVER BRIBE", [
                        "Your intel is worthless. Your card is locked before intel arrives.",
                        "Bribing wastes gold (which is useless anyway) AND reveals your strategy to P2.",
                        "If you all-in bribe: P2 knows you're desperate, reads your bluff, wins 100%.",
                        "Save the gold. It's useless, but spending it actively hurts you.",
                    ]),
                    ("STEP 2: PLAY THE OPTIMAL MIXED STRATEGY", [
                        "First round: 87.5% play 3, 7.0% play 1, 5.6% play 6.",
                        "Why 3? It's the median — P2 can't LOW you to death (3/6=50%), and you can still win HIGH.",
                        "Why mix? Any deterministic pattern gets exploited by P2.",
                        "Use a random number generator. Do NOT try to 'be random' by intuition — humans are bad at it.",
                    ]),
                    ("STEP 3: OPEN THE RULE RANDOMLY", [
                        "Call HIGH 50% of the time, LOW 50% of the time.",
                        "Do NOT base this on your card — P2 will learn the pattern.",
                        "The rule will likely be flipped by P2 anyway, but randomizing prevents P2 from predicting your opening.",
                    ]),
                    ("STEP 4: RAISE OCCASIONALLY (30% OF THE TIME)", [
                        "If P2 raises, occasionally re-raise to flip the rule back.",
                        "This disrupts P2's rhythm and forces them to use their final flip.",
                        "Don't do it every time — P2 will just flip it back and you've wasted a move.",
                        "Remember: P2 has the FINAL flip. You can never win a rule-war against P2.",
                    ]),
                    ("STEP 5: ACCEPT REALITY", [
                        "Your maximum win rate is 21.5%. That's the theoretical ceiling.",
                        "You cannot outplay P2. You cannot outsmart the seat.",
                        "The best you can do is make P2 work for it — and survive long enough to see the truth.",
                        "If you're playing best-of-3: focus on winning the rounds where YOU sit P2.",
                    ]),
                ]
                sy = 145
                for title, lines in steps:
                    draw_text(surf, title, FONT_B, C_GOLD, cx, sy, center=True)
                    sy += 18
                    for line in lines:
                        draw_text(surf, line, FONT_XS, C_BONE, cx, sy, center=True)
                        sy += 14
                    sy += 4
                draw_text(surf, "MAXIMUM ACHIEVABLE WIN RATE: 21.5%. Anything higher means P2 is playing badly.",
                          FONT_B, C_BLOOD_L, cx, 595, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 23: 换边制策略
            # ═══════════════════════════════════════════════════════════
            elif page == 23:
                draw_text(surf, "BEST-OF-3 SWAP: TURNING THE FLAW INTO THE FEATURE", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "The game's biggest flaw (asymmetry) becomes its biggest feature (perspective shift).",
                          FONT_XS, (180,160,130), cx, 118, center=True)
                draw_text(surf, "HOW IT WORKS:", FONT_B, C_GOLD, cx, 150, center=True)
                rules = [
                    "• First to win 2 rounds takes the match (best of 3).",
                    "• After EVERY round, players SWAP SEATS: P1 becomes P2, P2 becomes P1.",
                    "• Each round is independent: gold resets to 50, hand resets to 1-6, death resets.",
                    "• The match score is displayed between rounds.",
                ]
                ry = 175
                for line in rules:
                    draw_text(surf, line, FONT_S, C_BONE, cx, ry, center=True)
                    ry += 20
                draw_text(surf, "WHY THIS IS GENIUS:", FONT_B, C_BLOOD_L, cx, 270, center=True)
                genius = [
                    "1. FAIRNESS: Each player experiences both the advantaged and disadvantaged seat.",
                    "   Overall match win rate approaches 50/50 — the asymmetry cancels out over 3 rounds.",
                    "",
                    "2. PERSPECTIVE SHIFT: In round 1, you sit P1 and feel powerless.",
                    "   In round 2, you sit P2 and suddenly understand WHY you felt powerless.",
                    "   The swap is not just a mechanic — it is the game's thesis statement.",
                    "",
                    "3. STRATEGIC DEPTH: Now you must master BOTH seats.",
                    "   As P1: survive with 21.5% win rate. As P2: dominate with 90%+ win rate.",
                    "   The player who better understands BOTH perspectives wins the match.",
                    "",
                    "4. THE REVEAL: After round 1 (as P1), you might think 'I just played badly'.",
                    "   After round 2 (as P2), you realize: 'No. The seat was doing all the work.'",
                    "   That moment of realization IS the game. The swap makes it inevitable.",
                ]
                gy = 295
                for line in genius:
                    if line.startswith("That moment"):
                        col, f = C_GOLD_L, FONT_B
                    elif line.startswith(("1.", "2.", "3.", "4.")):
                        col, f = C_GOLD, FONT_B
                    else:
                        col, f = C_BONE, FONT_XS
                    draw_text(surf, line, f, col, cx, gy, center=True)
                    gy += 16 if line else 7
                draw_text(surf, "Do NOT play single-round. Play best-of-3. The swap is where the game lives.",
                          FONT_B, C_BLOOD_L, cx, 595, center=True)
# ═══════════════════════════════════════════════════════════
            # PAGE 24-53: 30 CASE STUDIES (像围棋棋谱一样)
            # ═══════════════════════════════════════════════════════════
            elif 24 <= page <= 53:
                case_num = page - 23  # 1-30
                cases = [
                    # Case 1
                    {"title": "CASE 1: THE NEWBIE'S CONFUSION", "persona": "Random Player",
                     "scene": "First game. Both players are new. Random cards, random bribes.",
                     "decision": "P1 randomly plays 3, bribes 5g. P2 randomly plays 5, bribes 3g.",
                     "result": "P1 wins bribe auction, gets true intel (P2=5=large). But P1's card 3 is already locked. P2 opens HIGH, P1 calls. 5>3, P1 loses, shoots at 3/6=50%, survives.",
                     "analysis": "P1 'won' the bribe but got worthless intel. The card was already played. P2 didn't even need intel — random play still won 80.1% of games.",
                     "lesson": "Winning the bribe auction ≠ winning the game. For P1, intel is worthless."},
                    # Case 2
                    {"title": "CASE 2: THE CAUTIOUS TURTLE", "persona": "Conservative Player",
                     "scene": "P1 always plays the smallest available card, believing lower death rate = safer.",
                     "decision": "Round 1: P1 plays 1. Round 2: P1 plays 2. Round 3: P1 plays 3...",
                     "result": "P1's death rate per loss is lowest (1/6=16.7% first round). But small cards lose more often in HIGH mode. P1 keeps losing, keeps shooting. Cumulative death rate climbs.",
                     "analysis": "Conservative ≠ safe. Playing small means you lose more often. Each loss is a coin flip at low odds, but you flip many more coins. The expected number of shots is higher.",
                     "lesson": "Low death rate per shot doesn't mean high survival rate if you get shot more often."},
                    # Case 3
                    {"title": "CASE 3: THE EXTREME GAMBLER", "persona": "Aggressive Player",
                     "scene": "P1 always plays 6, believing the biggest card always wins.",
                     "decision": "Round 1: P1 plays 6, opens HIGH.",
                     "result": "If P2 plays <6 and P1 keeps HIGH: P1 wins, no death. But P2 can RAISE and flip to LOW. 6 is the WORST card in LOW mode. P1 loses, shoots at 6/6=100% — instant death.",
                     "analysis": "6 is a double-edged sword. Win = no death. Lose = guaranteed death. Against P2's rule-flip power, P1's 6 becomes a suicide note. P2 can ALWAYS flip to make 6 lose.",
                     "lesson": "Your strongest card is also your death sentence — when you don't control the rules."},
                    # Case 4
                    {"title": "CASE 4: THE ALL-IN MADMAN", "persona": "Desperate Player",
                     "scene": "P1 bribes ALL remaining gold every round, believing being the 'sugar daddy' guarantees advantage.",
                     "decision": "Round 1: P1 bribes 50g. P2 bribes 1g.",
                     "result": "P1 wins auction (50>1), gets true intel. But P1's intel value = 0. P2 knows P1 went all-in (dealer used to broadcast this), so P2 knows P1 is desperate. P2 plays optimally, wins. P1 has 0 gold left, can't do anything. P1 win rate: 0.0%.",
                     "analysis": "All-in bribe is the WORST possible P1 strategy. You waste all your gold on worthless intel, AND you signal your desperation to P2. The old dealer's 'sugar daddy' line made this even worse — P2 could literally hear you panicking.",
                     "lesson": "For P1, bribing is not just worthless — it's actively harmful. The more you spend, the more you lose."},
                    # Case 5
                    {"title": "CASE 5: THE SHREWED LIZARD", "persona": "Calculating Player (P2)",
                     "scene": "P2 spends exactly 1 gold on bribe every round.",
                     "decision": "P2 bribes 1g, learns P1 played 3 (medium). P2 plays 6, opens HIGH.",
                     "result": "6>3 in HIGH, P1 loses, shoots at 3/6=50%. P2 wins round. P2 spent 1 gold out of 50. Repeat every round.",
                     "analysis": "1 gold buys the entire game. With intel + rule-flip power, P2 wins whenever C₁≠C₂. The only way P1 survives is to tie (play the same card), which P2 can also avoid by choosing a different card.",
                     "lesson": "For P2, 1 gold bribe is the highest-ROI action in the entire game. Never spend more."},
                    # Case 6
                    {"title": "CASE 6: THE MATHEMATICIAN SNAKE", "persona": "Optimal Player (P1)",
                     "scene": "P1 uses linear programming to derive the optimal mixed strategy.",
                     "decision": "Round 1: 87.5% chance play 3, 7% play 1, 5.6% play 6. Never bribe. Open rule randomly.",
                     "result": "P1 win rate: 21.5% (against P2 optimal + 1g intel). This is the theoretical maximum for P1.",
                     "analysis": "The mathematician's solution is correct — but it only yields 21.5%. The game is structurally unfair. No amount of math can overcome the seat disadvantage. The mixed strategy prevents P2 from exploiting deterministic patterns, but can't overcome the rule-flip asymmetry.",
                     "lesson": "Math can find the optimal strategy. But optimal ≠ winning. In an unfair game, optimal just means 'losing less badly'."},
                    # Case 7
                    {"title": "CASE 7: THE ASCENDING DELAYER", "persona": "Patient Player (no bribes)",
                     "scene": "P1 plays cards in ascending order: 1, 2, 3, 4, 5, 6. No bribes (P2 also random, no bribes).",
                     "decision": "Round 1: P1 plays 1. Round 2: P1 plays 2...",
                     "result": "P1 win rate: 64.2% (against random P2, no bribes). Average 2.37 rounds.",
                     "analysis": "Counter-intuitive! Ascending play gives P1 the HIGHEST win rate (when P2 is random and no bribes). Why? Playing small first means if you lose, death rate is low (1/6=16.7%). You survive to later rounds where your bigger cards can win. P2's random play doesn't exploit the predictable pattern.",
                     "lesson": "Against a non-optimal opponent, 'boring' survival strategies can be surprisingly effective. But this only works without bribes — P2's intel destroys any predictable pattern."},
                    # Case 8
                    {"title": "CASE 8: THE DESCENDING DAREDEVIL", "persona": "Aggressive Player (no bribes)",
                     "scene": "P1 plays cards in descending order: 6, 5, 4, 3, 2, 1. No bribes.",
                     "decision": "Round 1: P1 plays 6.",
                     "result": "P1 win rate: 36.7%. Average 1.73 rounds (fastest death).",
                     "analysis": "Descending play is the fastest way to die. Playing 6 first: if P2 flips to LOW, 6/6=100% death. Even if P1 wins, P2's small card has low death rate. The big-card-first strategy risks everything on round 1, when you have the least information.",
                     "lesson": "Playing your strongest card first is a gamble — and the house (P2) holds the dice."},
                    # Case 9
                    {"title": "CASE 9: THE RULE-FLIP MASTER", "persona": "Control Player (P2)",
                     "scene": "P2 RAISEs every single time, flipping the rule back and forth.",
                     "decision": "P1 opens HIGH. P2 RAISE → LOW. P1 RAISE → HIGH. P2 RAISE (3rd, final) → LOW.",
                     "result": "Final rule is LOW, decided by P2. P2 chooses based on own card vs P1's card. P2 wins.",
                     "analysis": "P2 doesn't even need to think about what rule to choose — just flip to whatever makes P2 win. The 3rd raise is always P2's, so P2 always gets the final say. P1 can flip twice, but P2's final flip overrides everything.",
                     "lesson": "The last rule-flip is the only one that matters. And it always belongs to P2."},
                    # Case 10
                    {"title": "CASE 10: THE GOLD HOARDER", "persona": "Frugal Player",
                     "scene": "Player never bets, never bribes. Keeps all 50 gold.",
                     "decision": "Every round: bet 0, bribe 0.",
                     "result": "Gold stays at 50 the entire game. But win rate = random level. Gold has zero effect.",
                     "analysis": "The gold hoarder plays 'rationally' (if gold had value) — saving resources for later. But gold = 0. The hoarded gold is meaningless. The player might as well have spent it all on nothing. This is the game's most bitter joke: the most 'responsible' player is playing a game that doesn't exist.",
                     "lesson": "You're not hoarding gold. You're hoarding nothing. The vault is empty."},
                    # Case 11
                    {"title": "CASE 11: THE MONEY BURNER", "persona": "Reckless Player",
                     "scene": "Player bets maximum gold every round, trying to 'pressure' the opponent.",
                     "decision": "Round 1: bet 30g. Round 2: bet remaining 20g.",
                     "result": "Gold reaches 0 by round 2. But betting doesn't affect rules or hit chance. Opponent wins regardless.",
                     "analysis": "The money burner thinks big bets = psychological pressure. But there's no fold mechanic, no all-in, no penalty for calling with insufficient gold. The bets are just gold destruction. The burner might as well be throwing money into a fire while the opponent ignores them.",
                     "lesson": "Betting big doesn't pressure anyone. It just destroys your (worthless) gold faster."},
                    # Case 12
                    {"title": "CASE 12: THE DEALER'S DISCIPLE", "persona": "Trusting Player",
                     "scene": "Player believes every word the dealer says about opponent's card.",
                     "decision": "Dealer says 'opponent played large' → player plays small, opens LOW.",
                     "result": "If dealer told truth (winner's honest intel): player might win. If dealer lied (TRICK): player loses badly. Overall = random level (old code).",
                     "analysis": "The dealer is not your friend. In the old code, the dealer broadcast who bribed and how much — so the opponent could tell if you were being lied to. Even with fixes, the dealer's intel is only useful if you can act on it (P2) — for P1, it's just noise.",
                     "lesson": "Never trust a dealer who takes money from both sides."},
                    # Case 13
                    {"title": "CASE 13: THE ANTI-DEALER SKEPTIC", "persona": "Paranoid Player",
                     "scene": "Player always assumes the dealer is lying, and does the opposite of what intel suggests.",
                     "decision": "Dealer says 'large' → player assumes small → plays big, opens HIGH.",
                     "result": "Sometimes right (when TRICK), sometimes wrong (when HONEST). Overall win rate ≈ random. No statistical advantage.",
                     "analysis": "After the medium bug fix, false intel can produce all three signal types. This means there's no statistical way to distinguish true from false intel by signal alone. Always reversing = same as always believing = random. The only way to gain advantage is to know WHO bribed (which the old dealer leaked, but v5.0 fixed).",
                     "lesson": "Paranoia doesn't give you an edge. In a fair deception game, truth and lies are statistically indistinguishable."},
                    # Case 14
                    {"title": "CASE 14: THE TIE MASTER", "persona": "Cunning Player (P2)",
                     "scene": "P2 uses intel to deliberately play the SAME card as P1, forcing a tie.",
                     "decision": "P2 bribes 1g, learns P1 played 4. P2 also plays 4.",
                     "result": "Tie! No one shoots. Both survive, both lose card 4. Next round.",
                     "analysis": "Tie is the only 'safe' outcome — no one dies. P2 can force ties whenever P1's card is available in P2's hand. This is P2's 'stalling' tactic: burn through P1's best cards without risk. But ties also burn P2's cards, so it's a trade-off. Best used when P1 plays a high-value card that P2 can match.",
                     "lesson": "For P2, a tie is not a failure — it's a risk-free way to neutralize P1's best cards."},
                    # Case 15
                    {"title": "CASE 15: THE WISE FIRST-MOVE (Play 1)", "persona": "Cautious Player (P1)",
                     "scene": "P1 plays 1 on round 1, the lowest-risk opening.",
                     "decision": "P1 plays 1, bets 1g, no bribe. Opens HIGH randomly.",
                     "result": "If P2 plays >1 and HIGH: P1 loses, shoots at 1/6=16.7% — 83.3% chance to survive. If P2 plays 1: tie. If LOW and P2 plays >1: P1 wins! Overall low-risk opening.",
                     "analysis": "Playing 1 first is the safest possible opening for P1. Even if you lose, you have an 83.3% chance to survive. This lets you see P2's play style and adjust. But playing 1 means you probably lose the round (if HIGH), and you're burning your safest card early. Best used when you want to survive and gather information.",
                     "lesson": "Sometimes the best first move is the one that lets you live to see round 2."},
                    # Case 16
                    {"title": "CASE 16: THE RECKLESS FIRST-MOVE (Play 6)", "persona": "Aggressive Player (P1)",
                     "scene": "P1 plays 6 on round 1, trying to intimidate.",
                     "decision": "P1 plays 6, opens HIGH.",
                     "result": "If P2 plays <6 and P1 keeps HIGH: P1 wins! But P2 can RAISE flip to LOW. 6 loses to everything in LOW. P1 shoots at 6/6=100% — dead. Round 1 death.",
                     "analysis": "Playing 6 first is the ultimate gamble. You either win cleanly or die instantly. Against P2's rule-flip power, the odds are terrible — P2 can ALWAYS flip to LOW and kill you. The only way 6 works is if P2 doesn't have enough gold to raise (unlikely round 1) or if P2 plays 6 (tie).",
                     "lesson": "Don't put your entire life on round 1. The house always gets to flip the table."},
                    # Case 17
                    {"title": "CASE 17: THE PREDICTOR", "persona": "Psychological Player",
                     "scene": "P1 tries to predict P2's card and play accordingly.",
                     "decision": "P1 thinks: 'P2 always plays big early. So I'll play small and open LOW.'",
                     "result": "If prediction correct: P1 wins. If wrong: P1 loses badly. Against optimal P2 (mixed strategy), prediction success rate ≈ random.",
                     "analysis": "Prediction works against predictable opponents. But P2's optimal strategy is mixed (91.3% play 6, 7.5% play 2) — there's no reliable pattern to predict. And even if P1 correctly predicts P2's card, P2 can still flip the rule to win. Prediction is only useful if you also control the rule — which P1 doesn't.",
                     "lesson": "You can't predict your way out of a structural disadvantage. The house doesn't need to bluff."},
                    # Case 18
                    {"title": "CASE 18: THE PRE-PREDICTOR (I know you know I know)", "persona": "Mastermind Player",
                     "scene": "P1 tries infinite recursion: 'P2 thinks I'll play small, so P2 will play medium, so I'll play big...'",
                     "decision": "P1 goes through 5 levels of recursion before playing.",
                     "result": "In zero-sum games with mixed strategy equilibria, all levels of recursion converge to the same Nash equilibrium. P1's 'higher-level thinking' yields the same result as random play against optimal P2.",
                     "analysis": "This is the classic 'guess 2/3 of the average' problem. In games with a mixed strategy equilibrium, there is no 'highest level' of thinking — all levels converge. P1's elaborate recursion is wasted cognitive effort. The only thing that matters is the seat. P2 doesn't need to think at all — just flip the rule to win.",
                     "lesson": "In a structurally unfair game, infinite recursion converges to the same loss. Thinking harder doesn't help when the rules are rigged."},
                    # Case 19
                    {"title": "CASE 19: THE TILTED LOSER", "persona": "Emotional Player",
                     "scene": "P1 loses round 1 (survives), gets angry, goes all-in on round 2.",
                     "decision": "Round 2: P1 bribes all remaining gold, plays 6, opens HIGH.",
                     "result": "P2 sees P1 tilt (old dealer leaked all-in), plays optimally. P1 loses, shoots at 6/6=100% — dead. Game over in 2 rounds.",
                     "analysis": "Tilt is the worst possible strategy. Emotional decisions are almost always suboptimal. In this game, tilt means: spending gold on worthless intel, playing high-risk cards, making predictable moves. P2 loves a tilted opponent — they're easy to read and easy to kill. The game's fast pace (average 2 rounds) means tilt kills you before you can recover.",
                     "lesson": "In a game where you're already disadvantaged, emotion is the final nail in the coffin. Stay calm or stay dead."},
                    # Case 20
                    {"title": "CASE 20: THE EMOTIONLESS MACHINE", "persona": "Rational Player",
                     "scene": "Player always plays the mathematically optimal move, no emotion.",
                     "decision": "P1: mixed strategy (87.5% play 3, etc.), no bribe, random rule open. P2: 1g bribe, play based on intel, flip rule to win.",
                     "result": "P1 achieves theoretical max 21.5%. P2 achieves 90%+. Both play 'perfectly' — but P2 still wins overwhelmingly.",
                     "analysis": "The emotionless machine plays perfectly but still loses. This is the game's most profound statement: perfection is not enough when the rules are unfair. The machine understands this intellectually but cannot change it. The only 'winning' move for P1 is to recognize the asymmetry and play best-of-3 with side swaps.",
                     "lesson": "You can play perfectly and still lose. The game isn't testing your skill — it's testing whether you notice the seat."},
                    # Case 21
                    {"title": "CASE 21: THE MIMIC", "persona": "Copycat Player",
                     "scene": "P1 copies P2's previous round's card.",
                     "decision": "P2 played 5 last round → P1 plays 5 this round.",
                     "result": "P2 quickly learns the pattern. P2 plays a card that beats 5 in whatever rule P2 chooses. P1 loses every time.",
                     "analysis": "Mimicry is a deterministic strategy, and all deterministic strategies get exploited by P2. P2 only needs to observe one round to learn the pattern, then counter it perfectly. The mimic's 'strategy' is actually a gift to P2 — free information about P1's next move.",
                     "lesson": "Any pattern you create becomes a weapon for your opponent. Especially when your opponent writes the rules."},
                    # Case 22
                    {"title": "CASE 22: THE ANTI-MIMIC", "persona": "Contrarian Player",
                     "scene": "P1 always plays the OPPOSITE of P2's previous round card.",
                     "decision": "P2 played 5 last round → P1 plays 2 (small opposite).",
                     "result": "Still deterministic. P2 learns the anti-pattern and counters it. P1 loses.",
                     "analysis": "Being contrarian is just another deterministic pattern. P2 can exploit 'always opposite' just as easily as 'always same'. The only defense against exploitation is genuine randomness (mixed strategy). Human 'contrarian' behavior is still predictable — it's just a different fixed function.",
                     "lesson": 'Being "unpredictable" on purpose is still predictable. Only mathematical randomness works.'},
                    # Case 23
                    {"title": "CASE 23: THE LINEAR PROGRAMMER", "persona": "Academic Player",
                     "scene": "P1 writes a Python script to solve the game with linear programming before playing.",
                     "decision": "Script outputs: 87.5% play 3, 7% play 1, 5.6% play 6. P1 follows exactly.",
                     "result": "P1 achieves 21.5% win rate. The script was correct — but the answer is 'you lose most of the time.'",
                     "analysis": "The linear programmer does everything right. They model the game correctly, solve it correctly, execute the solution correctly. And they still lose 78.5% of the time. This is the game's most academic joke: the correct answer to 'how do I win?' is 'you don't, not from this seat.' The programmer's skill is real — but the seat is stronger.",
                     "lesson": "The correct solution to an unfair game is 'you lose.' The question isn't 'how do I win?' — it's 'why am I sitting here?'"},
                    # Case 24
                    {"title": "CASE 24: THE INTUITIONIST", "persona": "Gut-Feeling Player",
                     "scene": "P1 plays by 'vibes' — 'I feel like playing 4 this round.'",
                     "decision": "Random-ish card selection based on mood. Random bribes.",
                     "result": "Win rate ≈ 19.9% (random level). Intuition provides no edge.",
                     "analysis": "In games with no hidden information asymmetry that you can exploit, intuition = randomness. P1 has no information advantage (P2 has more), so 'gut feeling' is just a fancy word for 'random choice.' The intuitionist might feel clever, but their results are indistinguishable from a coin flip.",
                     "lesson": "Intuition only works when you have information to intuit from. When you're information-disadvantaged, your gut is just guessing."},
                    # Case 25
                    {"title": "CASE 25: THE STATISTICIAN", "persona": "Data-Driven Player",
                     "scene": "P1 records P2's every move across 10 games, then plays based on frequency analysis.",
                     "decision": "Data shows P2 plays 6 60% of the time → P1 plays 6 to tie, or plays 1 to survive LOW.",
                     "result": "Against non-optimal P2: slight edge. Against optimal P2 (mixed strategy): no edge. Historical data doesn't predict mixed strategy moves.",
                     "analysis": "Statistics work against predictable opponents. But P2's optimal strategy is a fixed probability distribution — each move is independent, past performance doesn't predict future moves. The statistician's 10-game sample is noise. This is the gambler's fallacy in academic clothing: 'P2 played 6 a lot, so they're due for a small card.' No — each round is independent.",
                     "lesson": "Past performance doesn't predict future moves when the opponent plays a true mixed strategy. The dice have no memory."},
                    # Case 26
                    {"title": "CASE 26: THE GAME THEORIST", "persona": "Nash Equilibrium Player",
                     "scene": "Both players play their Nash equilibrium strategies.",
                     "decision": "P1: mixed strategy (87.5%/7%/5.6%). P2: 1g bribe + optimal response.",
                     "result": "P1: 21.5%. P2: 78.5%. This is the stable equilibrium — neither can improve by changing strategy unilaterally.",
                     "analysis": "Nash equilibrium means neither player can improve by changing their strategy alone. But it does NOT mean fair. In this game, the Nash equilibrium heavily favors P2. The game theorist understands this — they know they're at a stable but unfair equilibrium. The only way to 'win' is to change the game itself (play best-of-3 with swaps).",
                     "lesson": "Nash equilibrium ≠ fair. It just means stable. You can be in a perfectly stable equilibrium and still be getting crushed."},
                    # Case 27
                    {"title": "CASE 27: THE PHILOSOPHER", "persona": "Enlightened Player",
                     "scene": "P1 has played 20 games and finally understands: gold=0, seat=everything, intel=worthless for P1.",
                     "decision": "P1 plays randomly, no emotion, no expectation. Just enjoys the process.",
                     "result": "Win rate ≈ random (19.9%). But player satisfaction = maximum. The philosopher has 'won' by understanding the game's true nature.",
                     "analysis": "The philosopher is the only player who truly 'gets' the game. They don't try to win — they try to understand. And in understanding, they achieve something the hyper-competitive players never will: peace. The game's real victory condition isn't 'survive' — it's 'understand.' The philosopher is the only one who reads the rulebook and says 'ah, I see what you did there.'",
                     "lesson": "The only way to win is to stop trying to win by the game's rules, and instead understand the game itself."},
                    # Case 28
                    {"title": "CASE 28: THE SWAP BENEFICIARY", "persona": "Strategic Player (Best-of-3)",
                     "scene": "Player understands the asymmetry and focuses on winning the rounds where they sit P2.",
                     "decision": "Round 1 (P1): play mixed strategy, try to survive. Round 2 (P2): 1g bribe + optimal play, dominate. Round 3 (P1, if needed): mixed strategy.",
                     "result": "Match win rate approaches 50%. The player wins their P2 rounds ~90% of the time, and wins P1 rounds ~21.5% of the time. Overall fair match.",
                     "analysis": "The swap beneficiary doesn't fight the asymmetry — they exploit it from both sides. They know they'll probably lose as P1, so they just try to survive. They know they'll probably win as P2, so they dominate. The match becomes a test of: can you survive your P1 rounds long enough to win your P2 rounds? This turns the game's biggest flaw into its deepest strategy.",
                     "lesson": "Don't fight the asymmetry — use it. Win your advantage rounds, survive your disadvantage rounds."},
                    # Case 29
                    {"title": "CASE 29: THE FINAL WINNER", "persona": "Awakened Player",
                     "scene": "After 10 games, the player fully understands: the seat decides 90% of the outcome.",
                     "decision": "Chooses to play best-of-3. When P2: dominates with 1g bribe + rule flip. When P1: mixed strategy + acceptance.",
                     "result": "Wins more matches than any other player. Not because they're more skilled — because they understand the game's true structure.",
                     "analysis": "The final winner isn't the best card-player or the best psychologist. They're the one who first realized 'the seat decides everything.' Once you understand that, every other decision becomes simple: when you have the advantage, press it; when you don't, survive. The game's real skill ceiling isn't in the cards — it's in recognizing the asymmetry and adapting to it.",
                     "lesson": "The greatest skill in an unfair game is recognizing the unfairness. Once you see it, the game becomes simple."},
                    # Case 30
                    {"title": "CASE 30: YOUR STORY", "persona": "You",
                     "scene": "The game you just played. The choices you made. The wins and losses.",
                     "decision": "Every card you played. Every bribe you made. Every rule you called. Every time you pulled the trigger.",
                     "result": "You just experienced it. You know the result.",
                     "analysis": "Think back: when did you feel confident? When did you feel helpless? When did you first suspect 'something isn't right here'? When did you realize gold doesn't matter? When did you notice the seat? Your story is unique, but the structure is the same for everyone: confusion → suspicion → realization → understanding. That arc IS the game. The cards are just the delivery mechanism.",
                     "lesson": "You didn't just play a game. You walked through a proof. The question is: did you reach the conclusion?"},
                ]
                case = cases[case_num - 1]
                # 标题
                draw_text(surf, case["title"], FONT_T, C_GOLD_L, cx, 90, center=True)
                pygame.draw.line(surf, C_GOLD_D, (cx-300, 115), (cx+300, 115), 1)
                # 人格标签
                pygame.draw.rect(surf, (40,25,10), (cx-150, 125, 300, 28), border_radius=4)
                pygame.draw.rect(surf, C_GOLD_D, (cx-150, 125, 300, 28), 1, border_radius=4)
                draw_text(surf, f"Persona: {case['persona']}", FONT_B, C_GOLD, cx, 139, center=True)
                # 场景
                draw_text(surf, "SCENE:", FONT_B, C_GOLD, 100, 175, center=False)
                draw_text(surf, case["scene"], FONT_S, C_BONE, 100, 198, center=False)
                # 决策
                draw_text(surf, "DECISION:", FONT_B, C_GOLD, 100, 235, center=False)
                draw_text(surf, case["decision"], FONT_S, C_BONE, 100, 258, center=False)
                # 结果
                draw_text(surf, "RESULT:", FONT_B, C_BLOOD_L, 100, 295, center=False)
                draw_text(surf, case["result"], FONT_S, (220,200,170), 100, 318, center=False)
                # 分析
                draw_text(surf, "ANALYSIS:", FONT_B, C_GOLD, 100, 395, center=False)
                draw_text(surf, case["analysis"], FONT_S, C_BONE, 100, 418, center=False)
                # 教训
                pygame.draw.rect(surf, (35,20,8), (80, 510, 1120, 70), border_radius=8)
                pygame.draw.rect(surf, C_BLOOD, (80, 510, 1120, 70), 2, border_radius=8)
                draw_text(surf, "LESSON:", FONT_B, C_BLOOD_L, 100, 528, center=False)
                draw_text(surf, case["lesson"], FONT_B, C_GOLD_L, 100, 552, center=False)

            # ═══════════════════════════════════════════════════════════
            # PAGE 54: 最终结论
            # ═══════════════════════════════════════════════════════════
            elif page == 54:
                draw_text(surf, "THE FINAL VERDICT", FONT_H, C_BLOOD, cx, 100, center=True)
                pygame.draw.line(surf, C_GOLD_D, (cx-250, 135), (cx+250, 135), 2)
                verdict = [
                    ("This is not a card game.", C_BONE, FONT_T),
                    ("Not a luck game.", C_BONE, FONT_T),
                    ("Not a psychology game.", C_BONE, FONT_T),
                    ("", C_BONE, FONT_S),
                    ("It is a math problem about asymmetry,", C_GOLD_L, FONT_T),
                    ("wrapped in a western saloon.", C_GOLD_L, FONT_T),
                    ("", C_BONE, FONT_S),
                    ("The real game is the moment you realize:", (200,180,150), FONT_B),
                    ("nothing you did mattered.", C_BLOOD, FONT_H),
                    ("Only where you sat mattered.", C_GOLD_L, FONT_T),
                    ("And the seat was random.", (180,160,130), FONT_B),
                    ("", C_BONE, FONT_S),
                    ("That's the most western thing of all.", C_GOLD_L, FONT_B),
                ]
                vy = 165
                for line, col, f in verdict:
                    draw_text(surf, line, f, col, cx, vy, center=True)
                    vy += 28 if line else 12
                draw_text(surf, "In the dusty saloon, no one cares how smart you are.", FONT_S, (160,140,110), cx, 560, center=True)
                draw_text(surf, "Only which side of the table you sit on.", FONT_S, (160,140,110), cx, 582, center=True)

            # ═══════════════════════════════════════════════════════════
            # PAGE 55: 数据来源与方法
            # ═══════════════════════════════════════════════════════════
            elif page == 55:
                draw_text(surf, "METHODOLOGY & DATA SOURCES", FONT_T, C_GOLD_L, cx, 90, center=True)
                draw_text(surf, "All claims in this analysis are reproducible and verifiable.",
                          FONT_XS, (180,160,130), cx, 115, center=True)
                sections = [
                    ("SIMULATION METHODOLOGY", C_GOLD, [
                        "• 350,000 total games simulated across 7 experiments (50,000 each)",
                        "• Pure Python implementation, no pygame dependency (simulate.py)",
                        "• Each experiment tests a different strategy combination",
                        "• Win rates, average rounds, and round distributions recorded",
                        "• Results saved to simulation_results.json",
                    ]),
                    ("MATHEMATICAL ANALYSIS", C_GOLD, [
                        "• State space: ~1.8×10¹⁰ states (compressed to ~7.1×10⁶ effective states)",
                        "• Bellman equations solved for optimal strategies",
                        "• Nash equilibrium derived for both players",
                        "• Stackelberg game model (leader-follower)",
                        "• Full proof in MATHEMATICAL_ANALYSIS.md (11 chapters)",
                    ]),
                    ("STRATEGY TESTING", C_GOLD, [
                        "• P1 strategies: random, optimal mixed, ascending, descending, all-in bribe",
                        "• P2 strategies: random, optimal + 1g intel, no bribe",
                        "• Cross-comparison: 7 unique experiment configurations",
                        "• Each strategy tested against multiple opponent strategies",
                    ]),
                    ("REPRODUCIBILITY", C_BLOOD_L, [
                        "• Run: python simulate.py (generates fresh 350k games)",
                        "• Read: MATHEMATICAL_ANALYSIS.md (full proofs and methodology)",
                        "• Verify: simulation_results.json (raw data from all experiments)",
                        "• All code is open source at: github.com/kexin-dev/russian-roulette-poker",
                    ]),
                ]
                sy = 140
                for title, col, lines in sections:
                    draw_text(surf, title, FONT_B, col, cx, sy, center=True)
                    sy += 22
                    for line in lines:
                        draw_text(surf, line, FONT_XS, C_BONE, cx, sy, center=True)
                        sy += 16
                    sy += 10
                draw_text(surf, "No claims are made without evidence. No data is fabricated. Everything is verifiable.",
                          FONT_B, C_GOLD_L, cx, 590, center=True)

            # 底部操作提示（所有页面共用）
            draw_text(surf, "[A/D or ←/→] Flip Page  |  [ESC/ENTER] Back to Game Over",
                      FONT_S, (150,130,100), cx, H-30, center=True)
            # 页码进度条
            progress_w = 300
            progress_x = cx - progress_w // 2
            progress_y = H - 55
            pygame.draw.rect(surf, (40,30,15), (progress_x, progress_y, progress_w, 6), border_radius=3)
            fill_w = int((page + 1) / pages_total * progress_w)
            pygame.draw.rect(surf, C_GOLD_D, (progress_x, progress_y, fill_w, 6), border_radius=3)
        if self.phase in ('reveal','shooting','round_end'):
            helps = [
                "Rules: 50 gold each, hand 1-6 | Select -> Bribe -> Call/RAISE -> Reveal -> Loser shoots",
                "Hit chance = card/6  |  Tie = no penalty  |  Death or empty hand = game over",
                "All gold (bets + bribes) is DESTROYED | Opponent's total gold is SECRET",
            ]
            for i, line in enumerate(helps):
                draw_text(surf, line, FONT_XS, (180,160,130), 20, H-80+i*18, shadow=False)

# ═════════════════════════════════════════════════════════════════════
#  Main Loop
# ═════════════════════════════════════════════════════════════════════
def main():
    game = Game()
    audio.start_bgm()
    audio.start_ambience()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_m:
                audio.toggle_mute()
            game.handle(ev)
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    audio.stop_all()
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
