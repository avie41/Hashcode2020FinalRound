#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Tuple


def manhattan(a: Tuple[int, int], b: Tuple[int, int]):
    """
    Returns the manhattan distance between two points.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
