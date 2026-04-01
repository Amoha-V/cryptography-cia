import math

# ──────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────

ALPHABET_SIZE = 26

# Only these 12 values are valid for A (must be coprime with 26)
VALID_A = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

# All printable ASCII characters that are NOT letters (space through ~, minus A-Z and a-z)
# These 69 characters form the special character pool
SPECIAL_CHARS = [c for c in range(32, 127) if not ((65 <= c <= 90) or (97 <= c <= 122))]
SPECIAL_SIZE  = len(SPECIAL_CHARS)   # 69


# ──────────────────────────────────────────────
#  SIMPLE HASH FUNCTION
#  Formula: sum of (ASCII value of char x its position)
#  Example: "hi" -> (104x1) + (105x2) = 314
# ──────────────────────────────────────────────

def simple_hash(passphrase: str) -> int:
    total = 0
    for i, ch in enumerate(passphrase):
        total += ord(ch) * (i + 1)   # position starts at 1
    return total


# ──────────────────────────────────────────────
#  KEY DERIVATION
#  Derive A and B from passphrase using the hash
# ──────────────────────────────────────────────

def derive_keys(passphrase: str) -> tuple[int, int]:
    hash_val = simple_hash(passphrase)
    A = VALID_A[hash_val % len(VALID_A)]   # % 12 -> index into VALID_A list
    B = hash_val % ALPHABET_SIZE           # % 26 -> shift value 0-25
    return A, B


# ──────────────────────────────────────────────
#  SPECIAL CHARACTER MAP
#
#  We apply the affine formula over the 69-character
#  special set (all printable ASCII that are not letters).
#  This guarantees:
#    1. Encrypted specials NEVER look like letters
#    2. The mapping is bijective (one-to-one and reversible)
#
#  Formula: index_out = (A * index_in + B) mod 69
# ──────────────────────────────────────────────

def build_special_maps(A: int, B: int) -> tuple[dict, dict]:
    """
    Returns (enc_map, dec_map) where:
      enc_map[plain_char]  -> cipher_char
      dec_map[cipher_char] -> plain_char
    Both maps cover only non-letter printable ASCII.
    """
    enc_map: dict[str, str] = {}
    dec_map: dict[str, str] = {}
    for i, code in enumerate(SPECIAL_CHARS):
        j          = (A * i + B) % SPECIAL_SIZE
        plain_ch   = chr(code)
        cipher_ch  = chr(SPECIAL_CHARS[j])
        enc_map[plain_ch]  = cipher_ch
        dec_map[cipher_ch] = plain_ch
    return enc_map, dec_map


# ──────────────────────────────────────────────
#  MODULAR INVERSE  (used for decryption)
#  Finds A_inv such that (A x A_inv) % 26 == 1
# ──────────────────────────────────────────────

def mod_inverse(a: int, m: int = ALPHABET_SIZE) -> int:
    old_r, r = a % m, m
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_s % m


# ──────────────────────────────────────────────
#  ENCRYPT
#  Letters  -> f(x) = (A*x + B) mod 26
#  Specials -> affine over 69-char special set
# ──────────────────────────────────────────────

def encrypt(plaintext: str, A: int, B: int) -> str:
    enc_map, _ = build_special_maps(A, B)
    result = []
    for ch in plaintext:
        if ch.isupper():
            x = ord(ch) - ord('A')
            y = (A * x + B) % ALPHABET_SIZE
            result.append(chr(y + ord('A')))

        elif ch.islower():
            x = ord(ch) - ord('a')
            y = (A * x + B) % ALPHABET_SIZE
            result.append(chr(y + ord('a')))

        elif ch in enc_map:
            result.append(enc_map[ch])

        else:
            result.append(ch)   # non-printable: pass through

    return ''.join(result)


# ──────────────────────────────────────────────
#  DECRYPT
#  Letters  -> x = A_inv * (y - B) mod 26
#  Specials -> reverse affine over 69-char special set
# ──────────────────────────────────────────────

def decrypt(ciphertext: str, A: int, B: int) -> str:
    A_inv = mod_inverse(A)
    _, dec_map = build_special_maps(A, B)
    result = []
    for ch in ciphertext:
        if ch.isupper():
            y = ord(ch) - ord('A')
            x = (A_inv * (y - B)) % ALPHABET_SIZE
            result.append(chr(x + ord('A')))

        elif ch.islower():
            y = ord(ch) - ord('a')
            x = (A_inv * (y - B)) % ALPHABET_SIZE
            result.append(chr(x + ord('a')))

        elif ch in dec_map:
            result.append(dec_map[ch])

        else:
            result.append(ch)

    return ''.join(result)


# ──────────────────────────────────────────────
#  DISPLAY HELPERS
# ──────────────────────────────────────────────

def show_hash_working(passphrase: str) -> None:
    print("\n  Hash calculation:")
    total = 0
    for i, ch in enumerate(passphrase):
        contrib = ord(ch) * (i + 1)
        total += contrib
        print(f"    '{ch}'  ->  ASCII {ord(ch):>3}  x  position {i+1}  =  {contrib}")
    print(f"    {'─'*40}")
    print(f"    Hash  =  {total}")


def show_key_derivation(passphrase: str) -> None:
    hash_val = simple_hash(passphrase)
    A, B     = derive_keys(passphrase)
    idx      = hash_val % len(VALID_A)
    print(f"\n  Key derivation:")
    print(f"    A  =  VALID_A[{hash_val} % 12]  =  VALID_A[{idx}]  =  {A}")
    print(f"    B  =  {hash_val} % 26  =  {B}")
    print(f"    A_inv mod 26  =  {mod_inverse(A)}")
    print(f"    Letter formula : f(x) = ({A}x + {B}) mod 26")
    print(f"    Special formula: f(i) = ({A}i + {B}) mod {SPECIAL_SIZE}  (over {SPECIAL_SIZE}-char set)")


