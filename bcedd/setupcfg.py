#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setupcfg.py

# ----------------------------------------------
# import from standard lib
from pathlib import Path
import logging
import logging.config
import yaml
import pkgutil
import sys
import os
import warnings
import argparse
import datetime as dt
from time import strftime, localtime
# import from other lib
import confuse  # Initialize config with your app
from dateutil.parser import parse
# import from my project
import bcedd

# --- module's variable ------------------------
# public
global erddapPath, erddapWebInfDir, erddapContentDir, datasetXmlPath, datasetCsvPath, logPath, bceddPath, \
    log_filename, yaml, freq
# private
global _update_log


def _chk_update_freq(cfg_):
    """ """
    global freq

    try:
        freq = cfg_['update']['freq'].get(str)
    except confuse.exceptions.NotFoundError:
        pass
    except Exception:
        logging.exception(f'Invalid yaml filename; '
                          f'Check arguments/configuration file(s)')
        raise  # Throw exception again so calling code knows it happened


def _chk_update_yaml(cfg_):
    """ """
    global yaml

    try:
        yaml = cfg_['update']['yaml'].get(str)
    except confuse.exceptions.NotFoundError:
        pass
    except Exception:
        logging.exception(f'Invalid yaml filename; '
                          f'Check arguments/configuration file(s)')
        raise  # Throw exception again so calling code knows it happened


def _chk_update(cfg_=None):
    """

    """

    if cfg_ is None:
        cfg_ = confuse.Configuration('bcedd', modname=bcedd.__pkg_cfg__)  # Get a value from your YAML file
        _ = Path(cfg_._package_path)
        cfg_.default_config_path = _ / confuse.DEFAULT_FILENAME

    try:
        _chk_update_yaml(cfg_)
        _chk_update_freq(cfg_)
    except Exception:
        logging.exception('Something goes wrong when checking update')
        raise  # Throw exception again so calling code knows it happened


def _chk_path_log(cfg_):
    """ check path to log files, and set up global variable

    path where log files will be stored
    """
    global logPath

    logPath = Path(cfg_['paths']['log'].get(str))
    if not logPath.is_dir():
        logPath.mkdir(parents=True, exist_ok=True)
        warnings.warn('log path {} did not exist before.\n Check config file(s) {} and/or {}'.
                      format(logPath, cfg_.user_config_path(), cfg_.default_config_path))

    logging.debug(f'logPath: {logPath}')


def _chk_path_xml(cfg_):
    """ check path to xml files, and set up global variable

    path where xml files will be stored
    """
    global datasetXmlPath

    datasetXmlPath = Path(cfg_['paths']['dataset']['xml'].as_filename())
    if not datasetXmlPath.is_dir():
        raise FileNotFoundError('can not find path where store dataset xml file {}.\n'
                                'Check config file(s) {} and/or {}'.format(datasetXmlPath,
                                                                           cfg_.user_config_path(),
                                                                           cfg_.default_config_path))
    logging.debug(f'datasetXmlPath: {datasetXmlPath}')


def _chk_path_edd(cfg_):
    """ check path to ERDDAP, and set up global variables

    path where ERDDAP has been previously installed
    """
    global erddapPath, erddapWebInfDir, erddapContentDir

    erddapPath = Path(cfg_['paths']['erddap'].get(str))
    if not erddapPath.is_dir():
        raise FileNotFoundError('can not find ERDDAP path {}.\n'
                                'Check config file(s) {} and/or {}'.format(erddapPath,
                                                                           cfg_.user_config_path(),
                                                                           cfg_.default_config_path))
    logging.debug(f'erddapPath: {erddapPath}')

    erddapWebInfDir = erddapPath / 'webapps' / 'erddap' / 'WEB-INF'
    if not erddapWebInfDir.is_dir():
        raise FileNotFoundError('can not find ERDDAP sub-directory {} \n'
                                'check ERDDAP installation. '.format(erddapWebInfDir))
    logging.debug(f'erddapWebInfDir: {erddapWebInfDir}')

    erddapContentDir = erddapPath / 'content' / 'erddap'
    if not erddapContentDir.is_dir():
        raise FileNotFoundError('can not find ERDDAP sub-directory {} \n'
                                'check ERDDAP installation'.format(erddapContentDir))
    logging.debug(f'erddapContentDir: {erddapContentDir}')


