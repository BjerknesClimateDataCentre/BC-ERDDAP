#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setupcfg.py

# ----------------------------------------------
# import from standard lib
from pathlib import Path
import logging
import logging.config
import atexit
import yaml
import pkgutil
import sys
import os
import warnings
import argparse
from time import strftime, localtime
# import from other lib
import confuse  # Initialize config with your app
import errorhandler
# import from my project
import bcedd

# --- module's variable ------------------------
# public
global erddapPath, erddapWebInfDir, erddapContentDir, \
       datasetXmlPath, datasetCsvPath, \
       bceddPath, logPath, log_filename, \
       authorised_frequency, authorised_eddtype, \
       extraParam

# private
global _cfg_path, _logcfg, _warning_handler, _error_handler, _fatal_handler


def _search_file(cfg_, filename_):
    """ search file in several directory

    look for file 'filename_' in:
    - local directory or given path
    - user    config directory
    - package directory
    - package config directory

    :param cfg_:
    :param filename_: name of the file search
    :return: absolute path to filename_
    """
    global _cfg_path

    # check file exist
    if Path(filename_).is_file():
        # local directory
        return Path(filename_).absolute()
    elif Path(Path(cfg_.config_dir()) / filename_).is_file():
        # user config directory
        # ~/.config/<package> directory
        return Path(Path(cfg_.config_dir()) / filename_)
    elif Path(bceddPath / filename_).is_file():
        # ~/path/to/package/ directory
        return Path(bceddPath / filename_)
    elif Path(_cfg_path / filename_).is_file():
        # package config directory
        # ~/path/to/package/cfg directory
        return Path(_cfg_path / filename_)
    else:
        logging.exception(f"can not find file -{filename_}-; "
                          f'Check arguments/configuration file(s)')
        raise FileNotFoundError


def _chk_config_extra(cfg_):
    """
    """
    global extraParam

    try:
        extraParam = cfg_['extra']['parameters'].get(str)
    except confuse.exceptions.NotFoundError:
        logging.exception(f'Can not find extra parameters; '
                          f'Check arguments/configuration file(s)')
        raise  # Throw exception again so calling code knows it happened
    except Exception:
        logging.exception(f'Invalid parameters yaml filename; '
                          f'Check arguments/configuration file(s)')
        raise  # Throw exception again so calling code knows it happened

    # check config file exist
    extraParam = _search_file(cfg_, extraParam)


def _chk_config_update(cfg_):
    """
    """
    global freq

    try:
        freq = cfg_['update']['freq'].get(str)
    except confuse.exceptions.NotFoundError:
        pass
    except Exception:
        logging.exception(f'Invalid frequency; '
                          f'Check arguments/configuration file(s)')
        raise  # Throw exception again so calling code knows it happened

    if freq not in authorised_frequency:
        logging.exception(f"update frequency must be choose in {authorised_frequency}")
        raise  # Throw exception again so calling code knows it happened


def _chk_config_log(cfg_):
    """
    """
    # TODO
    pass


def _chk_config_authorised(cfg_):
    """
    """
    global authorised_frequency, authorised_eddtype

    # Authorised eddtype
    try:
        authorised_eddtype = cfg_['authorised']['eddtype'].get(list)
    except confuse.exceptions.NotFoundError:
        authorised_eddtype = None
        # do not raise other exception as it will be by calling function

    # Authorised frequency
    try:
        authorised_frequency = cfg_['authorised']['frequency'].get(list)
    except confuse.exceptions.NotFoundError:
        authorised_frequency = None
        # do not raise other exception as it will be by calling function