def show_encryption_steps(plaintext: str, A: int, B: int) -> None:
    enc_map, _ = build_special_maps(A, B)
    print(f"\n  {'Char':<8} {'Type':<10} {'Index':<8} {'Formula':<36} {'Result'}")
    print(f"  {'─'*72}")
    for ch in plaintext:
        if ch.isupper():
            x = ord(ch) - ord('A')
            y = (A * x + B) % ALPHABET_SIZE
            formula = f"({A}x{x}+{B}) mod 26 = {y}"
            print(f"  {ch:<8} {'upper':<10} {x:<8} {formula:<36} {chr(y + ord('A'))}")

        elif ch.islower():
            x = ord(ch) - ord('a')
            y = (A * x + B) % ALPHABET_SIZE
            formula = f"({A}x{x}+{B}) mod 26 = {y}"
            print(f"  {ch:<8} {'lower':<10} {x:<8} {formula:<36} {chr(y + ord('a'))}")

        elif ch in enc_map:
            i = SPECIAL_CHARS.index(ord(ch))
            j = (A * i + B) % SPECIAL_SIZE
            formula = f"({A}x{i}+{B}) mod {SPECIAL_SIZE} = {j}"
            print(f"  {repr(ch):<8} {'special':<10} {i:<8} {formula:<36} {repr(enc_map[ch])}")

        else:
            print(f"  {repr(ch):<8} {'other':<10} {ord(ch):<8} {'pass through':<36} {repr(ch)}")


def show_decryption_steps(ciphertext: str, A: int, B: int) -> None:
    A_inv      = mod_inverse(A)
    _, dec_map = build_special_maps(A, B)
    print(f"\n  {'Char':<8} {'Type':<10} {'Index':<8} {'Formula':<36} {'Result'}")
    print(f"  {'─'*72}")
    for ch in ciphertext:
        if ch.isupper():
            y = ord(ch) - ord('A')
            x = (A_inv * (y - B)) % ALPHABET_SIZE
            formula = f"{A_inv}x({y}-{B}) mod 26 = {x}"
            print(f"  {ch:<8} {'upper':<10} {y:<8} {formula:<36} {chr(x + ord('A'))}")

        elif ch.islower():
            y = ord(ch) - ord('a')
            x = (A_inv * (y - B)) % ALPHABET_SIZE
            formula = f"{A_inv}x({y}-{B}) mod 26 = {x}"
            print(f"  {ch:<8} {'lower':<10} {y:<8} {formula:<36} {chr(x + ord('a'))}")

        elif ch in dec_map:
            j = SPECIAL_CHARS.index(ord(ch))
            formula = f"reverse affine, index {j} -> {repr(dec_map[ch])}"
            print(f"  {repr(ch):<8} {'special':<10} {j:<8} {formula:<36} {repr(dec_map[ch])}")

        else:
            print(f"  {repr(ch):<8} {'other':<10} {ord(ch):<8} {'pass through':<36} {repr(ch)}")


# ──────────────────────────────────────────────
#  MENU
# ──────────────────────────────────────────────

def print_banner():
    print("\n" + "=" * 50)
    print("        AFFINE CIPHER  —  passphrase mode")
    print("=" * 50)


def print_menu():
    print("\n  [1]  Encrypt a message")
    print("  [2]  Decrypt a message")
    print("  [3]  Show hash & key derivation details")
    print("  [4]  Change passphrase")
    print("  [5]  Exit")
    print()


def get_passphrase() -> str:
    while True:
        p = input("  Enter passphrase: ").strip()
        if p:
            return p
        print("  Passphrase cannot be empty.")


def main():
    print_banner()

    print("\n  The passphrase is hashed to automatically derive keys A and B.")
    passphrase = get_passphrase()
    A, B = derive_keys(passphrase)
    print(f"\n  Keys derived  ->  A = {A},  B = {B}")

    while True:
        print_menu()
        choice = input("  Choose an option (1-5): ").strip()

        # ── Encrypt ──────────────────────────────
        if choice == '1':
            text = input("\n  Enter plaintext: ")
            if not text:
                print("  Nothing to encrypt.")
                continue
            ciphertext = encrypt(text, A, B)
            print(f"\n  Plaintext  : {text}")
            print(f"  Ciphertext : {ciphertext}")

            show_steps = input("\n  Show step-by-step working? (y/n): ").strip().lower()
            if show_steps == 'y':
                show_encryption_steps(text, A, B)

        # ── Decrypt ──────────────────────────────
        elif choice == '2':
            text = input("\n  Enter ciphertext: ")
            if not text:
                print("  Nothing to decrypt.")
                continue
            plaintext = decrypt(text, A, B)
            print(f"\n  Ciphertext : {text}")
            print(f"  Plaintext  : {plaintext}")

            show_steps = input("\n  Show step-by-step working? (y/n): ").strip().lower()
            if show_steps == 'y':
                show_decryption_steps(text, A, B)

        # ── Hash details ─────────────────────────
        elif choice == '3':
            print(f"\n  Passphrase : \"{passphrase}\"")
            show_hash_working(passphrase)
            show_key_derivation(passphrase)

        # ── Change passphrase ─────────────────────
        elif choice == '4':
            passphrase = get_passphrase()
            A, B = derive_keys(passphrase)
            print(f"\n  New keys derived  ->  A = {A},  B = {B}")

        # ── Exit ──────────────────────────────────
        elif choice == '5':
            print("\n  Goodbye!\n")
            break

        else:
            print("  Invalid choice. Enter a number from 1 to 5.")


if __name__ == "__main__":
    main()