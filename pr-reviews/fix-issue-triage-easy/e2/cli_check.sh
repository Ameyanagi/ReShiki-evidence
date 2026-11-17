#!/bin/sh
# E2 evidence: usage: cli_check.sh <reshiki binary> <folder with ethanol.{png,svg,pdf}>
bin=$1; pictures=$2; work=$(mktemp -d)
export RESHIKI_DATA_DIR=$(mktemp -d)
"$bin" --version
for ext in png svg pdf; do
  echo "\$ reshiki --cli convert ethanol.$ext --to smiles   # exported by the app with the editable drawing"
  "$bin" --cli convert "$pictures/ethanol.$ext" --to smiles 2>&1; echo "exit $?"
  "$bin" --cli convert --smiles CCO -o "$work/plain.$ext" 2>&1
  echo "\$ reshiki --cli convert plain.$ext --to smiles   # written by this CLI, no drawing inside"
  "$bin" --cli convert "$work/plain.$ext" --to smiles 2>&1; echo "exit $?"
done
echo "\$ reshiki --cli analyze ethanol.png"
"$bin" --cli analyze "$pictures/ethanol.png" 2>&1 | head -4; echo "exit $?"
echo "\$ reshiki --cli name ethanol.pdf"
"$bin" --cli name "$pictures/ethanol.pdf" 2>&1; echo "exit $?"
echo "\$ reshiki --cli convert - --from mol --to smiles < ethanol.svg"
"$bin" --cli convert - --from mol --to smiles < "$pictures/ethanol.svg" 2>&1; echo "exit $?"
