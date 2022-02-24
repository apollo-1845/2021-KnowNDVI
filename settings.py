#!/usr/bin/env python3
import os

# Main - timing
IS_PROD = True
EXPERIMENT_DURATION_MINUTES = 3 * 60
SECONDS_PER_ITERATION = 1

# Processing
# Resolution from phase 2 guide
PREFERRED_RESOLUTION = (1296, 972)
PREFERRED_RES_NP = (972, 1296)  # Reverse - for creating NumPy arrays

MASK = True
CAN_DISCARD = True
# Discard, PNG - 904K used
# Discard, no PNG  - 1.1M used
# No discard, PNG - 3.7M used
# No discard, no PNG - 2.6M used
#
# Larger data set:
# Discard, no PNG - 26M
# Discard, PNG - 23M
#
# With 480x640:
    # 10 pictures take up around 2.2M
    # We are allowed to use 3G = 2600M (conservatively)
    # Roughly 12000 pictures are allowed
    # 3 hours = 10800 seconds, therefore 1 picture per second should work well
# Now:
# 1 picture per 5 seconds
USE_PNG = True

# Output
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve() # Get parent directory

OUT_DIR = BASE_DIR/"out"
OUT_FILE = OUT_DIR/"out.blob"