#!/usr/bin/env bash
# Identify which file is responsible for a side-effect (e.g., file creation, env pollution)
#
# Example: ./find-polluter.sh 'pollution-file.txt' 'src/**/*.test.ts'
#
# Logic:
# 1. Take a target side-effect (file path or grep pattern)
# 2. Take a list of suspect files (glob)
# 3. For each suspect file:
#    a. Clean side-effect
#    b. Run the suspect file
#    c. Check if side-effect exists
#    d. If yes, that's the polluter

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <side-effect-file> <test-glob>"
  echo "Example: $0 'pollution-file.txt' 'src/**/*.test.ts'"
  exit 1
fi

TARGET="$1"
SUSPECTS="$2"

echo "Searching for polluter of $TARGET among $SUSPECTS..."

for f in $(ls $SUSPECTS); do
  # Cleanup
  rm -f "$TARGET"
  
  # Run suspect (adapt command as needed)
  # npx ts-node "$f" > /dev/null 2>&1
  npm test "$f" > /dev/null 2>&1
  
  # Check side-effect
  if [[ -f "$TARGET" ]]; then
    echo "FOUND POLLUTER: $f"
    exit 0
  fi
done

echo "Polluter not found."
exit 1
