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
C_RUST      = (138,  74,  38)
C_BROWN     = ( 60,  40,  24)
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
def draw_card(surf, number, x, y, face_up=True, selected=False, scale=1.0):
    cw, ch = int(CARD_W*scale), int(CARD_H*scale)
    rect = pygame.Rect(x, y, cw, ch)
    shadow = make_alpha_surf(cw+6, ch+6, (0,0,0), 140)
    surf.blit(shadow, (x+3, y+3))
    if face_up and number in IMG_CARDS and IMG_CARDS[number]:
        img = IMG_CARDS[number]
        if scale != 1.0:
            img = pygame.transform.smoothscale(img, (cw, ch))
        surf.blit(img, rect.topleft)
    else:
        if IMG_CARD_BACK:
            img = IMG_CARD_BACK
            if scale != 1.0:
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
    def emit(self, x, y, color, count=30, speed=6, life=40):
        for _ in range(count):
            ang = random.uniform(0, math.pi*2)
            sp = random.uniform(1, speed)
            self.parts.append({
                "x":x,"y":y,"vx":math.cos(ang)*sp,"vy":math.sin(ang)*sp-random.uniform(0,2),
                "life":random.randint(life//2, life),"color":color[:3],"size":random.randint(2,5)
            })
    def update(self):
        for p in self.parts:
            p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.15; p["life"]-=1
        self.parts = [p for p in self.parts if p["life"]>0]
    def draw(self, surf):
        for p in self.parts:
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
    def draw(self, surf):
        hov = self.rect.collidepoint(pygame.mouse.get_pos()) and self.enabled
        base = self.hot if hov else self.col
        draw_rounded(surf, self.rect, 8, base, C_LEATHER_D, 2)
        pygame.draw.line(surf, (*C_GOLD_L[:3],80), (self.rect.x+4,self.rect.y+2),
                         (self.rect.right-4,self.rect.y+2), 2)
        tc = self.txt_col if self.enabled else (120,120,120)
        draw_text(surf, self.text, self.font, tc, self.rect.centerx, self.rect.centery, center=True)
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
            surf.blit(char_img, (cx-CHAR_W//2, base_y-10))
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
        for i, num in enumerate(self.hand):
            rx = start_x + i*spacing - CARD_W//2
            ry = hand_y
            sel = (self.pending_play == num)
            draw_card(surf, num, rx, ry, face_up=show_face, selected=sel)
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
        """生成关于某张牌的假情报（与真实相反）"""
        if card_val <= 2:
            return random.choice([
                "Opponent's card is huge! He's loaded for bear.",
                "Big card, real big. I'd be scared if I were you.",
                "He's packin' serious heat. Watch yourself.",
            ])
        elif card_val <= 4:
            return random.choice([
                "Opponent's card is tiny. Practically empty.",
                "Small card. He's got nothing.",
                "Light as a feather, that one.",
            ])
        else:
            return random.choice([
                "Opponent's card is tiny. Nothing to fear.",
                "Small card. He's bluffing if he acts tough.",
                "Barely a bullet in there. You'll be fine.",
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
        total = sum(self.bribes.values())
        ratio = top_amt / total if total > 0 else 0

        if ratio > 0.8:
            lines.append(f"({top.name.split('—')[0].strip()} is my sugar daddy tonight. I gotta play nice.)")
        elif ratio > 0.55:
            lines.append(f"({top.name.split('—')[0].strip()} paid well... I owe 'em one.)")
        else:
            lines.append("(Both paid up. I don't wanna cross either.)")

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
        pygame.draw.ellipse(surf, (70,44,24), (bx-260, by+80, 520, 60))
        if IMG_DEALER:
            surf.blit(IMG_DEALER, (bx-80, by-10))
        else:
            pygame.draw.polygon(surf, C_LEATHER, [(bx-36,by+72),(bx+36,by+72),(bx+48,by-8),(bx-48,by-8)])
            pygame.draw.circle(surf, (200,172,132), (bx, by-22), 20)
        pygame.draw.circle(surf, C_GOLD, (bx+70, by+50), 16)
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
        self._start_select()

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
            self.p1.bribe_amount = max(0, min(self.p1.gold, self.bribe_input.value))
            self.p1.gold -= self.p1.bribe_amount
            self._announce_turn(self.p2, "enter your bribe (0 = skip)")
            self.bribe_input = InputBox(W//2-70, 640, 140, 56, 0, 0, self.p2.gold, "Bribe Gold")
            self.buttons['strat'].text = "Strat: TRICK"
            self.p2.bribe_strategy = 'trick'
        else:
            self.p2.bribe_amount = max(0, min(self.p2.gold, self.bribe_input.value))
            self.p2.gold -= self.p2.bribe_amount
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
            # 开局叫价：选规则+下注
            self.bet_input = InputBox(W//2-70, 620, 140, 52, 1, 1, max_bet, "Bet Gold")
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
        amt = max(1, min(self.bet_turn.gold, self.bet_input.value))
        mode = self.buttons['mode'].text.split(':')[1].strip().lower()
        self.bet_mode = 'big' if mode == 'high' else 'small'
        self.bet_current = amt
        self.bet_turn.gold -= amt
        self.bet_turn.round_bet += amt
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

    def _check_gameover(self):
        return (not self.p1.alive) or (not self.p2.alive) or \
               (len(self.p1.hand)==0) or (len(self.p2.hand)==0)

    # ── Events ─────────────────────────────────────────────────────
    def handle(self, ev):
        if self.phase == 'menu':
            if 'start' in self.buttons and self.buttons['start'].check(ev):
                self.phase = 'contract'
                self.buttons = {}
        elif self.phase == 'contract':
            if 'accept' in self.buttons and self.buttons['accept'].check(ev):
                self.new_round()
        elif self.phase == 'bribe':
            if self.bribe_input: self.bribe_input.handle(ev)
            cp = self.current_player
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 'strat' in self.buttons and self.buttons['strat'].rect.collidepoint(ev.pos):
                    cp.bribe_strategy = 'honest' if cp.bribe_strategy=='trick' else 'trick'
                    self.buttons['strat'].text = f"Strat: {'TRICK' if cp.bribe_strategy=='trick' else 'HONEST'}"
            if 'bribe_ok' in self.buttons and self.buttons['bribe_ok'].check(ev):
                self._bribe_next()
        elif self.phase == 'select':
            cp = self.current_player
            if ev.type == pygame.MOUSEBUTTONDOWN and cp and cp.alive:
                for rect, num in cp.card_rects:
                    if rect.collidepoint(ev.pos):
                        cp.pending_play = num if cp.pending_play != num else None
                        return
            if 'play_btn' in self.buttons and self.buttons['play_btn'].check(ev):
                if cp and cp.pending_play is not None:
                    cp.selected_card = cp.pending_play
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
                        cur = self.buttons['mode'].text
                        self.buttons['mode'].text = "Mode: LOW" if "HIGH" in cur else "Mode: HIGH"
                if 'call' in self.buttons and self.buttons['call'].check(ev):
                    self._place_opening_bet()
            else:
                # 跟注/加注
                if 'call' in self.buttons and self.buttons['call'].check(ev):
                    self._call_bet()
                elif 'raise' in self.buttons and self.buttons['raise'].check(ev):
                    self._raise_bet()
        elif self.phase == 'round_end':
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                if self._check_gameover(): self.phase = 'gameover'
                else: self.new_round()
        elif self.phase == 'gameover':
            if 'restart' in self.buttons and self.buttons['restart'].check(ev):
                self.reset_all()

    # ── Update ─────────────────────────────────────────────────────
    def update(self):
        self.particles.update()
        if self.turn_announce_timer > 0:
            self.turn_announce_timer -= 1
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.phase == 'reveal':
                self._resolve_round()
        if self.phase == 'shooting' and self.shoot_target:
            self.shoot_anim -= 1
            t = 180 - self.shoot_anim
            if t == 25:
                self.muzzle_flash = 15
                self.screen_shake = 8
            if t == 30:
                bullet = self.shoot_target.selected_card
                hit = random.random() < bullet/6.0
                if hit:
                    self.shoot_target.alive = False
                    self.shoot_target.set_mood("dead")
                    self.flash_alpha = 255
                    self.blood_alpha = 255
                    self.screen_shake = 25
                    self.particles.emit(W//2, H//2-40, C_BLOOD, 120, 16, 70)
                    self.particles.emit(W//2, H//2-40, (200,50,50), 60, 10, 50)
                    self.message = f"{self.shoot_target.name} takes a bullet to the skull! DEAD"
                    other = self.p2 if self.shoot_target==self.p1 else self.p1
                    other.set_mood("victory")
                else:
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
            alpha = min(255, self.turn_announce_timer * 4)
            banner = make_alpha_surf(W, 80, C_BROWN, min(220, alpha))
            canvas.blit(banner, (0, H//2-40))
            pygame.draw.line(canvas, C_GOLD, (0, H//2-40), (W, H//2-40), 3)
            pygame.draw.line(canvas, C_GOLD, (0, H//2+40), (W, H//2+40), 3)
            name = self.current_player.name
            draw_text(canvas, f"{name}'S TURN", FONT_H, C_GOLD_L, W//2, H//2, center=True)
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
        if IMG_ROULETTE and self.phase in ('shooting','round_end','reveal','betting'):
            surf.blit(IMG_ROULETTE, (cx-70, 370))
        if self.phase in ('reveal','betting','shooting','round_end'):
            cards_up = self.phase in ('reveal','shooting','round_end')
            if self.p1.selected_card is not None:
                draw_card(surf, self.p1.selected_card, cx-200, 470, face_up=cards_up, scale=1.1)
            if self.p2.selected_card is not None:
                draw_card(surf, self.p2.selected_card, cx+110, 470, face_up=cards_up, scale=1.1)
            if self.bet_mode and cards_up:
                mode_txt = "HIGH" if self.bet_mode=='big' else "LOW"
                draw_text(surf, mode_txt, FONT_H, C_BLOOD, cx, 420, center=True)
        pot = self.p1.round_bet + self.p2.round_bet
        if pot > 0 or self.phase == 'betting':
            destroyed = self.p1.round_bet + self.p2.round_bet + self.p1.bribe_amount + self.p2.bribe_amount
            draw_text(surf, f"Pot: {pot}g bet + {self.p1.bribe_amount + self.p2.bribe_amount}g bribed = {destroyed}g DESTROYED",
                      FONT_B, C_GOLD, cx, 628, center=True)

    def _draw_topbar(self, surf):
        bar = pygame.Rect(10, 8, W-20, 52)
        draw_rounded(surf, bar, 10, (*C_BROWN[:3], 220), C_LEATHER, 2)
        draw_text(surf, f"Round {self.round_num}", FONT_B, C_GOLD_L, 30, 34)
        phase_cn = {
            'menu':'Menu','bribe':'Bribe','select':'Select',
            'reveal':'Reveal','betting':'Betting','shooting':'Shooting',
            'round_end':'Round End','gameover':'Game Over'
        }
        draw_text(surf, f"Phase: {phase_cn.get(self.phase,'')}", FONT_B, C_BONE, 180, 34)
        draw_text(surf, self.message, FONT, C_BONE, W//2, 34, center=True)
        draw_text(surf, f"Dealer: {self.dealer.gold}g", FONT_S, C_GOLD, W-40, 34, center=True)

    def _draw_ui(self, surf):
        cx = W//2
        if self.phase == 'menu':
            self.buttons['start'] = Button(cx-140, H//2+80, 280, 72, "START GAME", font=FONT_H, col=C_RUST, hot=C_BLOOD)
            self.buttons['start'].draw(surf)
            draw_text(surf, "BULLET", FONT_H, C_GOLD, cx, H//2-140, center=True)
            draw_text(surf, "CARDS", FONT_H, C_BLOOD, cx, H//2-70, center=True)
            draw_text(surf, "Doomsday Western — Two-Player Duel", FONT_T, C_BONE, cx, H//2-10, center=True)
            draw_text(surf, "Snake vs Lizard  \u2022  Bribe  \u2022  Bluff  \u2022  Survive", FONT_B, C_GOLD_L, cx, H//2+30, center=True)
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
            if not self.p1.alive or len(self.p1.hand) == 0:
                winner = self.p2
                reason = "Snake took a bullet" if not self.p1.alive else "Snake ran out of cards"
            else:
                winner = self.p1
                reason = "Lizard took a bullet" if not self.p2.alive else "Lizard ran out of cards"
            draw_text(surf, "GAME OVER", FONT_H, C_BLOOD, cx, H//2-120, center=True)
            draw_text(surf, f"{winner.name} WINS!", FONT_H, C_GOLD, cx, H//2-40, center=True)
            draw_text(surf, reason, FONT_B, C_BONE, cx, H//2+10, center=True)
            draw_text(surf, f"Remaining Gold — {winner.name}: {winner.gold} | Dealer: {self.dealer.gold}",
                      FONT_B, C_GOLD_L, cx, H//2+44, center=True)
            self.buttons['restart'] = Button(cx-130, H//2+100, 260, 60, "PLAY AGAIN", font=FONT_T, col=C_RUST, hot=C_BLOOD)
            self.buttons['restart'].draw(surf)
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
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: running = False
            game.handle(ev)
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
