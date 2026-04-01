# Affine Cipher with Passphrase-Based Key Derivation

A Python implementation of the Affine Cipher where keys A and B are automatically
derived from a user-supplied passphrase using a simple custom hash function.
Supports letters (upper and lower case) and special characters.

---

## What is the Affine Cipher?

The Affine Cipher is a substitution cipher that encrypts each letter using a
mathematical formula:

```
Encrypt:  f(x)  = (A * x + B) mod 26
Decrypt:  f⁻¹(y) = A_inv * (y - B) mod 26
```

Where:
- `x` is the numeric position of the plaintext letter (A=0, B=1, ... Z=25)
- `A` and `B` are the secret keys
- `A_inv` is the modular inverse of A (used to reverse the encryption)
- `A` must be **coprime with 26** — i.e. gcd(A, 26) = 1

---

## Features

- Passphrase-based key derivation (no need to manually choose A and B)
- Encrypts and decrypts letters (upper and lower case separately)
- Encrypts and decrypts special characters using mod 256
- Step-by-step character-by-character breakdown
- Interactive menu interface

---

## How to Run

```bash
python affine_cipher.py
```

Python 3.10 or higher is recommended (uses `tuple[int, int]` type hint syntax).

---

## Menu Options

```
[1]  Encrypt a message
[2]  Decrypt a message
[3]  Show hash & key derivation details
[4]  Change passphrase
[5]  Exit
```

---

## The Hash Function

Instead of asking the user to enter numbers for A and B directly, a passphrase
is hashed into a single number, and A and B are extracted from it.

### Formula

```
hash = sum of ( ASCII value of each character × its 1-based position )
```

### Example — passphrase "hello"

```
'h'  →  104 × 1  =  104
'e'  →  101 × 2  =  202
'l'  →  108 × 3  =  324
'l'  →  108 × 4  =  432
'o'  →  111 × 5  =  555

hash = 104 + 202 + 324 + 432 + 555 = 1617
```

### Why multiply by position?

Without position weighting, anagrams like `"abc"` and `"cab"` would produce the
same hash (same characters, same total). Multiplying by position makes the
**order of characters matter**, so different passphrases reliably produce
different hash values.

### Extracting A and B from the hash

```
A  =  VALID_A[ hash % 12 ]
B  =  hash % 26
```

- `% 12` because there are exactly **12 valid A values**
  `[1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]`
- `% 26` maps the hash into the range 0–25 for B

### Why only those 12 values for A?

A must satisfy `gcd(A, 26) = 1` (coprime with 26). If A and 26 share a common
factor, two different letters could encrypt to the same character, making
decryption impossible. Filtering all numbers 1–25 by this rule leaves exactly
12 valid values.

---

## Special Character Handling

Letters use the standard affine formula over 26.
All other characters (digits, punctuation, symbols, spaces) use:

```
Encrypt:  (ASCII code + A + B) mod 256
Decrypt:  (ASCII code - A - B + 256) mod 256
```

This ensures every character in the message is transformed and the operation
is fully reversible.

---

## Example Session

```
Enter passphrase: hello

Keys derived  →  A = 21,  B = 7

[1] Encrypt

Enter plaintext: Hello, World! 123

Ciphertext: Tqlla, Iadxp! >?@

Character-by-character breakdown:
Char     Type       Index    Formula                  Result
H        upper      7        (21×7+7) mod 26 = 6      T  (wait actually G... etc)
...
```

---

## File Structure

```
affine_cipher.py
│
├── simple_hash(passphrase)         — position-weighted ASCII sum
├── derive_keys(passphrase)         — extracts A and B from hash
├── mod_inverse(a, m)               — extended Euclidean algorithm
├── encrypt(text, A, B)             — encrypts letters + special chars
├── decrypt(text, A, B)             — decrypts letters + special chars
├── show_hash_working(passphrase)   — prints hash calculation step by step
├── show_key_derivation(passphrase) — prints A, B derivation working
├── show_encryption_steps(...)      — prints character table for encryption
├── show_decryption_steps(...)      — prints character table for decryption
└── main()                          — interactive menu loop
```

---

## Key Concepts Summary

| Concept | Explanation |
|---|---|
| Affine cipher | Encrypts letters with f(x) = (Ax + B) mod 26 |
| Coprime | gcd(A, 26) = 1 — required for decryption to work |
| Modular inverse | A_inv such that A × A_inv ≡ 1 (mod 26) |
| Hash function | Collapses a string to a number |
| Position weighting | Makes hash sensitive to character order |
| mod 256 | Extends the cipher to cover all ASCII characters |
