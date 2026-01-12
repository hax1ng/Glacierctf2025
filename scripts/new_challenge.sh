#!/bin/bash
# Creates a new challenge folder with template files
# Usage: ./scripts/new_challenge.sh <category> <challenge_name>
#
# Example: ./scripts/new_challenge.sh crypto rsa_challenge

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validate arguments
if [ $# -lt 2 ]; then
    echo -e "${YELLOW}Usage:${NC} $0 <category> <challenge_name>"
    echo ""
    echo "Categories: crypto, forensics, misc, osint, pwn, rev, web"
    echo ""
    echo "Example:"
    echo "  $0 crypto rsa_baby"
    echo "  $0 web sql_injection"
    exit 1
fi

CATEGORY="$1"
CHALLENGE_NAME="$2"

# Normalize challenge name (lowercase, underscores)
CHALLENGE_NAME=$(echo "$CHALLENGE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' -' '_')

# Valid categories
VALID_CATEGORIES=("crypto" "forensics" "misc" "osint" "pwn" "rev" "web" "hardware" "mobile" "blockchain")

# Validate category
if [[ ! " ${VALID_CATEGORIES[*]} " =~ " ${CATEGORY} " ]]; then
    echo -e "${RED}Error:${NC} Invalid category '${CATEGORY}'"
    echo "Valid categories: ${VALID_CATEGORIES[*]}"
    exit 1
fi

# Create directory
CHALLENGE_DIR="$REPO_ROOT/$CATEGORY/$CHALLENGE_NAME"

if [ -d "$CHALLENGE_DIR" ]; then
    echo -e "${RED}Error:${NC} Challenge directory already exists: $CHALLENGE_DIR"
    exit 1
fi

mkdir -p "$CHALLENGE_DIR"
echo -e "${GREEN}Created:${NC} $CHALLENGE_DIR"

# Create display name (title case)
DISPLAY_NAME=$(echo "$CHALLENGE_NAME" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')

# Create README.md (challenge info)
cat > "$CHALLENGE_DIR/README.md" << EOF
# ${DISPLAY_NAME}

**Category:** ${CATEGORY^}
**Points:** ???
**Solves:** ???

## Description

_Challenge description goes here._

## Connection Info

_Connection info or file downloads._

## Files

- \`file.zip\`

## Flag Format

\`uoftctf{...}\`
EOF

echo -e "${GREEN}Created:${NC} README.md"

# Create write-up template
cat > "$CHALLENGE_DIR/${CHALLENGE_NAME}_writeup.md" << EOF
# ${DISPLAY_NAME} Write-up

**Category:** ${CATEGORY^}
**Points:** ???
**Flag:** \`uoftctf{flag_here}\`

## Overview

_Brief description of the challenge._

## Analysis

_Your analysis and approach._

## Solution

_Step-by-step solution._

\`\`\`python
# solve.py
\`\`\`

## Flag

\`\`\`
uoftctf{flag_here}
\`\`\`

## Takeaways

- _Key learning from this challenge_
EOF

echo -e "${GREEN}Created:${NC} ${CHALLENGE_NAME}_writeup.md"

# Create empty solve script based on category
case "$CATEGORY" in
    "pwn")
        cat > "$CHALLENGE_DIR/solve.py" << 'EOF'
#!/usr/bin/env python3
from pwn import *

# context.log_level = 'debug'
context.arch = 'amd64'

HOST = 'localhost'
PORT = 1337

def main():
    # r = process('./challenge')
    r = remote(HOST, PORT)

    # Exploit here

    r.interactive()

if __name__ == '__main__':
    main()
EOF
        ;;
    "crypto")
        cat > "$CHALLENGE_DIR/solve.py" << 'EOF'
#!/usr/bin/env python3
from Crypto.Util.number import *

def main():
    # Solution here
    pass

if __name__ == '__main__':
    main()
EOF
        ;;
    "web")
        cat > "$CHALLENGE_DIR/solve.py" << 'EOF'
#!/usr/bin/env python3
import requests

URL = 'http://localhost:8080'

def main():
    s = requests.Session()
    # Solution here

if __name__ == '__main__':
    main()
EOF
        ;;
    *)
        cat > "$CHALLENGE_DIR/solve.py" << 'EOF'
#!/usr/bin/env python3

def main():
    # Solution here
    pass

if __name__ == '__main__':
    main()
EOF
        ;;
esac

chmod +x "$CHALLENGE_DIR/solve.py"
echo -e "${GREEN}Created:${NC} solve.py"

echo ""
echo -e "${GREEN}Challenge created successfully!${NC}"
echo -e "Directory: ${YELLOW}$CHALLENGE_DIR${NC}"
echo ""
echo "Next steps:"
echo "  1. Add challenge files to the directory"
echo "  2. Update README.md with challenge info"
echo "  3. Write your solution in solve.py"
echo "  4. Document in ${CHALLENGE_NAME}_writeup.md"
echo "  5. Run: python scripts/generate_readme.py"
