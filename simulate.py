"""
Bullet Cards — 大规模模拟与数学分析
不依赖 pygame，纯逻辑模拟，可快速跑 10 万+ 对局
"""
import random
import json
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════
#  核心游戏逻辑（与 game_v2.py 一致，去掉渲染）
# ═══════════════════════════════════════════════════════════════════

class SimPlayer:
    def __init__(self, name, side):
        self.name = name
        self.side = side
        self.reset()
    def reset(self):
        self.gold = 50
        self.hand = [1,2,3,4,5,6]
        self.alive = True
        self.selected_card = None
        self.round_bet = 0
        self.bribe_amount = 0
        self.bribe_strategy = 'trick'
        self.private_hint = "..."

class SimGame:
    def __init__(self, p1_strategy='random', p2_strategy='random',
                 p1_bribe='random', p2_bribe='random', verbose=False):
        self.p1 = SimPlayer("P1", 'left')
        self.p2 = SimPlayer("P2", 'right')
        self.p1_strategy = p1_strategy
        self.p2_strategy = p2_strategy
        self.p1_bribe = p1_bribe
        self.p2_bribe = p2_bribe
        self.verbose = verbose
        self.round_num = 0
        self.log = []

    def _pick_card(self, player, strategy):
        """根据策略选牌"""
        if not player.hand:
            return None
        if strategy == 'random':
            return random.choice(player.hand)
        elif strategy == 'always_6':
            return 6 if 6 in player.hand else max(player.hand)
        elif strategy == 'always_1':
            return 1 if 1 in player.hand else min(player.hand)
        elif strategy == 'p1_optimal':
            # P1最优混合策略：出3占87.5%、出1占7%、出6占5.6%
            available = player.hand
            r = random.random()
            if r < 0.875 and 3 in available:
                return 3
            elif r < 0.945 and 1 in available:
                return 1
            elif 6 in available:
                return 6
            else:
                return random.choice(available)
        elif strategy == 'p2_optimal':
            # P2最优策略：出6+HIGH占91.3%，出2+LOW占7.5%
            available = player.hand
            r = random.random()
            if r < 0.913 and 6 in available:
                return 6
            elif r < 0.988 and 2 in available:
                return 2
            else:
                return random.choice(available)
        elif strategy == 'ascending':
            return min(player.hand)
        elif strategy == 'descending':
            return max(player.hand)
        return random.choice(player.hand)

    def _bribe_amount(self, player, strategy):
        """根据策略决定贿赂金额"""
        if strategy == 'none':
            return 0
        elif strategy == 'one':
            return 1 if player.gold >= 1 else 0
        elif strategy == 'all':
            return player.gold
        elif strategy == 'half':
            return player.gold // 2
        elif strategy == 'random':
            return random.randint(0, min(player.gold, 20))
        return random.randint(0, player.gold)

    def _resolve_bribe(self):
        """贿赂结算：金主得真情报，对手得假/真情报"""
        bribes = {}
        for p in (self.p1, self.p2):
            if p.bribe_amount > 0 and p.alive:
                bribes[p] = p.bribe_amount
        if not bribes:
            for p in (self.p1, self.p2):
                p.private_hint = "vague"
            return
        sorted_b = sorted(bribes.items(), key=lambda kv: kv[1], reverse=True)
        top, top_amt = sorted_b[0]
        opponent = self.p2 if top == self.p1 else self.p1
        # 金主得真情报
        opp_card = opponent.selected_card
        if opp_card <= 2:
            top.private_hint = "small"
        elif opp_card <= 4:
            top.private_hint = "medium"
        else:
            top.private_hint = "large"
        # 对手得假/真情报
        if top.bribe_strategy == 'trick':
            # 假情报：三档都可能出现（修复后的逻辑）
            if opp_card <= 2:
                opponent.private_hint = random.choice(["medium", "large"])
            elif opp_card <= 4:
                opponent.private_hint = random.choice(["small", "large"])
            else:
                opponent.private_hint = random.choice(["small", "medium"])
        else:
            # honest：给真情报
            if opp_card <= 2:
                opponent.private_hint = "small"
            elif opp_card <= 4:
                opponent.private_hint = "medium"
            else:
                opponent.private_hint = "large"

    def _betting_phase(self):
        """下注阶段：P1开叫，P2跟注/加注，最多3次加注"""
        # P1开叫：定规则+下注
        p1_bet = min(self.p1.gold, random.randint(1, max(1, self.p1.gold)))
        # P1策略：有情报时根据情报定规则
        if self.p1.private_hint == "large":
            # 对手牌大，P1应该叫LOW（小牌赢），但P1不知道自己的牌相对大小
            p1_mode = random.choice(['big', 'small'])
        elif self.p1.private_hint == "small":
            p1_mode = random.choice(['big', 'small'])
        else:
            p1_mode = random.choice(['big', 'small'])
        # P2最优策略：有情报时选对自己有利的规则
        p2_card = self.p2.selected_card
        p1_card = self.p1.selected_card
        # P2知道自己的牌，有情报知道P1的牌，可以选规则
        if self.p2.private_hint in ("small", "medium", "large"):
            # P2有情报，根据双方牌选规则
            if p2_card > p1_card:
                p2_wants = 'big'  # P2大牌，想要HIGH
            else:
                p2_wants = 'small'  # P2小牌，想要LOW
        else:
            p2_wants = random.choice(['big', 'small'])

        self.p1.gold -= p1_bet
        self.p1.round_bet = p1_bet
        current_bet = p1_bet
        current_mode = p1_mode
        raise_count = 0
        turn = self.p2  # P2先响应

        # 最多3次加注
        while raise_count < 3:
            if turn == self.p2:
                # P2决策：跟注或加注
                # P2有规则决定权优势
                if raise_count == 0:
                    # 第一次响应：P2可以直接加注翻转规则
                    if current_mode != p2_wants and self.p2.gold > current_bet:
                        # 翻转规则对P2有利，加注
                        raise_amt = min(self.p2.gold, current_bet + random.randint(1, 10))
                        owed = raise_amt - self.p2.round_bet
                        owed = min(owed, self.p2.gold)
                        self.p2.gold -= owed
                        self.p2.round_bet += owed
                        current_bet = raise_amt
                        current_mode = p2_wants  # 翻转
                        raise_count += 1
                        turn = self.p1
                        continue
                # 跟注
                owed = current_bet - self.p2.round_bet
                owed = min(owed, self.p2.gold)
                self.p2.gold -= owed
                self.p2.round_bet += owed
                break
            else:
                # P1响应：跟注或加注
                # P1信息劣势，通常跟注
                if random.random() < 0.3 and self.p1.gold > current_bet and raise_count < 2:
                    # 偶尔加注
                    raise_amt = min(self.p1.gold, current_bet + random.randint(1, 10))
                    owed = raise_amt - self.p1.round_bet
                    owed = min(owed, self.p1.gold)
                    self.p1.gold -= owed
                    self.p1.round_bet += owed
                    current_bet = raise_amt
                    current_mode = 'small' if current_mode == 'big' else 'big'
                    raise_count += 1
                    turn = self.p2
                    continue
                # 跟注
                owed = current_bet - self.p1.round_bet
                owed = min(owed, self.p1.gold)
                self.p1.gold -= owed
                self.p1.round_bet += owed
                break

        return current_mode

    def _resolve_round(self, mode):
        """结算回合：比大小，输家开枪"""
        c1, c2 = self.p1.selected_card, self.p2.selected_card
        if (mode == 'big' and c1 > c2) or (mode == 'small' and c1 < c2):
            winner, loser = self.p1, self.p2
        elif (mode == 'big' and c1 < c2) or (mode == 'small' and c1 > c2):
            winner, loser = self.p2, self.p1
        else:
            # 平局
            return 'tie', None

        # 输家开枪
        bullet = loser.selected_card
        hit = random.random() < bullet / 6.0
        if hit:
            loser.alive = False
            return 'death', loser
        else:
            return 'survive', loser

    def play_one_game(self):
        """玩一整局，返回结果"""
        while self.p1.alive and self.p2.alive and self.p1.hand and self.p2.hand:
            self.round_num += 1
            # 选牌
            self.p1.selected_card = self._pick_card(self.p1, self.p1_strategy)
            self.p2.selected_card = self._pick_card(self.p2, self.p2_strategy)
            if self.p1.selected_card is None or self.p2.selected_card is None:
                break
            # 贿赂
            self.p1.bribe_amount = self._bribe_amount(self.p1, self.p1_bribe)
            self.p2.bribe_amount = self._bribe_amount(self.p2, self.p2_bribe)
            self.p1.gold -= self.p1.bribe_amount
            self.p2.gold -= self.p2.bribe_amount
            self._resolve_bribe()
            # 下注
            mode = self._betting_phase()
            # 结算
            result, loser = self._resolve_round(mode)
            # 移除已出的牌
            if self.p1.selected_card in self.p1.hand:
                self.p1.hand.remove(self.p1.selected_card)
            if self.p2.selected_card in self.p2.hand:
                self.p2.hand.remove(self.p2.selected_card)
            # 重置回合状态
            for p in (self.p1, self.p2):
                p.round_bet = 0
                p.bribe_amount = 0
                p.selected_card = None
            if result == 'death':
                break

        # 判断胜者
        if not self.p1.alive:
            return {'winner': 'p2', 'rounds': self.round_num,
                    'p1_gold': self.p1.gold, 'p2_gold': self.p2.gold}
        elif not self.p2.alive:
            return {'winner': 'p1', 'rounds': self.round_num,
                    'p1_gold': self.p1.gold, 'p2_gold': self.p2.gold}
        elif not self.p1.hand:
            return {'winner': 'p2', 'rounds': self.round_num, 'reason': 'p1_no_cards',
                    'p1_gold': self.p1.gold, 'p2_gold': self.p2.gold}
        elif not self.p2.hand:
            return {'winner': 'p1', 'rounds': self.round_num, 'reason': 'p2_no_cards',
                    'p1_gold': self.p1.gold, 'p2_gold': self.p2.gold}
        return {'winner': 'unknown', 'rounds': self.round_num}


