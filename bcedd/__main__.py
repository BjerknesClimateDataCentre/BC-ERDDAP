#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __main__.py

# ----------------------------------------------
# import from standard lib
import logging
from urllib.parse import urlparse
import yaml
from time import strftime, localtime
# import from other lib
# import from my project
import bcedd.setupcfg as setupcfg
import bcedd.parameters as parameters
import bcedd.xml4Erddap as x4edd
import bcedd.timing


def main():
    """
    """
    # set up logger, paths, ...
    setupcfg.main()
    _logger = logging.getLogger(__name__)

    # check parameters file
    param = parameters.main()

    # select task to be done
    bindings = []
    for k, v in param['server'].items():
        # select frequency
        if v['freq'] == setupcfg.freq:
            # unpack type list
            for tt in v['type']:
                bindings += [(k,v['url'],tt)]

    for b in bindings:
        # run Generate
        x4edd.generate(*b)

    # aggregate
    dsxmlout = x4edd.concatenate()
    # check datasetid (select some, and remove duplicate)
    x4edd.check_datasetid(dsxmlout)
    # create hard link
    x4edd.replaceXmlBy(dsxmlout)

    # add footer to log file
    _logger.info(f'-------------------')
    _logger.info(f'end time: {strftime("%Y-%m-%d %H:%M:%S", localtime())}')
    _logger.info(f'-------------------')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Something goes wrong!!!')
        raise  # Throw exception again so calling code knows it happened

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
