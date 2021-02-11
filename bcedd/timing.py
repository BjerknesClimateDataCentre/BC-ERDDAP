#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timing.py
# source: http://stackoverflow.com/a/1557906/6009280

# ----------------------------------------------
# import from standard lib
import atexit
from time import time, strftime, localtime
from datetime import timedelta
# import from other lib
# import from my project


def _secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))


def log(s, elapsed=None):
    line = "-"*40
    print(line)
    print(f"{_secondsToStr()} - {s}")
    if elapsed:
        print(f"Elapsed time: {elapsed}")
    print(line)


def endlog():
    end = time()
    elapsed = end-start
    log("End Program", _secondsToStr(elapsed))


# ----------------------------------------------
start = time()
atexit.register(endlog)
log(f"Start Program")