# ═══════════════════════════════════════════════════════════════════
#  大规模模拟
# ═══════════════════════════════════════════════════════════════════

def run_simulation(n=100000, p1_strategy='random', p2_strategy='random',
                    p1_bribe='random', p2_bribe='random', label=""):
    """跑n局模拟，返回统计结果"""
    results = []
    for i in range(n):
        game = SimGame(p1_strategy, p2_strategy, p1_bribe, p2_bribe)
        results.append(game.play_one_game())

    p1_wins = sum(1 for r in results if r['winner'] == 'p1')
    p2_wins = sum(1 for r in results if r['winner'] == 'p2')
    avg_rounds = sum(r['rounds'] for r in results) / len(results)
    round_dist = defaultdict(int)
    for r in results:
        round_dist[r['rounds']] += 1

    return {
        'label': label,
        'n': n,
        'p1_wins': p1_wins,
        'p2_wins': p2_wins,
        'p1_winrate': p1_wins / n * 100,
        'p2_winrate': p2_wins / n * 100,
        'avg_rounds': avg_rounds,
        'round_dist': dict(round_dist),
        'p1_strategy': p1_strategy,
        'p2_strategy': p2_strategy,
        'p1_bribe': p1_bribe,
        'p2_bribe': p2_bribe,
    }


