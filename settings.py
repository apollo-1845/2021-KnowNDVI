#!/usr/bin/env python3
import os

# Main - timing
IS_PROD = True
EXPERIMENT_DURATION_MINUTES = 0.5
SECONDS_PER_ITERATION = 1

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
USE_PNG = True

# Output
OUT_DIR = os.path.join(".", "out")
OUT_FILE = os.path.join(OUT_DIR, "out.blob")
