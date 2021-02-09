#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __main__.py

# ----------------------------------------------
# import from standard lib
import logging
from urllib.parse import urlparse
import copy
import pprint
from time import strftime, localtime
# import from other lib
import yaml
# import from my project
import bcedd.setupcfg as setupcfg

_type_list = ['table', 'grid']
_freq_list = ['weekly', 'monthly']

# ----------------------------------------------
def is_url(url_):
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


def _check_param(param_):
    """ """

    if not is_url(param_['url']):
        raise TypeError(f"invalid type for 'url'")

    if not isinstance(param_['type'], list):
        raise TypeError(f"'type' must be a list in yaml file")
    else:
        if any(tt not in _type_list for tt in param_['type']):
            raise ValueError(f"'type' value must be choose in {_type_list}")

    ff = param_['freq']
    if ff not in _freq_list:
        raise ValueError(f"'freq' value must be choose in _freq_list")


# def generate(srcname_, param_, freq_):
#     """ """
#     # creates output sub directory
#     datasetSubDir = 'Dataset/xml'
#     try:
#         datasetSubDir.mkdir(parents=True)
#     except FileExistsError:
#         # directory already exists
#         pass
#
#
#     if param_['freq'] != freq_:
#         print(f"Do not work of frequency {param_['freq']}")
#     else:
#         cmd_header = [srcname_, param_['url']]
#         for ttype in param_['type']:
#             cmd = copy.deepcopy(cmd_header)
#             cmd.append(ttype)
#             # add final argument
#             cmd.append('true')
#
#             # inserts executable
#             exe = './GenerateDatasetsXml.sh'
#             cmd.insert(0, exe)
#
#             print(f"{cmd}")
#
#             exe = Path.joinpath(setupcfg.erddapWebInfDir, exe)
#             # Check file exists
#             if not exe.is_file():
#                 raise FileNotFoundError(f"Can not find ERDDAP tools {exe}")
#
#             # Check for execution access
#             if not os.access(exe, os.X_OK):
#                 # change permission mode
#                 warnings.warn(f'change executable -{exe}- permission mode')
#                 exe.chmod(0o744)
#                 # raise PermissionError("")
#
#             # creates empty dataset file if need be
#             ds = Path.joinpath(datasetSubDir, _ds)
#             tag = '#' + srcname_ + '_' + ttype
#             tagline = '<!-- Begin GenerateDatasetsXml ' + tag + ' someDate -->'
#             if not self.ds.is_file():
#                 with open(self.ds, 'w') as f:
#                     f.write(tagline+'\n')
#                     f.write(re.sub('Begin', 'End', tagline))
#             else:
#                 # if file already exists, check taglines in file
#                 if not self._checkTag(self.ds, tagline):
#                     raise ValueError('file {} does not contains tags: {} and {}'
#                                      .format(self.ds, tagline, re.sub('Begin', 'End', tagline)))
#
#
#
#             # add tag to dataset name
#             dstag = Path.joinpath(datasetSubDir, self._ds + tag)
#             cmd.append('-i' + str(dstag))
#             #
#
#             # run process 'GenerateDatasetsXml.sh' from directory 'erddapWebInfDir' with arguments 'self._cmd'
#             # => creates file: ds
#             _logger.info(f'creates dataset: {self.ds}')
#             _logger.debug(f'from directory {setupcfg.erddapWebInfDir}, run process {cmd}')
#             process = subprocess.run(cmd,
#                                      cwd=setupcfg.erddapWebInfDir,
#                                      stdout=subprocess.PIPE,
#                                      timeout=60,
#                                      universal_newlines=True)
#             process.check_returncode()
#
# def concatenate():
#     """ concatenate header.xml dataset.XXX.xml footer.xml into local datasets.xml
#
#     >>> xmlout = concatenate()
#     concatenate in .../datasets.xml
#     \t.../header.xml
#     ...
#     \t.../footer.xml
#     >>> xmlout.__str__()
#     '.../datasets.xml'
#     """
#     dsxmlout = setupcfg.datasetXmlPath / 'datasets.xml'
#     _logger.debug(f'concatenate in {dsxmlout}')
#     with dsxmlout.open("w") as fp:
#         # add header
#         header = setupcfg.icp2eddPath / 'dataset' / 'header.xml'
#         _logger.debug('\t{}'.format(header))
#         fp.write(header.read_text())
#         # add single dataset
#         for ff in setupcfg.datasetXmlPath.glob('**/dataset.*.xml'):
#             _logger.debug('\t{}'.format(ff))
#             fp.write(ff.read_text())
#         # add footer
#         footer = setupcfg.icp2eddPath / 'dataset' / 'footer.xml'
#         _logger.debug('\t{}'.format(footer))
#         fp.write(footer.read_text())
#
#     return dsxmlout
#
# def check_duplicate(ds, gloatt, out=None):
#     """
#     :param ds: str
#        input filename
#     :param gloatt: dictionary
#        global and variable attribute to be added
#     :param out: str
#         output filename, optional
#     """
#     if not isinstance(ds, Path):
#         ds = Path(ds)
#
#     if not isinstance(gloatt, dict):
#         raise TypeError(f'Invalid type value, gloatt -{gloatt}- must be dictionary')
#
#     if out is not None and not isinstance(out, str):
#         raise TypeError(f'Invalid type value, out -{out}- must be string')
#
#     if not ds.is_file():
#         raise FileExistsError(f'File {ds} does not exist.')
#     else:
#         _logger.info(f'tree: {ds}')
#
#     # keep CDATA as it is
#     parser = etree.XMLParser(strip_cdata=False, encoding='ISO-8859-1')
#
#     tree = etree.parse(str(ds), parser)
#     root = tree.getroot()
#
#     # prevent creation of self-closing tags
#     for node in root.iter():
#         if node.text is None:
#             node.text = ''
#
#     # for node in list(root):
#     #    if node is not None:
#     # TODO need to test with variable attributes to add at every variables whatever datasetID
#     for node in root.findall('dataset'):
#         _logger.debug(f'node: tag -{node.tag}- attribute -{node.attrib}-')
#         if 'datasetID' in node.attrib:
#
#             dsID = node.attrib.get('datasetID')
#             if dsID in gloatt:
#                 _logger.debug(f'dsID: {dsID}')
#                 for attrNode in node.findall('addAttributes'):
#                     _logger.debug(f'attrNode: tag -{attrNode.tag}- attribute -{attrNode.attrib}-')
#                     for att in attrNode.iter('att'):
#                         attname = att.get('name')
#                         _logger.debug(f"att name: {attname} val: {att.text}")
#                         if att.get('name') in gloatt[dsID]:
#                             # TODO figure out how to keep information not to be changed
#                             if attname in keepERDDAP:
#                                 # keep ERDDAP attribute
#                                 del gloatt[dsID][attname]
#                             elif attname in keepICOSCP:
#                                 # keep ICOS CP attribute
#                                 attrNode.remove(att)
#                             else:
#                                 # append ERDDAP attribute with ICOS CP one
#                                 attrNode.remove(att)
#                                 gloatt[dsID][att.get('name')].append(att.text)
#                     for k, v in gloatt[dsID].items():
#                         # for k, v in gloatt.items():
#                         subnode = etree.SubElement(attrNode, 'att', name=k)
#                         subnode.text = ", ".join([str(x) for x in v])
#
#         for varNode in node.iter('dataVariable'):
#             _logger.debug(f'varNode : tag {varNode.tag} attribute {varNode.attrib}')
#             srcname = None
#             for attrNode in varNode.findall('sourceName'):
#                 srcname = attrNode.text
#                 _logger.debug(f'srcname {srcname}')
#
#             # for attrNode in varNode.findall('destinationName'):
#             #     dstname = attrnode.text
#
#             if srcname in gloatt:
#                 for attrNode in varNode.findall('addAttributes'):
#                     _logger.debug(f'attrNode : tag {attrNode.tag} attribute {attrNode.attrib}')
#                     for att in attrNode.iter('att'):
#                         attname = att.get('name')
#                         _logger.debug(f"att name: {attname} val: {att.text}")
#                         if attname in gloatt[srcname]:
#                             if attname in keepERDDAP:
#                                 # keep ERDDAP attribute
#                                 del gloatt[srcname][attname]
#                             elif attname in keepICOSCP:
#                                 # keep ICOS CP attribute
#                                 attrNode.remove(att)
#                             else:
#                                 # append ERDDAP attribute with ICOS CP one
#                                 attrNode.remove(att)
#                                 gloatt[srcname][att.get('name')].append(att.text)
#                     for k, v in gloatt[srcname].items():
#                         subnode = etree.SubElement(attrNode, 'att', name=k)
#                         subnode.text = ", ".join([str(x) for x in v])
#
#             etree.indent(node)
#
#     # write xml output
#     if out is not None:
#         dsout = out
#     else:
#         dsout = ds
#
#     tree.write(str(dsout), encoding='ISO-8859-1', xml_declaration=True)
#
# def replaceXmlBy(dsxmlout):
#     """ overwrite erddap datasets.xml with the new one
#     :param dsxmlout:
#     """
#     # remove erddap datasets.xml and create hard link to the new one
#     dsxml = setupcfg.erddapContentDir / 'datasets.xml'
#     if dsxml.is_file():  # and not dsxml.is_symlink():
#         dsxml.unlink()
#
#     _logger.info(f'create hard link to: {dsxmlout}')
#     dsxmlout.link_to(dsxml)

def main():
    """
    """
    # set up logger, paths, ...
    setupcfg.main()
    _logger = logging.getLogger(__name__)

    # 1 read yaml
    with open(setupcfg.yaml, 'r') as stream:
        try:
            data_loaded = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # select task to be done
    bindings = []
    for k, v in data_loaded.items():
        # check param
        try:
            _check_param(v)
        except Exception as err:
            raise Exception(f"Error in yaml file for {k}:\n\t{err}")

        # select frequency
        if v['freq'] == setupcfg.freq:
            # unpack type list
            for tt in v['type']:
                bindings += [(k,v['url'],tt)]

    pprint.pprint(bindings)
    # for b in bindings:
    #     # 2 run Generate
    #     generate(b)

    # 3 aggregate
    # dsxmlout = concatenate()
    # 4 check duplicate
    # check_duplicate(dsxmlout)
    # 5 create hard link
    # replaceXmlBy(dsxmlout)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Something goes wrong!!!')
        raise  # Throw exception again so calling code knows it happened

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
