#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __init__.py

# --- import -----------------------------------
# import from standard lib
# import from other lib
from pbr.version import VersionInfo as _VersionInfo
# import from my project

__all__ = (
    '__version__',
    '__version_long__',
    '__nextMajor__',
    '__nextMinor__',
    '__nextPatch__',
    'version_info'
)

# semantic version (Sem-Ver): "major.minor.micro/patch"
#   - Breaking changes are indicated by increasing the major number (high risk)
#   - New non-breaking features increment the minor number (medium risk)
#   - All other non-breaking changes increment the patch number (lowest risk)
_v = _VersionInfo(__package__).semantic_version()
__version__ = _v.brief_string()
__version_long__ = _v.release_string()

__nextPatch__ = _v.increment(minor=False, major=False).brief_string()
__nextMinor__ = _v.increment(minor=True, major=False).brief_string()
__nextMajor__ = _v.increment(minor=False, major=True).brief_string()

version_info = _v.version_tuple()

# where configuration files are stored
__pkg_cfg__ = f'{__package__}.cfg'