def _chk_config_paths(cfg_):
    """
    """
    try:
        # check path to ERDDAP, and set up global variables
        # path where ERDDAP has been previously installed
        global erddapPath, erddapWebInfDir, erddapContentDir
        #
        erddapPath = Path(cfg_['paths']['erddap'].get(str))
        if not erddapPath.is_dir():
            raise FileNotFoundError('can not find ERDDAP path {}.\n'
                                    'Check config file(s) {} and/or {}'.format(erddapPath,
                                                                               cfg_.user_config_path(),
                                                                               cfg_.default_config_path))
        logging.debug(f'erddapPath: {erddapPath}')

        # erddapWebInfDir = erddapPath / 'webapps' / <ROOT> / 'WEB-INF'
        erddapWebInfDir = Path(cfg_['paths']['webinf'].get(str))
        if not erddapWebInfDir.is_dir():
            raise FileNotFoundError('can not find ERDDAP sub-directory {} \n'
                                    'check ERDDAP installation. '.format(erddapWebInfDir))
        logging.debug(f'erddapWebInfDir: {erddapWebInfDir}')

        erddapContentDir = erddapPath / 'content' / 'erddap'
        if not erddapContentDir.is_dir():
            raise FileNotFoundError('can not find ERDDAP sub-directory {} \n'
                                    'check ERDDAP installation'.format(erddapContentDir))
        logging.debug(f'erddapContentDir: {erddapContentDir}')

        # check path to xml files, and set up global variable
        # path where xml files will be stored
        global datasetXmlPath
        #
        datasetXmlPath = Path(cfg_['paths']['dataset']['xml'].as_filename())
        if not datasetXmlPath.is_dir():
            raise FileNotFoundError('can not find path where store dataset xml file {}.\n'
                                    'Check config file(s) {} and/or {}'.format(datasetXmlPath,
                                                                               cfg_.user_config_path(),
                                                                               cfg_.default_config_path))
        logging.debug(f'datasetXmlPath: {datasetXmlPath}')

        # check path to log files, and set up global variable
        # path where log files will be stored
        global logPath
        #
        logPath = Path(cfg_['paths']['log'].get(str))
        if not logPath.is_dir():
            logPath.mkdir(parents=True, exist_ok=True)
            warnings.warn('log path {} did not exist before.\n Check config file(s) {} and/or {}'.
                          format(logPath, cfg_.user_config_path(), cfg_.default_config_path))

        logging.debug(f'logPath: {logPath}')


    except Exception:
        logging.exception('Something goes wrong when checking paths')
        raise  # Throw exception again so calling code knows it happened


def _chk_config(cfg_):
    """
    :param cfg_: config from confuse _setup_config
    """
    try:
        # check paths parameters from configuration file(s)
        _chk_config_paths(cfg_)
        # check log parameters from configuration file(s)
        _chk_config_log(cfg_)
        # check authorised list from configuration file(s)
        _chk_config_authorised(cfg_)
        # check update list from configuration file(s)
        _chk_config_update(cfg_)
        # check update parameters from configuration file(s)
        _chk_config_extra(cfg_)
    except Exception:
        logging.exception('Something goes wrong when checking configuration file')
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


def _logger_header():
    """ """
    # add header to log file
    logging.info(f'-------------------')
    logging.info(f'package                  : {bcedd.__name__}')
    logging.info(f'version                  : {bcedd.__version__}')
    logging.info(f'start time               : {strftime("%Y-%m-%d %H:%M:%S", localtime())}')
    logging.info(f'-------------------')

def _logger_footer():
    """ """
    # add footer to log file
    logging.info(f'-------------------')
    logging.info(f"Warning     have occurred: {_warning_handler.fired}")
    logging.info(f"Error       have occurred: {_error_handler.fired}")
    logging.info(f"Fatal error have occurred: {_fatal_handler.fired}")
    logging.info(f'end time                 : {strftime("%Y-%m-%d %H:%M:%S", localtime())}')
    logging.info(f'-------------------')
    print(f"See output log for more details: {log_filename} ")


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
    global log_filename, _cfg_path, _logcfg, _warning_handler, _error_handler, _fatal_handler

    _cfg_path = Path(_find_package_path(bcedd.__pkg_cfg__))
    if not _cfg_path.is_dir():
        logging.exception('Can not find configuration path')
        raise FileNotFoundError

    _logcfg = _search_file(config_, 'logging.yaml')
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
                _log_filename = config_['log']['filename'].get()
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
            # Track if message gets logged with severity of error or greater
            _warning_handler = errorhandler.ErrorHandler(logging.WARNING)
            _error_handler = errorhandler.ErrorHandler(logging.ERROR)
            _fatal_handler = errorhandler.ErrorHandler(logging.CRITICAL)

            # keep log filename and path name
            log_filename = Path(cfg_log['handlers']['file']['filename']).resolve()

    except Exception:
        logging.exception('Error loading configuration file. Using default configs')
        raise  # Throw exception again so calling code knows it happened

    _logger_header()
    atexit.register(_logger_footer)


