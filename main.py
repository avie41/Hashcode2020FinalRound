#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Module d'entrée pour la mise en oeuvre du projet Poly#.
"""

from polyhash.polyhmodel import main_model


if __name__ == "__main__":
    main_model('input/d_tight_schedule.txt', drawing=True, gif=False)
