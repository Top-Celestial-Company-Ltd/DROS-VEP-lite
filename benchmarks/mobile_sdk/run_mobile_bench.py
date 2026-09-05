# -*- coding: utf-8 -*-
"""
DROS-Mobile-SDK: Master Benchmark Runner
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tests.test_mobile_attacks import run_mobile_sdk_benchmark

if __name__ == "__main__":
    run_mobile_sdk_benchmark()
