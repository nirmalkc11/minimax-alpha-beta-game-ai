import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List

@dataclass(frozen=True)
class State:
    r: int
    b: int
    to_move: str   # "computer" or "human"
    version: str   # "standard" or "misere"

def is_terminal(s: State) -> bool:
    # Terminal is checked at the start of a player's turn
    return s.r == 0 or s.b == 0

def terminal_score(s: State) -> int:
    # Score = +/- (2*r + 3*b), sign depends on version and whose turn it is.
    score = 2 * s.r + 3 * s.b
    if s.version == "standard":
        # Current player loses that many points.
        return -score if s.to_move == "computer" else score
    else:  # misere
        # Current player wins that many points.
        return score if s.to_move == "computer" else -score

def legal_moves(s: State) -> List[Tuple[str,int]]:
    # Return moves in required order based on version.
    # A move is a tuple (pile, k) where pile in {"R","B"} and k in {1,2}.
    order_standard = [("R",2), ("B",2), ("R",1), ("B",1)]
    order_misere   = [("B",1), ("R",1), ("B",2), ("R",2)]  # inverted
    order = order_standard if s.version == "standard" else order_misere

    moves = []
    for pile,k in order:
        if pile == "R" and s.r >= k:
            moves.append((pile,k))
        if pile == "B" and s.b >= k:
            moves.append((pile,k))
    return moves

def apply_move(s: State, move: Tuple[str,int]) -> State:
    pile,k = move
    if pile == "R":
        return State(s.r - k, s.b, "human" if s.to_move == "computer" else "computer", s.version)
    else:
        return State(s.r, s.b - k, "human" if s.to_move == "computer" else "computer", s.version)

def eval_state(s: State) -> int:
    
    # Heuristic for depth-limited search (Extra Credit).
    
    base = 2 * s.r + 3 * s.b
    lm_now = len(legal_moves(s))
    # approximate opponent mobility by averaging over successors (cheap fallback if none)
    opp_cands = legal_moves(s)
    if opp_cands:
        next_states = [apply_move(s, m) for m in opp_cands]
        lm_opp_avg = sum(len(legal_moves(ns)) for ns in next_states) / len(next_states)
    else:
        lm_opp_avg = 0.0
    mobility = lm_now - lm_opp_avg

    # Signs
    base_sign_standard = (-1 if s.to_move == "computer" else +1)
    base_sign = base_sign_standard if s.version == "standard" else -base_sign_standard
    mobility_sign = (+1 if s.to_move == "computer" else -1)

    val = base_sign * base + int(2 * mobility_sign * mobility)
    # Always from computer perspective
    return val

def minimax(s: State, alpha: int, beta: int, depth: Optional[int]) -> Tuple[int, Optional[Tuple[str,int]]]:
    # Returns (value_from_computer_perspective, best_move)
    # If depth is None => full search to terminal; else depth-limited with eval at leaf.
    if is_terminal(s):
        return terminal_score(s), None
    if depth is not None and depth <= 0:
        return eval_state(s), None

    moves = legal_moves(s)
    if not moves:  # no legal move (shouldn't happen unless both piles <1)
        # Treat as pass-to-opponent; but better to consider terminal check already handled.
        return eval_state(s), None

    best_move = None
    if s.to_move == "computer":
        value = -10**9
        for m in moves:
            ns = apply_move(s, m)
            v, _ = minimax(ns, alpha, beta, None if depth is None else depth-1)
            if v > value:
                value, best_move = v, m
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, best_move
    else:
        value = +10**9
        for m in moves:
            ns = apply_move(s, m)
            v, _ = minimax(ns, alpha, beta, None if depth is None else depth-1)
            if v < value:
                value, best_move = v, m
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

