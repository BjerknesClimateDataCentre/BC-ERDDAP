#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# wrapper.py

# ----------------------------------------------
# import from standard lib
import time
# import from other lib
import schedule
# import from my project
import bcedd
from bcedd.__main__ import main

if __name__ == '__main__':
    """ """
    print('module: {}'.format(bcedd.__name__))
    print('package: {}'.format(bcedd.__package__))
    print('version: {}'.format(bcedd.__version__))

    # run icp2edd
    schedule.every().day.at("00:30:00").do(main)
    # check ontology ...
    # schedule.every().wednesday.at("01:30:00").do(check)

    while True:
        schedule.run_pending()
        time.sleep(1)

