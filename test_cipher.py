"""
test_cipher.py
==============
Automated test script demonstrating the full pipeline:

    plaintext  ──encrypt──>  ciphertext  ──hash──>  hash_digest
                                  │
                             ──decrypt──>  recovered_plaintext

All tests assert that decrypt(encrypt(plaintext)) == plaintext  (round-trip).
The hash of the ciphertext is also printed for each test case.

No external testing frameworks required — pure Python.
"""

from affine_cipher import encrypt, decrypt, derive_keys, simple_hash, SPECIAL_CHARS
from hash_function  import poly_hash

# ──────────────────────────────────────────────────────────────
#  ANSI colour helpers (graceful fallback on Windows)
# ──────────────────────────────────────────────────────────────
try:
    import os, sys
    _colour = sys.platform != "win32" or os.environ.get("ANSICON")
except Exception:
    _colour = False

def green(s):  return f"\033[92m{s}\033[0m" if _colour else s
def red(s):    return f"\033[91m{s}\033[0m" if _colour else s
def cyan(s):   return f"\033[96m{s}\033[0m" if _colour else s
def bold(s):   return f"\033[1m{s}\033[0m"  if _colour else s


# ──────────────────────────────────────────────────────────────
#  TEST CASES
# ──────────────────────────────────────────────────────────────

TEST_CASES = [
    # (description, passphrase, plaintext)
    (
        "Basic lowercase sentence",
        "secret",
        "hello world"
    ),
    (
        "Mixed case with punctuation",
        "MyP@ssw0rd",
        "Hello, World! How are you?"
    ),
    (
        "Numbers and special characters",
        "alpha123",
        "Price: $19.99 — Sale 50% off!"
    ),
    (
        "All uppercase",
        "CIPHER",
        "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    ),
    (
        "Passphrase same as plaintext edge case",
        "test",
        "test"
    ),
    (
        "Long message",
        "longpassphrase!",
        "In cryptography, an affine cipher is a type of monoalphabetic substitution cipher, "
        "where each letter in an alphabet is mapped to its numeric equivalent, encrypted using "
        "a simple mathematical function f(x) = (Ax + B) mod 26."
    ),
    (
        "Digits only in plaintext",
        "numkey",
        "1234567890"
    ),
    (
        "Symbols only",
        "symkey",
        "!@#$%^&*()-_=+[]{}|;':\",./<>?"
    ),
]


# ──────────────────────────────────────────────────────────────
#  RUN TESTS
# ──────────────────────────────────────────────────────────────

def run_tests():
    print(bold("\n" + "=" * 70))
    print(bold("   AFFINE CIPHER — Encrypt → Hash → Decrypt Round-Trip Test Suite"))
    print(bold("=" * 70))

    passed = 0
    failed = 0

    for idx, (desc, passphrase, plaintext) in enumerate(TEST_CASES, 1):
        print(f"\n{cyan(f'Test {idx}: {desc}')}")
        print(f"  Passphrase : {repr(passphrase)}")

        # Derive keys
        A, B = derive_keys(passphrase)
        print(f"  Keys       : A = {A},  B = {B}")

        # Step 1 — Encrypt
        ciphertext = encrypt(plaintext, A, B)
        print(f"  Plaintext  : {repr(plaintext)}")
        print(f"  Ciphertext : {repr(ciphertext)}")

        # Step 2 — Hash the ciphertext
        h = poly_hash(ciphertext)
        print(f"  Hash(cipher): {h}")

        # Step 3 — Decrypt
        recovered = decrypt(ciphertext, A, B)
        print(f"  Recovered  : {repr(recovered)}")

        # Assert round-trip
        if recovered == plaintext:
            print(f"  Result     : {green('PASS')} ✓  (round-trip verified)")
            passed += 1
        else:
            print(f"  Result     : {red('FAIL')} ✗  (mismatch!)")
            print(f"    Expected : {repr(plaintext)}")
            print(f"    Got      : {repr(recovered)}")
            failed += 1

    # ── Summary ──────────────────────────────────────────────
    print(bold("\n" + "=" * 70))
    print(bold(f"   Results: {passed} passed, {failed} failed  (out of {len(TEST_CASES)} tests)"))
    print(bold("=" * 70 + "\n"))

    # ── Extra: hash sensitivity demo ─────────────────────────
    print(cyan("Hash Sensitivity Demo — small input changes → large hash change"))
    print("─" * 55)
    sensitivity_pairs = [
        ("hello", "Hello"),
        ("secret", "Secret"),
        ("abc", "abd"),
        ("test123", "test124"),
    ]
    for a, b in sensitivity_pairs:
        ha, hb = poly_hash(a), poly_hash(b)
        print(f"  {repr(a):<15} hash = {ha}")
        print(f"  {repr(b):<15} hash = {hb}")
        print(f"  Difference   = {abs(ha - hb)}")
        print()

    return failed == 0


# ──────────────────────────────────────────────────────────────
#  WORKED EXAMPLES  (printed in detail for the README)
# ──────────────────────────────────────────────────────────────

def print_worked_examples():
    print(bold("\n" + "=" * 70))
    print(bold("   WORKED EXAMPLES  (step-by-step)"))
    print(bold("=" * 70))

    examples = [
        ("hello world", "secret"),
        ("Hello, World! How are you?", "MyP@ssw0rd"),
    ]

    for plaintext, passphrase in examples:
        A, B = derive_keys(passphrase)
        ciphertext = encrypt(plaintext, A, B)
        recovered  = decrypt(ciphertext, A, B)
        h_plain    = poly_hash(plaintext)
        h_cipher   = poly_hash(ciphertext)

        print(f"\n{'─'*70}")
        print(f"  Passphrase        : {repr(passphrase)}")
        print(f"  Built-in hash val : {simple_hash(passphrase)}")
        print(f"  Derived  A        : {A}")
        print(f"  Derived  B        : {B}")
        print()
        print(f"  Plaintext         : {repr(plaintext)}")
        print(f"  Poly-hash(plain)  : {h_plain}")
        print()
        print(f"  Ciphertext        : {repr(ciphertext)}")
        print(f"  Poly-hash(cipher) : {h_cipher}")
        print()
        print(f"  Decrypted         : {repr(recovered)}")
        print(f"  Round-trip OK?    : {green('YES') if recovered == plaintext else red('NO')}")


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ok = run_tests()
    print_worked_examples()
    raise SystemExit(0 if ok else 1)
