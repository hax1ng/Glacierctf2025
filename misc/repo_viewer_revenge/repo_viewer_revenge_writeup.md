 Repo Viewer Revenge - GlacierCTF 2025 Writeup

  The Challenge

  So we're given a service that lets you upload a compressed archive (.tar.gz file) and it'll display the contents of a README.md file from inside that archive. Simple enough, right?

  The catch? There's a flag file sitting at /flag.txt on the server, and we need to read it. The obvious attack would be to create a symlink - basically a shortcut file that says "hey, when you
   read README.md, actually read /flag.txt instead."

  But the challenge authors aren't stupid. They added a check.

  The Defense

  Before extracting your archive, the server runs this check:

  tar -tvzf - | grep '^[lh]' | wc -l

  Translation: "List all files in this archive, and if ANY of them start with 'l' (symlink) or 'h' (hardlink), reject it."

  When you list a tar archive, symlinks show up like this:
  lrwxrwxrwx user/group  0 2025-01-01 README.md -> /flag.txt

  See that l at the very start? That's what the filter catches. Seems foolproof!

  The Twist

  Here's where it gets interesting. The check uses GNU tar (the standard Linux tool), but the extraction uses a Rust library called tokio-tar. The challenge description even hints at this:

  "My trusty coreutils have failed me! Maybe rust can save the day?"

  Different tools parsing the same file format... what could go wrong? 😈

  The Vulnerability: TARmageddon

  After a LOT of failed attempts (trust me, I tried everything), I stumbled upon CVE-2025-62518, nicknamed "TARmageddon." It's a parsing desynchronization bug.

  Here's the deal with tar files: they can have two types of headers for the same file:
  1. PAX extended header - the fancy modern way with extra metadata
  2. ustar header - the classic way

  Both headers can specify the file's size. But what happens if they disagree?

  The Mismatch Exploit

  I crafted a tar file like this:

  1. PAX header says: "The next file (other.txt) is 1536 bytes"
  2. ustar header says: "The next file (other.txt) is 0 bytes"
  3. The "data": 1536 bytes that are actually a complete tar entry for a symlink!

  [PAX Header: size=1536] [ustar Header: size=0] [Symlink Header hiding as "data"]

  How Each Tool Sees It

  GNU tar (the checker):
  - Reads PAX header: "Oh, other.txt is 1536 bytes"
  - Reads the ustar header
  - Reads 1536 bytes as the file content of other.txt
  - Never realizes those bytes are actually another tar entry
  - Output: -rw-r--r-- other.txt (just a regular file!)
  - ✅ Check passes - no symlinks detected!

  tokio-tar (the extractor):
  - Has different parsing logic
  - Sees the hidden symlink as a separate entry
  - Extracts both other.txt AND the symlink README.md → /flag.txt
  - ✅ Symlink gets created!

  The Payload

  # The symlink we want to smuggle
  symlink_header = make_tar_header('README.md', 0, '2', '/flag.txt')  # type '2' = symlink
  symlink_data = symlink_header + b'\x00' * 1024  # 1536 bytes total

  # PAX header claiming the file is 1536 bytes
  pax_content = b'13 size=1536\n'

  # Build the tar:
  # 1. PAX extended header
  # 2. ustar header with size=0 (the mismatch!)
  # 3. The "data" which is secretly our symlink
  tar_data = pax_header + ustar_header_size_zero + symlink_data

  The Result

  === SERVER RESPONSE ===
  Found entry: other.txt
  Found entry: README.md      <-- Our smuggled symlink!
  Extracted README.md

  --- README.md contents ---
  gctf{Ru5t_m4k3s_3v3Ry7h1ng_5eCuR3_71a9f2ed8}

  The Flag

  gctf{Ru5t_m4k3s_3v3Ry7h1ng_5eCuR3_71a9f2ed8}

  The flag itself is the punchline: "Rust makes everything secure" - except when your parsing logic differs from everyone else's!

  Lessons Learned

  1. Don't mix parsers - If you check with one tool and process with another, you're asking for trouble
  2. Format specifications are complex - Tar files have decades of extensions and edge cases
  3. "Memory safe" ≠ "bug free" - Rust prevents memory corruption, not logic bugs
  4. CVE databases are your friend - Sometimes the exploit already exists, you just need to find it

  The Journey

  Honestly, this one took me through a wild ride:
  - ❌ Tried different tar entry types (sparse, FIFO, devices)
  - ❌ Tried multi-member gzip files
  - ❌ Tried GNU long name/link extensions
  - ❌ Tried corrupted checksums
  - ❌ Tried PAX attributes on regular files
  - ✅ Finally found TARmageddon!

  The key insight was realizing that GNU tar and tokio-tar could see different entries in the same file. Once I understood that, it was just a matter of crafting the right payload.

  Great challenge! 🏔️🚩
