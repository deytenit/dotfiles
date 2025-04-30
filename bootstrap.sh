#!/usr/bin/env bash

#
# Root-level bootstrapper
# Recursively finds & runs any bootstrap.sh scripts in subdirs.
#

set -euo pipefail
IFS=$'\n\t'

#----------------------------------------
# Configuration
#----------------------------------------

FIND_OPTS=( -type f -name 'bootstrap.sh' -not -path './bootstrap.sh' )

#----------------------------------------
# Helpers
#----------------------------------------

log() {
  echo -e "\e[1;34m[bootstrap]\e[0m $*"
}

#----------------------------------------
# Main
#----------------------------------------

log "Starting root bootstrap at $(pwd)"

# 1) Find all bootstrap.sh except this one (./bootstrap.sh)
# 2) Sort so order is stable
# 3) For each, cd into its dir and run it
while IFS= read -r script; do
  dir=$(dirname "$script")
  log "Bootstrapping in '$dir'"

  pushd "$dir" > /dev/null
    bash bootstrap.sh
  popd > /dev/null

done < <( find . "${FIND_OPTS[@]}" | sort )


dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
log "Bootstrapping in '$dir'"

pushd "$dir" > /dev/null
  bash bootstrap.root.sh
popd > /dev/null

log "All bootstrap jobs completed"
