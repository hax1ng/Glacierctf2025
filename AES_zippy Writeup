
# AES_zippy - GlacierCTF 2025 Writeup

**Category:** Crypto
**Difficulty:** Hard
**Flag:** `gctf{ZiPPY_iS_0UT_heRE_5NItchin6_on_@lL_tHE_nONC3s}`

## The Challenge

We're given a server that acts like a secure message storage system. It uses AES-GCM encryption (the gold standard for authenticated encryption) and lets us:

1. **Encrypt messages** - We provide plaintext and a nonce, it returns ciphertext + authentication tag
2. **Decrypt and verify** - We provide ciphertext, nonce, and tag, it checks if everything is valid

The twist? There's an "admin" message already encrypted on the server:
- Plaintext: `"Hello GlacierCTF"`
- The nonce and tag are stored in `ADMIN_LOGS`

To get the flag, we need to forge a valid decryption request for a *different* message: `"Glacier CTF Open"`.

Sounds impossible, right? AES-GCM is supposed to prevent exactly this kind of forgery. But there are two fatal flaws in this implementation...

## The Two Vulnerabilities

### Vulnerability #1: The Compression Oracle (CRIME Attack)

The server has a "storage" feature that shows how much space the logs take up:

```python
def get_size():
    return len(zlib.compress(ADMIN_LOGS + NORMAL_LOGS)) + len(USED_NONCES) * 16
```

See that `zlib.compress`? That's the killer. Compression works by finding repeated patterns - if your input has repetition, it gets smaller.

The `ADMIN_LOGS` contains something like:
```
[+] Nonce: VgVA9+kvQh96...==
[+] Tag: cghmqGIg...==
```

And `NORMAL_LOGS` contains our encrypted messages. So if we encrypt a message that starts with `[+] Nonce: V`, the compressed size will be *smaller* than if we encrypt `[+] Nonce: X` (assuming the real nonce starts with V).

This is the **CRIME attack** - we can leak secret data one character at a time by watching how compression changes!

**The leak process:**
1. Try encrypting `"[+] Nonce: A"`, `"[+] Nonce: B"`, ... `"[+] Nonce: /"` (all 64 base64 characters)
2. Whichever gives the smallest storage = that's the first character of the nonce
3. Repeat for each position until we have the full nonce
4. Do the same for the tag

After ~2800 queries, we know both the admin's nonce and tag!

### Vulnerability #2: Nonce Reuse (The Classic GCM Sin)

Here's the thing about AES-GCM: **you must NEVER reuse a nonce with the same key**. The server doesn't stop us from doing exactly that.

When you encrypt with GCM:
- The ciphertext is just `plaintext XOR keystream`
- The keystream depends only on the key and nonce
- If you reuse a nonce, you get the **same keystream**!

So if we know:
- Admin encrypted `"Hello GlacierCTF"` with nonce N → got ciphertext C1
- We encrypt `"Hello GlacierCTG"` (one byte different) with same nonce N → get ciphertext C2

Then: `C1 XOR C2 = "Hello GlacierCTF" XOR "Hello GlacierCTG"` = just the plaintext difference!

This lets us:
1. Recover the keystream
2. Compute what the admin's ciphertext was
3. Recover the secret authentication key H (more math below)
4. Forge a valid tag for any message we want

## The Math (Simplified)

GCM tags are computed using a polynomial hash called GHASH:

```
Tag = GHASH(H, associated_data, ciphertext) XOR E(K, nonce||counter0)
```

Where H is a secret "authentication key" derived from the main key.

When we reuse a nonce and change only the ciphertext slightly:
- The `E(K, nonce||counter0)` part stays the same
- Only the GHASH part changes

If we call the ciphertext difference `D` and the tag difference `deltaT`:
```
deltaT = D * H^2  (in the weird GF(2^128) math field)
```

So: `H^2 = deltaT / D`

And we can take the square root to get H!

Once we have H, we can compute a valid tag for any ciphertext we want.

## The Gotcha That Took 100+ Attempts

Here's where I banged my head against the wall for hours. The compression oracle was working perfectly - I was getting consistent results with clear winners. But the forgery kept failing with "tags don't match".

**The bug:** In GCM's mathematical field (GF(2^128) with the bit-reflected representation), the multiplicative identity is NOT `1`. It's `2^127`!

```python
# WRONG - what I had
def gf_pow(x, e):
    r = 1  # <- BUG! This isn't the identity element!
    while e > 0:
        if e & 1: r = gf_mul(r, x)
        x = gf_mul(x, x)
        e >>= 1
    return r

# CORRECT
IDENTITY = 1 << 127  # = 0x80000000000000000000000000000000

def gf_pow(x, e):
    r = IDENTITY  # <- Now it works!
    ...
```

In normal math, `x * 1 = x`. But in GCM's field, `x * (2^127) = x`. This is because of how the polynomial multiplication is defined with bit reflection.

This bug meant my inverse calculation was wrong, so H recovery failed, so tag forgery failed. Once I fixed this one line, everything worked!

## The Full Attack Flow

```
1. Connect to server

2. Leak the admin nonce (22 base64 chars):
   - For each position 0-21:
     - Try all 64 base64 chars
     - Pick the one with smallest compressed size
   Result: "VgVA9+kvQh96..." (example)

3. Leak the admin tag (22 base64 chars):
   - Same process
   Result: "cghmqGIgIJSf..." (example)

4. Reuse the nonce:
   - Encrypt "Hello GlacierCTG" with the leaked nonce
   - Get ciphertext C2 and tag T2

5. Recover H:
   - Compute ciphertext difference D = C_admin XOR C2
   - Compute tag difference deltaT = T_admin XOR T2
   - H^2 = deltaT * inverse(D)
   - H = sqrt(H^2) = (H^2)^(2^127)

6. Forge the winning message:
   - Target plaintext: "Glacier CTF Open"
   - Compute target ciphertext: plaintext XOR keystream
   - Compute valid tag using GHASH with recovered H

7. Submit forgery → Get flag!
```

## Key Takeaways

1. **Never mix compression with secrets** - The CRIME/BREACH attacks are real and devastating. If user-controlled data gets compressed alongside secrets, those secrets can leak.

2. **Never reuse nonces in GCM** - This is crypto 101, but it still happens. One nonce reuse = complete authentication bypass.

3. **Galois field math is tricky** - The identity element depends on your polynomial representation. Always double-check when implementing GF arithmetic!

4. **CTF debugging is hard** - When your attack "should" work but doesn't, systematically verify each component. In this case, the oracle was fine; the math library was broken.

## Files

- `solve_fixed.py` - The working exploit with the correct GF(2^128) implementation
- `aes-zippy/challenge` - Server source code

Thanks GlacierCTF for a great challenge that combined two classic crypto vulnerabilities in a clever way!