def _parse():
    """set up parameter from command line arguments
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
    parser.add_argument("--param",
                        type=str,
                        help="parameters configuration file",
                        dest='extra.parameters'
                        )
    parser.add_argument("--arguments",
                        action="store_const",
                        const=True,
                        help="print arguments value (from config file and/or inline argument) and exit",
                        dest='arguments'
                        )
    parser.add_argument("--version",
                        action="store_const",
                        const=True,
                        help="print release version and exit",
                        dest='version'
                        )

    # parse arguments
    args = parser.parse_args()

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
    global bceddPath  # _update_log

    bceddPath = Path(_find_package_path(__package__))
    if not bceddPath.is_dir():
        logging.exception('Can not find package path')
        raise FileNotFoundError

    # update_log_path = bceddPath / '.log'
    # if not update_log_path.is_dir():
    #     update_log_path.mkdir(parents=True, exist_ok=True)
    #     logging.warning(f'update log path -{update_log_path}- did not exist before.')

    # _update_log = update_log_path / 'update.log'


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


def _show_arguments(cfg_, print_=False):
    """ """
    logging.debug(f"config files:")
    logging.debug(f"   pkg              : {cfg_.default_config_path}")
    logging.debug(f"   user             : {cfg_.user_config_path()}")
    logging.debug(f"   logging          : {_logcfg}")

    logging.debug(f"paths.erddap        : {erddapPath}")
    logging.debug(f"paths.webinf        : {erddapWebInfDir}")
    logging.debug(f"paths.dataset.xml   : {datasetXmlPath}")
    logging.debug(f"paths.log           : {logPath}\n")

    logging.debug(f"log.filename        : {log_filename} ")
    logging.debug(f"log.verbose         : {cfg_['log']['verbose']}  ")
    logging.debug(f"log.level           : {cfg_['log']['level']}\n")

    logging.debug(f"authorised.eddtype  : {authorised_eddtype}")
    logging.debug(f"authorised.frequency: {authorised_frequency}\n")

    logging.debug(f"update.freq         : {cfg_['update']['freq']}\n")

    logging.debug(f"extra.parameters    : {extraParam}\n")

    if print_:
        print(f"config files:")
        print(f"   pkg              : {cfg_.default_config_path}")
        print(f"   user             : {cfg_.user_config_path()}")
        print(f"   logging          : {_logcfg}")

        print(f"paths.erddap        : {erddapPath}")
        print(f"paths.webinf        : {erddapWebInfDir}")
        print(f"paths.dataset.xml   : {datasetXmlPath}")
        print(f"paths.log           : {logPath}\n")

        print(f"log.filename        : {log_filename} ")
        print(f"log.verbose         : {cfg_['log']['verbose']}  ")
        print(f"log.level           : {cfg_['log']['level']}\n")

        print(f"authorised.eddtype  : {authorised_eddtype}")
        print(f"authorised.frequency: {authorised_frequency}\n")

        print(f"update.freq         : {cfg_['update']['freq']}\n")

        print(f"extra.parameters    : {extraParam}\n")
        exit(0)


def _show_version():
    """ """
    # print release version
    print(f'package: {bcedd.__name__}')
    print(f'version: {bcedd.__version__}')
    exit(0)


def main():
    """set up bcedd

    set up config file(s)
    set up logger
    """

    # init default
    _default_logger()

    # setup package path
    _setup_path()

    # read configuration file(s)
    config = _setup_cfg()

    # read command line arguments
    args = _parse()

    if args.version:
        _show_version()

    # overwrite configuration file parameter with parser arguments
    config.set_args(args, dots=True)

    # read logging configuration file
    _setup_logger(config)

    # check configuration file
    _chk_config(config)

    # print parameters use from config file and/or inline command
    _show_arguments(config, args.arguments)


if __name__ == '__main__':
    main()

    _logger = logging.getLogger(__name__)
    _logger.debug('This message should go to the log file')
    _logger.info('So should this')
    _logger.warning('And this, too')
    _logger.error('\tAnd non-ASCII stuff, too, like Øresund and Malmö\n')
    _logger.critical('this is critical')
    # _logger.exception('raise en exception')
