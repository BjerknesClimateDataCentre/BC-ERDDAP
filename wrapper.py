#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# wrapper.py

# ----------------------------------------------
# import from standard lib
import time
# import from other lib
# import from my project
import bcedd
from bcedd.__main__ import main

if __name__ == '__main__':
    """ """
    print('package: {}'.format(bcedd.__package__))
    print('version: {}'.format(bcedd.__version__))

    # run bcedd
    main()
