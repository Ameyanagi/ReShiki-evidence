#!/bin/sh
# E2 evidence: usage: cli_check.sh <reshiki binary> <folder with ethanol.{png,svg,pdf}>
bin=$1; pictures=$2; work=$(mktemp -d)
export RESHIKI_DATA_DIR=$(mktemp -d)
# Prints the command as typed, its output (first lines) and its exit code.
run() {
  echo "\$ reshiki --cli $1"; shift
  out=$("$bin" --cli "$@" 2>&1); code=$?
  echo "$out" | cut -c1-200 | head -3; echo "(exit $code)"; echo
}
"$bin" --version; echo
for ext in png svg pdf; do
  "$bin" --cli convert --smiles CCO -o "$work/plain.$ext" 2>/dev/null
  echo "# ethanol.$ext: exported by the app with the editable drawing. plain.$ext: written by this CLI, no drawing inside."
  run "convert ethanol.$ext --to smiles" convert "$pictures/ethanol.$ext" --to smiles
  run "convert plain.$ext --to smiles" convert "$work/plain.$ext" --to smiles
done
run "analyze ethanol.png" analyze "$pictures/ethanol.png"
run "name ethanol.pdf" name "$pictures/ethanol.pdf"
echo "\$ reshiki --cli convert - --from mol --to smiles < ethanol.svg"
"$bin" --cli convert - --from mol --to smiles < "$pictures/ethanol.svg" 2>&1 | cut -c1-200; echo "(exit $?)"