def _chk_path(cfg_=None):
    """

    """
    if cfg_ is None:
        cfg_ = confuse.Configuration('bcedd', modname=bcedd.__pkg_cfg__)  # Get a value from your YAML file
        _ = Path(cfg_._package_path)
        cfg_.default_config_path = _ / confuse.DEFAULT_FILENAME

    try:
        _chk_path_edd(cfg_)
        _chk_path_xml(cfg_)
        _chk_path_log(cfg_)
    except Exception:
        logging.exception('Something goes wrong when checking paths')
        raise  # Throw exception again so calling code knows it happened


def _find_package_path(name):
    # function from https://github.com/beetbox/confuse/blob/master/confuse/util.py
    """Returns the path to the package containing the named module or
    None if the path could not be identified (e.g., if
    ``name == "__main__"``).
    """
    # Based on get_root_path from Flask by Armin Ronacher.
    loader = pkgutil.get_loader(name)
    if loader is None or name == '__main__':
        return None

    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(name)
    else:
        # Fall back to importing the specified module.
        __import__(name)
        filepath = sys.modules[name].__file__

    return os.path.dirname(os.path.abspath(filepath))


def _setup_logger(config_):
    """set up logger

    set up logging parameters from command line arguments
    otherwise from configuration file(s)
    otherwise from logging configuration file: /path/to/package/cfg/logging.yaml

    > Level and When it’s used
    > ------------------------
    > DEBUG:
    > Detailed information, typically of interest only when diagnosing problems.
    >
    > INFO:
    > Confirmation that things are working as expected.
    >
    > WARNING:
    > An indication that something unexpected happened, or indicative of some problem in the near
    > future (e.g. ‘disk space low’). The software is still working as expected.
    >
    > ERROR:
    > Due to a more serious problem, the software has not been able to perform some function.
    >
    > CRITICAL:
    > A serious error, indicating that the program itself may be unable to continue running.
    """
    global log_filename

    cfg_path = Path(_find_package_path(bcedd.__pkg_cfg__))
    if not cfg_path.is_dir():
        logging.exception('Can not find configuration path')
        raise FileNotFoundError

    _logcfg = cfg_path / 'logging.yaml'
    try:
        with open(_logcfg, 'rt') as file:
            cfg_log = yaml.safe_load(file.read())

            try:
                # overwrite default with config or parser value
                _log_level = config_['log']['level'].get(str)
                if _log_level is not None:
                    cfg_log['handlers']['console']['level'] = _log_level.upper()
            except confuse.exceptions.NotFoundError:
                pass
            except Exception:
                logging.exception(f'Invalid log level; '
                                  f'Check arguments/configuration file(s)')
                raise  # Throw exception again so calling code knows it happened

            try:
                # if verbose activated, print output on console
                _log_verbose = config_['log']['verbose'].get(bool)
                if _log_verbose is not None:
                    if not _log_verbose:
                        # disable log on console
                        cfg_log['handlers'].pop('console')
                        cfg_log['root']['handlers'].remove('console')
            except confuse.exceptions.NotFoundError:
                pass
            except Exception:
                logging.exception(f'Invalid log verbose; '
                                  f'Check arguments/configuration file(s)')
                raise  # Throw exception again so calling code knows it happened

            try:
                # rename log file with config or parser value
                _log_filename = config_['log']['filename'].get(str)
                if _log_filename is not None:
                    cfg_log['handlers']['file']['filename'] = _log_filename
            except confuse.exceptions.NotFoundError:
                pass
            except Exception:
                logging.exception(f'Invalid log filename; '
                                  f'Check arguments/configuration file(s)')
                raise  # Throw exception again so calling code knows it happened

            _paths_log = config_['paths']['log'].get()
            if _paths_log is not None:
                log_path = Path(str(_paths_log))
            else:
                # read path to output log file
                log_path = Path(cfg_log['handlers']['file']['filename']).parent

            if not log_path.is_dir():
                log_path.mkdir(parents=True, exist_ok=True)
                logging.warning(f'log path {log_path} did not exist before.\n Check config file(s) '
                                f'{config_.user_config_path()} and/or {config_.default_config_path}.')

            filename = cfg_log['handlers']['file']['filename']
            cfg_log['handlers']['file']['filename'] = str(log_path / filename)

            logging.config.dictConfig(cfg_log)
            # redirect warnings issued by the warnings module to the logging system.
            logging.captureWarnings(True)

            # keep log filename and path name
            log_filename = Path(cfg_log['handlers']['file']['filename']).resolve()

    except Exception:
        logging.exception('Error loading configuration file. Using default configs')
        raise  # Throw exception again so calling code knows it happened

    # add header to log file
    logging.info(f'-------------------')
    logging.info(f'package: {bcedd.__name__}')
    logging.info(f'version: {bcedd.__version__}')
    logging.info(f'start time: {strftime("%Y-%m-%d %H:%M:%S", localtime())}')
    logging.info(f'-------------------')


