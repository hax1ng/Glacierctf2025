# awesomeNESs - GlacierCTF 2025 Writeup

**Category:** Reverse Engineering
**Points:** 500
**Flag:** `gctf{0op5_wr0ng_jmp_t0_i1l3g4l_0pc0d35_s0rry}`

## The Challenge

We're given an NES ROM file called `awesome.nes`. When you load it up in an emulator, you see a retro-style game that asks you to "Enter the flag" - a 39-character password starting with `gctf{`.

The game lets you cycle through characters at each position using the D-pad and hit START to check if your flag is correct. Classic crackme style, but on a Nintendo!

## First Steps - What Are We Looking At?

The ROM is in iNES format - the standard format for NES games. It has:
- 32KB of program code (PRG ROM)
- 8KB of graphics data (CHR ROM)

The graphics data contains all the character tiles - letters, numbers, and symbols that can be displayed. By decoding these tiles, I figured out the character set:
- Lowercase letters a-z
- Uppercase letters A-Z
- Digits 1-9, 0
- Underscore and braces

## Reverse Engineering the Validation

Here's where things get interesting. I disassembled the 6502 assembly code (the NES uses a 6502 CPU) and found the flag validation routine.

For each of the 39 character positions, the game does this:

1. **Takes your input character** (stored as a value 0x00-0x4B)
2. **Transforms it** using one of three operations (ADD, SUB, or XOR with a constant)
3. **Uses the result to pick one of 12 "routines"** (numbered 0-11)
4. **Applies that routine** to some test data
5. **Compares the output** against expected values

If all 39 positions match their expected values, you win!

### The Key Insight

Instead of brute-forcing characters, I worked **backwards**. For each position:

1. I knew what the expected output needed to be
2. I tried each of the 12 possible routines
3. For each routine, I calculated what input character would select it
4. I checked if that character actually produces the correct output

Here's a concrete example for **Position 0**:

```
ROM Data:
  Operation: SUB
  Operand: 0x39
  Expected output: 0x88, 0x68

Working backwards:
  If routine 4 (XOR with table value) is used...
  Input = (4 + 0x39) mod 256 = 0x3D
  Character 0x3D = '0' (the digit zero)

Verification:
  0xF3 XOR 0x7B = 0x88 ✓
  0x13 XOR 0x7B = 0x68 ✓

Position 0 = '0'
```

## The Plot Twist - Broken Positions!

Running this analysis on all 39 positions, I found something weird:

- **36 positions** had valid solutions
- **3 positions (11, 24, 38)** had NO valid solution!

For example, position 24 uses ADD with operand 0x1F. To get any routine 0-11, you'd need:
```
input + 0x1F = 0 through 11
input = -31 through -20 (mod 256) = 0xE1 through 0xEC
```

But valid characters only go up to 0x4B! There's literally no character you can enter that will validate.

## Reading the Message

Despite these "impossible" positions, the 36 working positions spelled out a clear message:

```
Position:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19...
Character: 0  o  p  5  _  w  r  0  n  g  _  ?  m  p  _  t  0  _  i  1 ...
```

Filling in the blanks with context:
- Position 11: `?mp` → probably "jmp" (assembly jump instruction)
- Position 24: `i1l3g4?` → "illegal" (needs an 'l')
- Position 38: `s0rr?` → "sorry" (needs a 'y')

The full message in leetspeak:
```
0op5_wr0ng_jmp_t0_i1l3g4l_0pc0d35_s0rry
```

Which reads as: **"oops wrong jmp to illegal opcodes sorry"**

## The Meta Joke

This is absolutely brilliant challenge design. The flag itself is an apology message explaining that the validation code has bugs ("wrong jmp to illegal opcodes"). The challenge author intentionally broke 3 positions in the validation routine, making it literally impossible to enter the correct flag in the game!

The challenge description even hints at this:
> "I can't make it past level 1"

You CAN'T beat the game - that's the point! The flag is extracted through reverse engineering, not through playing.

## Final Flag

```
gctf{0op5_wr0ng_jmp_t0_i1l3g4l_0pc0d35_s0rry}
```

Leetspeak translation:
- `0` = o
- `5` = s
- `1` = l (in "i1l3g4l" = "illegal")
- `3` = e (in "0pc0d35" = "opcodes")
- `4` = a

**"oops wrong jmp to illegal opcodes sorry"**

## Tools Used

- Python for analysis scripts
- NES emulator (FCEUX/Mesen) for testing
- Custom 6502 disassembler
- Lots of hex dumps and caffeine

## Lessons Learned

1. Always look for the **intended message** in reverse engineering challenges
2. When math says "impossible," that might BE the answer
3. Challenge authors love meta-jokes
4. 6502 assembly is still fun after all these years

---

*This was a really clever challenge that rewarded careful analysis over brute force. The self-referential "sorry the code is broken" message hidden in an unbeatable game is peak CTF humor.*
