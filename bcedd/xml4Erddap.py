#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xml4Erddap.py

# --- import -----------------------------------
# import from standard lib
from pathlib import Path
import re
import os
import subprocess
import logging
import warnings
from pprint import pformat
# from importlib import resources
# import from other lib
# > conda forge
import lxml.etree as etree
# import from my project
import bcedd.setupcfg as setupcfg

# --- module's variable ------------------------
# load logger
_logger = logging.getLogger(__name__)


def _checkTag(self, ds_, tagline_):
    """
    check if both taglines:
        <!-- Begin GenerateDatasetsXml #XXX someDate -->
        <!-- End GenerateDatasetsXml #XXX someDate -->
    are presented in ds file.

    XXX is the name of the dataset (without suffix)
    """
    if not isinstance(ds_, Path):
        raise TypeError(f'Invalid type value, ds_ -{ds_}- must be Pathlib object')
    if not isinstance(tagline_, str):
        raise TypeError(f'Invalid type value, tagline_ -{tagline_}- must be string')

    content = ds_.read_text()

    # 2020-11-04T15:34:08
    # tagline = re.sub('someDate', '.*', tagline_)
    tagline = re.sub('someDate', '(someDate|[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})', tagline_)
    if re.search(tagline, content):
        tagline = re.sub('Begin', 'End', tagline)

    return re.search(tagline, content)


def generate(srcname_, url_, type_):
    """ """
    # creates output sub directory
    datasetSubDir = setupcfg.datasetXmlPath
    try:
        datasetSubDir.mkdir(parents=True)
    except FileExistsError:
        # directory already exists
        pass

    cmd = [srcname_, url_, type_+'FromErddap', 'true']

    # inserts executable
    exe = './GenerateDatasetsXml.sh'
    cmd.insert(0, exe)

    print(f"{cmd}")

    exe = Path.joinpath(setupcfg.erddapWebInfDir, exe)
    # Check file exists
    if not exe.is_file():
        raise FileNotFoundError(f"Can not find ERDDAP tools {exe}")

    # Check for execution access
    if not os.access(exe, os.X_OK):
        # change permission mode
        warnings.warn(f'change executable -{exe}- permission mode')
        exe.chmod(0o744)
        # raise PermissionError("")

    # creates empty dataset file if need be
    _ds = f"datasets.{srcname_}.{type_}.xml"
    ds = Path.joinpath(datasetSubDir, _ds)
    tag = '#' + srcname_ + '_' + type_
    tagline = '<!-- Begin GenerateDatasetsXml ' + tag + ' someDate -->'
    if not ds.is_file():
        with open(ds, 'w') as f:
            f.write(tagline+'\n')
            f.write(re.sub('Begin', 'End', tagline))
    else:
        # if file already exists, check taglines in file
        if not _checkTag(ds, tagline):
            raise ValueError('file {} does not contains tags: {} and {}'
                             .format(ds, tagline, re.sub('Begin', 'End', tagline)))

        # add tag to dataset name
        dstag = Path.joinpath(datasetSubDir, _ds + tag)
        cmd.append('-i' + str(dstag))
        #

        # run process 'GenerateDatasetsXml.sh' from directory 'erddapWebInfDir' with arguments 'cmd'
        # => creates file: ds
        _logger.info(f'creates dataset: {ds}')
        _logger.debug(f'from directory {setupcfg.erddapWebInfDir}, run process {cmd}')
        process = subprocess.run(cmd,
                                 cwd=setupcfg.erddapWebInfDir,
                                 stdout=subprocess.PIPE,
                                 timeout=60,
                                 universal_newlines=True)
        process.check_returncode()


def concatenate():
    """ concatenate header.xml dataset.XXX.xml footer.xml into local datasets.xml

    >>> xmlout = concatenate()
    concatenate in .../datasets.xml
    \t.../header.xml
    ...
    \t.../footer.xml
    >>> xmlout.__str__()
    '.../datasets.xml'
    """
    dsxmlout = setupcfg.datasetXmlPath / 'datasets.xml'
    _logger.debug(f'concatenate in {dsxmlout}')
    with dsxmlout.open("w") as fp:
        # add header
        header = setupcfg.bceddPath / 'dataset' / 'header.xml'
        _logger.debug('\t{}'.format(header))
        fp.write(header.read_text())
        # add single dataset
        for ff in setupcfg.datasetXmlPath.glob('**/dataset.*.xml'):
            _logger.debug('\t{}'.format(ff))
            fp.write(ff.read_text())
        # add footer
        footer = setupcfg.bceddPath / 'dataset' / 'footer.xml'
        _logger.debug('\t{}'.format(footer))
        fp.write(footer.read_text())

    return dsxmlout

def check_duplicate(ds, gloatt, out=None):
    """
    :param ds: str
       input filename
    :param gloatt: dictionary
       global and variable attribute to be added
    :param out: str
        output filename, optional
    """
    if not isinstance(ds, Path):
        ds = Path(ds)

    if not isinstance(gloatt, dict):
        raise TypeError(f'Invalid type value, gloatt -{gloatt}- must be dictionary')

    if out is not None and not isinstance(out, str):
        raise TypeError(f'Invalid type value, out -{out}- must be string')

    if not ds.is_file():
        raise FileExistsError(f'File {ds} does not exist.')
    else:
        _logger.info(f'tree: {ds}')

    # keep CDATA as it is
    parser = etree.XMLParser(strip_cdata=False, encoding='ISO-8859-1')

    tree = etree.parse(str(ds), parser)
    root = tree.getroot()

    # prevent creation of self-closing tags
    for node in root.iter():
        if node.text is None:
            node.text = ''

    # Use a `set` to keep track of "visited" elements with good lookup time.
    visited = set()
    # The iter method does a recursive traversal
    for el in root.iter('dataset'):
        # Since the id is what defines a duplicate for you
        if 'id' in el.attr:
            current = el.get('datasetID')
            # In visited already means it's a duplicate, remove it
            if current in visited:
                el.getparent().remove(el)
            # Otherwise mark this ID as "visited"
            else:
                visited.add(current)

    # write xml output
    if out is not None:
        dsout = out
    else:
        dsout = ds

    tree.write(str(dsout), encoding='ISO-8859-1', xml_declaration=True)
#
def replaceXmlBy(dsxmlout):
    """ overwrite erddap datasets.xml with the new one
    :param dsxmlout:
    """
    # remove erddap datasets.xml and create hard link to the new one
    dsxml = setupcfg.erddapContentDir / 'datasets.xml'
    if dsxml.is_file():  # and not dsxml.is_symlink():
        dsxml.unlink()

    _logger.info(f'create hard link to: {dsxmlout}')
    dsxmlout.link_to(dsxml)
