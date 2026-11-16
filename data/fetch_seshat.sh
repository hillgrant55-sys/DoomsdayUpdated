#!/bin/sh
# Fetch Seshat Equinox-2020 into data/external/ (not committed). Pinned to the commit recorded in data/HOLDOUT_SESHAT.md.
set -e
D=$(dirname "$0")/external/seshat
mkdir -p "$D" && cd "$D"
[ -d Equinox_Data ] || git clone -q https://github.com/seshatdb/Equinox_Data.git
cd Equinox_Data && git checkout -q 602c7cdf0649e1fbbdb37f5b5a387edbe19915d0
echo "48c7fbd00b6ebca4405d171e1d8e4fb2ea74a2fcd3edd0762e699e7d472f0556  Equinox_on_GitHub_June9_2022.xlsx" | sha256sum -c -
