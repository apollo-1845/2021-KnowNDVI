#!/usr/bin/env python3
import os

# Main - timing
IS_PROD = False
RUN_MINUTES = 0.5
SECONDS_PER_ITERATION = 1

# Processing
PREFERRED_RESOLUTION = (640, 480)
PREFERRED_RES_NP = (480, 640) # Reverse - for creating NumPy arrays

MASK = True
CAN_DISCARD = True
USE_PNG = True

# Output
OUT_DIR = os.path.join(".", "out")
OUT_FILE = os.path.join(OUT_DIR, "out.blob")