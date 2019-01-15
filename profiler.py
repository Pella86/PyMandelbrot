# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 21:02:42 2019

@author: Mauro
"""

import cProfile
import pstats
import os
import main

test_name = "test_lut_optimization"
run_prof = False

test_folder = "./profiler/" + test_name + os.sep
if not os.path.isdir(test_folder):
    os.mkdir(test_folder)


if __name__ == "__main__":
    if run_prof:
        cProfile.runctx("main.main()", globals(), locals(), test_folder + "stats")
    else:
        with open( test_folder + "beauty_stats.txt", "w") as f:
            p = pstats.Stats(test_folder + 'stats', stream=f)
            p.strip_dirs().sort_stats("cumulative").print_stats()