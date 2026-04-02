#  Affine Cipher — Passphrase Mode

> A from-scratch Python implementation of the classic Affine Cipher, extended with passphrase-based key derivation, full special-character support, a custom Polynomial Rolling Hash, and an automated test suite.  


---

## Table of Contents

1. [What is the Affine Cipher?](#1-what-is-the-affine-cipher)
2. [How Keys are Derived from a Passphrase](#2-how-keys-are-derived-from-a-passphrase)
3. [Special Character Handling](#3-special-character-handling)
4. [The Hash Function](#4-the-hash-function)
5. [File Structure & Function Reference](#5-file-structure--function-reference)
6. [How to Run](#6-how-to-run)
7. [Worked Examples](#7-worked-examples)
8. [Test Script](#8-test-script)

---

## 1. What is the Affine Cipher?

The **Affine Cipher** is a classical monoalphabetic substitution cipher. Every letter in the plaintext is mapped to a number, transformed by a linear (affine) function, and mapped back to a letter.

### Encryption

```
f(x) = (A × x + B) mod 26
```

### Decryption

```
f⁻¹(y) = A_inv × (y − B) mod 26
```

| Symbol | Meaning |
|---|---|
| `x` | Numeric index of the plaintext letter (A=0, B=1, … Z=25) |
| `A`, `B` | Secret keys |
| `A_inv` | Modular inverse of A mod 26, satisfying `A × A_inv ≡ 1 (mod 26)` |

### Why must A be coprime with 26?

If `gcd(A, 26) ≠ 1`, two different letters could encrypt to the same character — making decryption ambiguous or impossible. Only the following **12 values** satisfy `gcd(A, 26) = 1`:

```
{ 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25 }
```

The modular inverse `A_inv` is computed using the **Extended Euclidean Algorithm** (implemented from scratch in `affine_cipher.py`).

---

## 2. How Keys are Derived from a Passphrase

Instead of asking the user to manually enter numbers for A and B, a passphrase is hashed into a single integer, and A and B are extracted from it automatically.

### Internal hash formula

```
hash = Σ  ord(ch[i]) × (i + 1)     for i = 0, 1, …, n-1
```

### Example — passphrase `"hello"`

```
'h'  →  104 × 1  =   104
'e'  →  101 × 2  =   202
'l'  →  108 × 3  =   324
'l'  →  108 × 4  =   432
'o'  →  111 × 5  =   555
                  ───────
hash             =  1617
```

### Why multiply by position?

Without position weighting, anagrams like `"abc"` and `"cab"` would hash to the same value. Multiplying by position makes the **order of characters matter**, so different passphrases reliably produce different hash values.

### Extracting A and B

```
A  =  VALID_A[ hash % 12 ]    →  picks one of the 12 coprime values
B  =  hash % 26               →  shift value in range 0–25
```

---

## 3. Special Character Handling

Standard affine ciphers only operate on letters. This implementation extends encryption to **all 69 printable non-letter ASCII characters** — digits, punctuation, spaces, and symbols (character codes 32–126, excluding A–Z and a–z).

The same affine formula is applied over the special-character index space:

```
Encrypt:  index_out = (A × index_in + B) mod 69
Decrypt:  index_in  = A_inv × (index_out − B) mod 69
```

This design guarantees:
- Encrypted special characters **never turn into letters** (clean separation of domains)
- The mapping is **bijective** — one-to-one and fully reversible
- Every character in a message is transformed, including spaces and digits

---

## 4. The Hash Function

**File:** `hash_function.py`

### Choice: Polynomial Rolling Hash

A **Polynomial Rolling Hash** was chosen as the standalone hashing function — a well-established technique used in algorithms like Rabin-Karp string matching.

### Formula

```
H = Σ  ord(ch[i]) × BASE^i   (mod MOD)
    i = 0 to n−1
```

**Parameters:**

| Parameter | Value | Reason |
|---|---|---|
| `BASE` | `131` | Prime just above 128 — covers all printable ASCII values |
| `MOD` | `2^61 − 1` | Mersenne prime — maximally large, collision-resistant output space |

### Why a Mersenne prime for MOD?

`2^61 − 1` is prime, so the output space is maximally spread with no clustering. Mersenne primes also allow efficient modular arithmetic using bitwise operations on supporting platforms.

### Properties

| Property | Detail |
|---|---|
| **Deterministic** | Same input always produces the same output |
| **Position-sensitive** | `"ab"` and `"ba"` hash to different values |
| **Avalanche effect** | A single character change propagates through the hash |
| **Collision-resistant** | Large MOD makes practical collisions extremely rare |
| **O(n) time, O(1) space** | Linear scan, no extra memory |
| **No external libraries** | Pure Python arithmetic only |

### Difference from the key-derivation hash

| | Key-derivation hash (inside `affine_cipher.py`) | Polynomial Rolling Hash (`hash_function.py`) |
|---|---|---|
| Purpose | Derive cipher keys A and B from passphrase | General-purpose standalone hash |
| Formula | `Σ ord(ch) × position` | `Σ ord(ch) × BASE^i mod MOD` |
| Output range | Unbounded integer | `[0, 2^61 − 2]` |
| Collision resistance | Basic | Strong (Mersenne prime modulus) |

---

## 5. File Structure & Function Reference

```
.
├── affine_cipher.py    — Cipher core: encrypt, decrypt, key derivation, interactive menu
├── hash_function.py    — Standalone Polynomial Rolling Hash (from scratch)
├── test_cipher.py      — Automated test suite: encrypt → hash → decrypt round-trip
└── README.md
```

### `affine_cipher.py`

| Function | Description |
|---|---|
| `simple_hash(passphrase)` | Position-weighted ASCII sum for key derivation |
| `derive_keys(passphrase)` | Extracts A and B from the hash |
| `mod_inverse(a, m)` | Extended Euclidean Algorithm — finds A_inv |
| `build_special_maps(A, B)` | Builds encrypt/decrypt maps for the 69-char special set |
| `encrypt(text, A, B)` | Encrypts letters and special characters |
| `decrypt(text, A, B)` | Decrypts letters and special characters |
| `show_hash_working(passphrase)` | Prints hash calculation step by step |
| `show_key_derivation(passphrase)` | Prints A and B derivation working |
| `show_encryption_steps(text, A, B)` | Prints character-by-character encryption table |
| `show_decryption_steps(text, A, B)` | Prints character-by-character decryption table |
| `main()` | Interactive menu loop |

### `hash_function.py`

| Function | Description |
|---|---|
| `poly_hash(text)` | Polynomial rolling hash — returns integer in `[0, MOD−1]` |
| `show_hash_working(text)` | Prints step-by-step hash computation |

---

## 6. How to Run

**Requirements:** Python 3.10 or later. No third-party packages required.

### Interactive cipher menu

```bash
python affine_cipher.py
```

You will be prompted for a passphrase. Keys A and B are derived automatically. The menu then offers:

```
[1]  Encrypt a message
[2]  Decrypt a message
[3]  Show hash & key derivation details
[4]  Change passphrase
[5]  Exit
```

### Standalone hash demo

```bash
python hash_function.py
```

Runs several built-in examples and opens an interactive prompt for custom input.

### Automated test suite

```bash
python test_cipher.py
```

Runs 8 round-trip tests and prints full worked examples.

---

## 7. Worked Examples

### Example 1 — `"hello world"` with passphrase `"secret"`

**Key derivation:**

```
hash_val  =  2271
A  =  VALID_A[2271 % 12]  =  VALID_A[3]  =  7
B  =  2271 % 26           =  9
A_inv (mod 26)            =  15    (since 7 × 15 = 105 ≡ 1 mod 26)
```

**Letter encryption trace (A=7, B=9):**

| Char | Index x | Formula | y | Cipher |
|---|---|---|---|---|
| `h` | 7 | (7×7 + 9) mod 26 = 58 mod 26 | 6 | `g` |
| `e` | 4 | (7×4 + 9) mod 26 = 37 mod 26 | 11 | `l` |
| `l` | 11 | (7×11 + 9) mod 26 = 86 mod 26 | 8 | `i` |
| `l` | 11 | (7×11 + 9) mod 26 = 86 mod 26 | 8 | `i` |
| `o` | 14 | (7×14 + 9) mod 26 = 107 mod 26 | 3 | `d` |
| ` ` | 0 (special) | (7×0 + 9) mod 69 | 9 | `)` |
| `w` | 22 | (7×22 + 9) mod 26 = 163 mod 26 | 7 | `h` |
| `o` | 14 | (7×14 + 9) mod 26 = 107 mod 26 | 3 | `d` |
| `r` | 17 | (7×17 + 9) mod 26 = 128 mod 26 | 24 | `y` |
| `l` | 11 | (7×11 + 9) mod 26 = 86 mod 26 | 8 | `i` |
| `d` | 3 | (7×3 + 9) mod 26 = 30 mod 26 | 4 | `e` |

**Summary:**

| Field | Value |
|---|---|
| Passphrase | `secret` |
| Keys | A = 7, B = 9 |
| Plaintext | `hello world` |
| Ciphertext | `gliid)hdyie` |
| Poly-hash (plaintext) | `1236015006693062432` |
| Poly-hash (ciphertext) | `1140881231862911878` |
| Decrypted | `hello world` ✓ |

---

### Example 2 — `"Hello, World! How are you?"` with passphrase `"MyP@ssw0rd"`

**Key derivation:**

```
hash_val  =  5323
A  =  VALID_A[5323 % 12]  =  VALID_A[7]  =  17
B  =  5323 % 26           =  19
A_inv (mod 26)            =  23    (since 17 × 23 = 391 ≡ 1 mod 26)
```

**Summary:**

| Field | Value |
|---|---|
| Passphrase | `MyP@ssw0rd` |
| Keys | A = 17, B = 19 |
| Plaintext | `Hello, World! How are you?` |
| Ciphertext | `Ijyyx(3Dxwys^3Ixd3twj3lxv>` |
| Poly-hash (plaintext) | `16442377872537461` |
| Poly-hash (ciphertext) | `2282787758494366286` |
| Decrypted | `Hello, World! How are you?` ✓ |

---

## 8. Test Script

`test_cipher.py` runs **8 automated round-trip tests** — each verifying that `decrypt(encrypt(plaintext)) == plaintext` and printing the poly-hash of the ciphertext.

| # | Description | Passphrase | Result |
|---|---|---|---|
| 1 | Basic lowercase sentence | `secret` | ✓ PASS |
| 2 | Mixed case with punctuation | `MyP@ssw0rd` | ✓ PASS |
| 3 | Numbers and special characters | `alpha123` | ✓ PASS |
| 4 | All uppercase — pangram | `CIPHER` | ✓ PASS |
| 5 | Passphrase equals plaintext | `test` | ✓ PASS |
| 6 | Long paragraph (228 chars) | `longpassphrase!` | ✓ PASS |
| 7 | Digits only | `numkey` | ✓ PASS |
| 8 | Symbols only | `symkey` | ✓ PASS |

Run with:

```bash
python test_cipher.py
```

Expected output:
```
Results: 8 passed, 0 failed  (out of 8 tests)
```

---
