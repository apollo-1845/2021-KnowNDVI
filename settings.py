#!/usr/bin/env python3
import os

# Main - timing
IS_PROD = True
EXPERIMENT_DURATION_MINUTES = 3 * 60
SECONDS_PER_ITERATION = 60

# Processing
PREFERRED_RESOLUTION = (640, 480)
PREFERRED_RES_NP = (480, 640)  # Reverse - for creating NumPy arrays

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
# 10 pictures take up 2.2M
# We are allowed to use 3G = 2600M (conservatively)
# Roughly 12000 pictures are allowed
# 3 hours = 10800 minutes, therefore 1 picture per minute should work well
USE_PNG = True

# Output
OUT_DIR = os.path.join(".", "out")
OUT_FILE = os.path.join(OUT_DIR, "out.blob")