def parse_args(argv: List[str]) -> Tuple[int,int,str,str,Optional[int]]:
    if len(argv) < 3:
        print("Usage: python red_blue_nim.py <num-red> <num-blue> [standard|misere] [computer|human] [depth]")
        sys.exit(1)
    r = int(argv[1]); b = int(argv[2])
    version = "standard"
    first = "computer"
    depth = None
    if len(argv) >= 4:
        v = argv[3].lower()
        if v in ("standard","misere"):
            version = v
        else:
            # If 3rd arg is first-player instead, shift
            if v in ("computer","human"):
                first = v
            else:
                print("Error: <version> must be 'standard' or 'misere'.")
                sys.exit(1)
    if len(argv) >= 5:
        w = argv[4].lower()
        if w in ("computer","human"):
            first = w
        else:
            try:
                depth = int(argv[4]);  # allow depth in 5th position by mistake
            except:
                print("Error: <first-player> must be 'computer' or 'human'.")
                sys.exit(1)
    if len(argv) >= 6:
        try:
            depth = int(argv[5])
        except:
            print("Error: <depth> must be an integer.")
            sys.exit(1)
    if r < 0 or b < 0:
        print("Error: marbles must be non-negative.")
        sys.exit(1)
    return r,b,version,first,depth

def prompt_human_move(s: State) -> Tuple[str,int]:
    # Expected formats:
    #   R 1   or   B 2
    # Case-insensitive. Re-prompt on invalid.
    while True:
        try:
            raw = input("Your move (format: R 1, R 2, B 1, B 2): ").strip()
            parts = raw.split()
            if len(parts) != 2:
                raise ValueError
            pile = parts[0].upper()
            k = int(parts[1])
            if pile not in ("R","B") or k not in (1,2):
                raise ValueError
            move = (pile,k)
            if move not in legal_moves(s):
                print("Illegal move for current state. Try again.")
                continue
            return move
        except ValueError:
            print("Invalid input. Example: R 2")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)

def pretty_state(s: State) -> str:
    return f"[R={s.r}, B={s.b}, to_move={s.to_move}, version={s.version}]"

def game_loop(r: int, b: int, version: str, first: str, depth: Optional[int]) -> None:
    s = State(r,b,first,version)
    print(f"Starting game: {pretty_state(s)}")
    if depth is None:
        print("Search: full-depth to terminal.")
    else:
        print(f"Search: depth-limited with depth={depth} (alpha-beta + heuristic).")

    # Main alternation until terminal at START of a turn
    while True:
        if is_terminal(s):
            # Game ends immediately at start of this player's turn
            score = 2*s.r + 3*s.b
            if version == "standard":
                loser = s.to_move
                winner = "computer" if loser == "human" else "human"
                if loser == "computer":
                    print(f"Terminal: pile empty at computer's turn, computer loses {score} points.")
                    print(f"Winner: human (+{score}), Loser: computer (-{score})")
                else:
                    print(f"Terminal: pile empty at human's turn, human loses {score} points.")
                    print(f"Winner: computer (+{score}), Loser: human (-{score})")
            else:  # misere
                winner = s.to_move
                loser = "computer" if winner == "human" else "human"
                if winner == "computer":
                    print(f"Terminal: pile empty at computer's turn, computer wins {score} points.")
                    print(f"Winner: computer (+{score}), Loser: human (-{score})")
                else:
                    print(f"Terminal: pile empty at human's turn, human wins {score} points.")
                    print(f"Winner: human (+{score}), Loser: computer (-{score})")
            return

        print(f"\nCurrent state: R={s.r}, B={s.b}. To move: {s.to_move}")
        print(f"RULES: {'Lose if pile empty on your turn' if s.version=='standard' else 'Win if pile empty on your turn'}")
        if s.to_move == "computer":
            value, move = minimax(s, alpha=-10**9, beta=10**9, depth=depth)
            assert move is not None
            pile, k = move
            print(f"Computer chooses: {pile} {k} (expected value={value})")
            s = apply_move(s, move)
        else:
            move = prompt_human_move(s)
            s = apply_move(s, move)

def main():
    r,b,version,first,depth = parse_args(sys.argv)
    game_loop(r,b,version,first,depth)

if __name__ == "__main__":
    main()
