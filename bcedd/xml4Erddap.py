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
import yaml
# import from other lib
import lxml.etree as etree
# import from my project
import bcedd.setupcfg as setupcfg
import bcedd.parameters as parameters

# --- module's variable ------------------------
# load logger
_logger = logging.getLogger(__name__)


def _checkTag(ds_, tagline_):
    """
    check if both taglines:
        <!-- Begin GenerateDatasetsXml #XXX someDate -->
        <!-- End GenerateDatasetsXml #XXX someDate -->
    are presented in ds file.

    XXX is the name of the dataset (without suffix)

    :param ds_:
    :param tagline_:
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
    """

    :param srcname_: ERDDAP's name
    :param url_: ERDDAP's url
    :param type_: kind of dataset
    """
    # creates output sub directory
    datasetSubDir = setupcfg.datasetXmlPath
    try:
        datasetSubDir.mkdir(parents=True)
    except FileExistsError:
        # directory already exists
        pass

    cmd = [f"EDD{type_.capitalize()}FromErddap", url_, 'true']

    # inserts executable
    exe = './GenerateDatasetsXml.sh'
    cmd.insert(0, exe)

    exe = Path.joinpath(setupcfg.erddapWebInfDir, exe)
    # Check file exists
    if not exe.is_file():
        _logger.error(f"Can not find ERDDAP tools {exe}")
        raise FileNotFoundError

    # Check for execution access
    if not os.access(exe, os.X_OK):
        # change permission mode
        warnings.warn(f'change executable -{exe}- permission mode')
        exe.chmod(0o744)
        # raise PermissionError("")

    # creates empty dataset file if need be
    _ds = f"dataset.{srcname_}.{type_}.xml"
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


def check_datasetid(srcname_, url_, type_):
    """
    :param ds: str
       input filename
    :param out: str
        output filename, optional
    """
    # creates output sub directory
    datasetSubDir = setupcfg.datasetXmlPath
    try:
        datasetSubDir.mkdir(parents=True)
    except FileExistsError:
        # directory already exists
        pass

    # creates empty dataset file if need be
    _ds = f"dataset.{srcname_}.{type_}.xml"
    ds = Path.joinpath(datasetSubDir, _ds)
    if not isinstance(ds, Path):
        ds = Path(ds)

    if not ds.is_file():
        _logger.error(f"File {ds} does not exist.")
        raise FileExistsError

    # add dummy tag
    tmp = Path('dummy.xml')
    with tmp.open("w") as fp:
        # add header
        fp.write('<dummy>\n')
        # add single dataset
        fp.write(ds.read_text())
        # add footer
        fp.write('</dummy>')

    # keep CDATA as it is
    parser = etree.XMLParser(strip_cdata=False, encoding='ISO-8859-1')

    tree = etree.parse(str(tmp), parser)
    root = tree.getroot()

    # prevent creation of self-closing tags
    for node in root.iter():
        if node.text is None:
            node.text = ''

    # check parameters file
    param = parameters.main()
    # Use a `set` to keep track of "selected".
    keep = set(param['server'][srcname_]['keep'])

    if 'all' not in keep:
        _logger.info(f"from {srcname_}, keep: {keep}")
        # The iter method does a recursive traversal
        for node in root.findall('dataset'):

            # Since the id is what defines a duplicate for you
            if 'datasetID' in node.attrib:
                current = node.get('datasetID')
                # Not in keep means it's a useless, remove it
                if current not in keep:
                    node.getparent().remove(node)
    else:
        # keep all datasetIDs from sourcename_
        _logger.info(f"keep all datasetIDs from {srcname_}")
        pass

    # write xml output
    tree.write(str(tmp), encoding='ISO-8859-1', xml_declaration=False)

    # remove dummy tags
    with open(tmp, 'r') as fin:
        lines = fin.readlines()
    with open(str(ds), 'w') as fout:
        fout.writelines(lines[1:-1])

    # clean temporary file
    tmp.unlink()

def concatenate():
    """ concatenate header.xml dataset.XXX.xml footer.xml into local datasets.xml
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


def check_duplicate(ds, out=None):
    """
    :param ds: str
       input filename
    :param out: str
        output filename, optional
    """
    if not isinstance(ds, Path):
        ds = Path(ds)

    if out is not None and not isinstance(out, str):
        _logger.error(f'Invalid type value, out -{out}- must be string')
        raise TypeError

    if not ds.is_file():
        _logger.error(f"File {ds} does not exist.")
        raise FileExistsError
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

    # remove duplicate
    # Use a `set` to keep track of "visited" elements with good lookup time.
    visited = set()
    # The iter method does a recursive traversal
    # for node in root.iter('dataset'):
    for node in root.findall('dataset'):
        # print(f'node: tag -{node.tag}- attribute -{node.attrib}-')
        # Since the id is what defines a duplicate for you
        if 'datasetID' in node.attrib:
            current = node.get('datasetID')
            # In visited already means it's a duplicate, remove it
            if current in visited:
                node.getparent().remove(node)
            # Otherwise mark this ID as "visited"
            else:
                visited.add(current)

    # write xml output
    if out is not None:
        dsout = out
    else:
        dsout = ds

    tree.write(str(dsout), encoding='ISO-8859-1', xml_declaration=True)


def replaceXmlBy(dsxmlout):
    """ overwrite erddap datasets.xml with the new one

    :param dsxmlout:
    """
    # remove erddap datasets.xml and create hard link to the new one
    dsxml = setupcfg.erddapContentDir / 'datasets.xml'
    if dsxml.is_file():  # and not dsxml.is_symlink():
        dsxml.unlink()

    _logger.info(f'create hard link from {dsxmlout} to {dsxml}')
    dsxmlout.link_to(dsxml)
