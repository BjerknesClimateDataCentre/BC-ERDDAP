#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# parameters.py

# ----------------------------------------------
# import from standard lib
import logging
from urllib.parse import urlparse
import yaml
# import from other lib
# import from my project
import bcedd.setupcfg as setupcfg

# --- module's variable ------------------------
# load logger
_logger = logging.getLogger(__name__)

# ----------------------------------------------
def _is_url(url_):
    """
    check if argument is an url

    :param url_: string of url to check

    :return: boolean
    """
    try:
        result = urlparse(url_)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _get_list(list_=None):
    """ get list from yaml file element
    """
    if not isinstance(list_, list):
        if list_ is None:
            _ = []
        else:
            _ = [list_]
    else:
        _ = list_

    return _


def _chk_param_keep(list_):
    """ """
    return _get_list(list_)


def _chk_param_server(dict_):
    """ """
    _ = {}
    for k, v, in dict_.items():
        if not _is_url(v['url']):
            raise TypeError(f"invalid type for 'url'")

        v['type'] = _get_list(v['type'])

        if any(tt not in setupcfg.authorised_eddtype for tt in v['type']):
            raise ValueError(f"'type' value must be choose in {setupcfg.authorised_eddtype}")

        ff = v['freq']
        if ff not in setupcfg.authorised_frequency:
            raise ValueError(f"'freq' value must be choose in {setupcfg.authorised_frequency}")

        # check datasetID to keep parameters
        v['keep'] = _get_list(v['keep'])

        _[k] = v

    return _


def _check_param(dict_):
    """
    check dictionary elements and reformat if need be

    :return: dictionary reformat
    """
    _ = {}
    # check remote ERDDAP server parameters
    if 'server' in dict_:
        _['server'] = _chk_param_server(dict_['server'])
    else:
        _logger.exception(f"No remote erddap server to look for."
                          f"Check {setupcfg.extraParam}.")
        raise

    return _


def main():
    """
    """
    try:
        # read parameters configuration file yaml
        with open(setupcfg.extraParam, 'r') as stream:
            try:
                param = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # check parameters file
        return _check_param(param)

    except Exception:
        _logger.exception(f"Something goes wrong when loading extra parameters file -{setupcfg.extraParam}-.")
        raise  # Throw exception again so calling code knows it happened


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Something goes wrong!!!')
        raise  # Throw exception again so calling code knows it happened

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