def _parse(logfile_):
    """set up parameter from command line arguments

    :param logfile_: log filename, useless except to change the default log filename when using checkOntology
    """
    # define parser
    parser = argparse.ArgumentParser(
        prog="bcedd",
        description="blabla"
    )

    # positional arguments
    # parser.add_argument("name", type=str, help="file name")
    # optional arguments
    parser.add_argument("-v", "--verbose",
                        action="store_const",
                        const=True,
                        help="print status messages to stdout",
                        dest='log.verbose'
                        )
    parser.add_argument("--log_level",
                        type=str,
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help="stdout logger level",
                        dest='log.level'
                        )
    parser.add_argument("--log_filename",
                        type=str,
                        help="logger filename",
                        dest='log.filename'
                        )
    parser.add_argument("--log_path",
                        type=str,
                        help="logger path, where log will be stored",
                        dest='paths.log'
                        )
    parser.add_argument("-f", "--freq",
                        type=str,
                        choices=['weekly', 'monthly'],
                        help="updating frequency to be applied",
                        dest='update.freq'
                        )
    parser.add_argument("-y", "--yaml",
                        type=str,
                        help="yaml file with datasets to work with",
                        dest='update.yaml'
                        )

    # parse arguments
    args = parser.parse_args()

    if vars(args)['log.filename'] is None:
        vars(args)['log.filename'] = logfile_

    # TODO check and reformat args
    return args


def _setup_cfg():
    """set up from configuration file(s)

    read parameters from
    ~/.config/bcedd/config.yaml
    otherwise from
    /path/to/package/cfg/config_default.yaml
    """
    # set up configuration file
    try:
        # Read configuration file
        config_ = confuse.LazyConfig('bcedd', modname=bcedd.__pkg_cfg__)  # Get a value from your YAML file

        # TODO check use of templates,
        #  cf examples in https://github.com/beetbox/confuse/tree/c244db70c6c2e92b001ce02951cf60e1c8793f75

        # set up default configuration file path
        pkg_path = Path(config_._package_path)
        config_.default_config_path = pkg_path / confuse.DEFAULT_FILENAME

        return config_

    except Exception:
        logging.exception("Something goes wrong when loading config file.")
        raise  # Throw exception again so calling code knows it happened


def _setup_path():
    """ set up some useful path
    """
    global bceddPath, _update_log

    bceddPath = Path(_find_package_path(__package__))
    if not bceddPath.is_dir():
        logging.exception('Can not find package path')
        raise FileNotFoundError

    update_log_path = bceddPath / '.log'
    if not update_log_path.is_dir():
        update_log_path.mkdir(parents=True, exist_ok=True)
        logging.warning(f'update log path -{update_log_path}- did not exist before.')

    _update_log = update_log_path / 'update.log'


def _default_logger():
    """creates default logger, before any setting up

    this default logger should only be used in case of any exception raised during setting up
    """
    logging.basicConfig(
        level=logging.INFO,
        style='{',
        format="{asctime} | {levelname:8} | {name} | {message}"
    )
    # redirect warnings issued by the warnings module to the logging system.
    logging.captureWarnings(True)


def main(logfile_=None):
    """set up bcedd

    set up config file(s)
    set up logger

    :param logfile_: log filename, useless except to change the default log filename when using checkOntology
    """

    # init default
    _default_logger()

    # setup package path
    _setup_path()

    # read configuration file(s)
    config = _setup_cfg()

    # read command line arguments
    args = _parse(logfile_)

    # overwrite configuration file parameter with parser arguments
    config.set_args(args, dots=True)

    # read logging configuration file
    _setup_logger(config)

    # check paths parameters from configuration file(s)
    _chk_path(config)

    # check update parameters from configuration file(s)
    _chk_update(config)

    # TODO check log parameters from configuration file(s)
    # _chk_log(config)


if __name__ == '__main__':
    main()

    _logger = logging.getLogger(__name__)
    _logger.debug('This message should go to the log file')
    _logger.info('So should this')
    _logger.warning('And this, too')
    _logger.error('\tAnd non-ASCII stuff, too, like Øresund and Malmö\n')
    _logger.critical('this is critical')
    # _logger.exception('raise en exception')
