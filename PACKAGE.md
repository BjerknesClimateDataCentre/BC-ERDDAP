# Package info

we use **pbr** to create this package

## How to set up/update  package library
$ python3 setup.py sdist bdist_wheel

This command should output a lot of text and once completed should generate two files in the
 **dist** directory.
> The tar.gz file is a Source Archive whereas the .whl file is a Built Distribution.
Newer pip versions preferentially install built distributions, but will fall back to source archives
if needed. You should always upload a source archive and provide built archives for the platforms your
 project is compatible with.

## How to install package
$ python3 -m pip install path/to/package/dist/icp2edd.SOME_RELEASE.tar.gz

## How to install package in development mode
$ pip(3) install -e path/to/package

## How to install one of github hosted repo's specific tag
### using git clone

$ git clone -b { tag name } --single-branch { repo name } .

> --single-branch flag prevents fetching all the branches in the cloned repository

### using pip
$ pip(3) install -e git+https://github.com/{ username }/{ repo name }.git@{ tag name }#egg={ desired egg name }

> for 'egg name', use the contents of project-name.egg-info/top_level.txt

## Version

### Semantic Version (Sem-Ver):
 Given a version number MAJOR.MINOR.PATCH, increment the:
 - MAJOR version when you make incompatible API changes,
 - MINOR version when you add functionality in a backwards-compatible manner, and
 - PATCH version when you make backwards-compatible bug fixes.

### **pbr** will automatically configure your version for you by parsing semantically-versioned Git tags, and commit.

- If the currently checked out revision is tagged, that tag is used as the version.
- If the currently checked out revision is not tagged, then **pbr** take the last tagged version number
and increment it to get a minimum target version.
    - **pbr** then walk Git history back to the last release.
    - Within each commit **pbr** look for a **Sem-Ver: pseudo header** and, if found, parse it looking for keywords.
    > Unknown symbols are not an error (so that folk can’t wedge pbr or break their tree),
but **pbr** will emit an info-level warning message.

    The following pseudo header are recognized:
    - feature
    - api-break
    - deprecation
    - bugfix

    A missing Sem-Ver line is equivalent to Sem-Ver: bugfix.
    - The bugfix symbol causes a patch level increment to the version.
    - The feature and deprecation symbols cause a minor version increment.
    - The api-break symbol causes a major version increment.