def main():
    print("=" * 70)
    print("  BULLET CARDS — 大规模数学模拟")
    print("=" * 70)

    all_results = []

    # 实验1：双方随机策略，随机贿赂（基准）
    print("\n[实验1] 双方随机策略 + 随机贿赂（基准）...")
    r = run_simulation(50000, 'random', 'random', 'random', 'random', "随机 vs 随机")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验2：P1最优 vs P2最优
    print("\n[实验2] P1最优混合策略 vs P2最优策略...")
    r = run_simulation(50000, 'p1_optimal', 'p2_optimal', 'none', 'one', "P1最优 vs P2最优+1金贿赂")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验3：P2有情报（1金贿赂）vs P1无情报
    print("\n[实验3] P2花1金买情报 vs P1不贿赂...")
    r = run_simulation(50000, 'random', 'random', 'none', 'one', "P2买情报 vs P1不买")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验4：P1全砸贿赂 vs P2 1金贿赂
    print("\n[实验4] P1全砸贿赂 vs P2 1金贿赂...")
    r = run_simulation(50000, 'random', 'random', 'all', 'one', "P1全砸 vs P2 1金")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验5：P1升序出牌（拖延）vs P2随机
    print("\n[实验5] P1升序出牌（拖延）vs P2随机...")
    r = run_simulation(50000, 'ascending', 'random', 'none', 'none', "P1升序 vs P2随机")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验6：P1降序出牌（赌命）vs P2随机
    print("\n[实验6] P1降序出牌（赌命）vs P2随机...")
    r = run_simulation(50000, 'descending', 'random', 'none', 'none', "P1降序 vs P2随机")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 实验7：双方都不贿赂（纯随机）
    print("\n[实验7] 双方都不贿赂（纯随机无情报）...")
    r = run_simulation(50000, 'random', 'random', 'none', 'none', "无贿赂纯随机")
    print(f"  P1胜率: {r['p1_winrate']:.1f}%  P2胜率: {r['p2_winrate']:.1f}%  平均轮次: {r['avg_rounds']:.2f}")
    all_results.append(r)

    # 保存结果
    with open('simulation_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("  模拟完成！结果已保存到 simulation_results.json")
    print("=" * 70)

    # 打印汇总表
    print("\n" + "=" * 90)
    print(f"{'实验':<30} {'P1胜率':>8} {'P2胜率':>8} {'平均轮次':>8}")
    print("-" * 90)
    for r in all_results:
        print(f"{r['label']:<30} {r['p1_winrate']:>7.1f}% {r['p2_winrate']:>7.1f}% {r['avg_rounds']:>8.2f}")
    print("=" * 90)


if __name__ == '__main__':
    main()
