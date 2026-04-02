"""
hash_function.py
================
Custom Polynomial Rolling Hash  —  implemented from scratch
No built-in cryptography libraries are used.

WHY THIS HASH?
--------------
A polynomial rolling hash assigns a weight to each character based on its
position using a prime base (BASE) and reduces the result modulo a large
prime (MOD).  This is a well-studied approach in competitive programming
and computer science (e.g., Rabin-Karp string matching).

Formula:
    H = sum( ord(ch[i]) * BASE^i )  mod  MOD
        for i = 0, 1, 2, ..., len(s)-1

Properties that make it suitable for this cipher project:
  - Deterministic  : same input always produces the same output
  - Sensitive      : a single character change avalanches through the hash
  - Collision-resistant (for practical inputs) : large MOD keeps collisions rare
  - Fast           : O(n) time, O(1) space
  - No external libs: pure Python arithmetic only

BASE and MOD are both prime which minimises clustering of outputs.
"""

# ──────────────────────────────────────────────
#  PARAMETERS
# ──────────────────────────────────────────────

BASE = 131      # prime just above 128 (covers all printable ASCII values)
MOD  = (1 << 61) - 1   # Mersenne prime  2^61 - 1  (large, collision-resistant)


# ──────────────────────────────────────────────
#  CORE HASH
# ──────────────────────────────────────────────

def poly_hash(text: str) -> int:
    """
    Polynomial rolling hash over the full text.

    H = sum_{i=0}^{n-1}  ord(text[i]) * BASE^i   (mod MOD)

    Returns an integer in [0, MOD-1].
    """
    result = 0
    power  = 1          # BASE^0 = 1
    for ch in text:
        result = (result + ord(ch) * power) % MOD
        power  = (power * BASE) % MOD
    return result


# ──────────────────────────────────────────────
#  DISPLAY HELPER
# ──────────────────────────────────────────────

def show_hash_working(text: str) -> None:
    """Print a step-by-step breakdown of the hash computation."""
    print(f"\n  Polynomial Rolling Hash  (BASE={BASE}, MOD=2^61-1)")
    print(f"  Formula: H = Σ ord(ch[i]) × {BASE}^i  (mod {MOD})\n")
    print(f"  {'i':<6} {'ch':<6} {'ord':<6} {'BASE^i (mod MOD)':<30} {'term (mod MOD)'}")
    print(f"  {'─'*70}")

    result = 0
    power  = 1
    for i, ch in enumerate(text):
        term   = (ord(ch) * power) % MOD
        result = (result + term)  % MOD
        # Only print first 10 and last row to keep output manageable
        if i < 10 or i == len(text) - 1:
            print(f"  {i:<6} {repr(ch):<6} {ord(ch):<6} {power:<30} {term}")
        elif i == 10:
            print(f"  {'...':<6}")
        power = (power * BASE) % MOD

    print(f"\n  Final hash  =  {result}")
    return result


# ──────────────────────────────────────────────
#  MAIN  (standalone demo)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("   CUSTOM POLYNOMIAL ROLLING HASH  —  demo")
    print("=" * 60)

    examples = [
        "hello",
        "Hello",          # differs only in case
        "hello world",
        "SecretKey123!",
        "The quick brown fox jumps over the lazy dog",
    ]

    for s in examples:
        h = poly_hash(s)
        print(f"\n  Input  : {repr(s)}")
        print(f"  Hash   : {h}")

    # Interactive
    print("\n" + "─" * 60)
    while True:
        user_input = input("\n  Enter a string to hash (or 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            print("  Bye!")
            break
        h = poly_hash(user_input)
        print(f"  Hash   : {h}")
        show_steps = input("  Show step-by-step? (y/n): ").strip().lower()
        if show_steps == 'y':
            show_hash_working(user_input)
