#!/usr/bin/env bash
# Rebuild everything from data/raw. Run from the repository root.
set -euo pipefail
cd "$(dirname "$0")/src"
python3 -I prep.py     > ../results/prep_log.txt
python3 -I cross.py    > ../results/cross_log.txt
python3 -I prep2.py    > ../results/prep2_log.txt
python3 -I refit5.py   > ../results/refit5_log.txt
python3 -I proj5.py    > ../results/proj5_log.txt
python3 -I figs.py     > ../results/figs_log.txt
python3 -I verify.py   > ../results/verify_log.txt
python3 -I econ.py     > ../results/econ_log.txt
echo "Done. Key numbers are in results/results.json; figures in figures/."
