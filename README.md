# BC-ERDDAP

---
## To run 'module.__main__' from terminal
$ python3 -m bcedd

### To get help/usage message
$ python3 -m bcedd --help

## To run bcedd inside a scheduler
$ python3 wrapper.py

## Configuration file
put your own configuration file in
~/.config/bcedd/config.yaml

```python
# This is the default config file for icp2edd

paths:
    # erddap: path of the main ERDDAP repository [tomcat]
    erddap: '/home/jpa029/Code/apache-tomcat-8.5.57'
    # dataset: path where store file from each dataset
    dataset:
        # path where store xml file from ICOS CP for each dataset
        xml: '/home/jpa029/Data/ICOS2ERDDAP/dataset'
    # log: path where store output log file
    log: '/home/jpa029/Data/ICOS2ERDDAP/log'

update:
    # freq: updating frequency to be applied ['weekly', 'monthly']
    freq: 'monthly'
    # yaml: filename with datasets to work with
    yaml: 'example.yaml'

log:
    # filename: logger filename
    # filename:
    # below, apply only on standard output log
    # TODO find a way to make it work, overwrite by argument
    # verbose: activate verbose mode [True|False]
    verbose: False
    # level: log level [DEBUG, INFO, WARN, ERROR, CRITICAL]
    level: 'INFO'
```

> **NOTE:** arguments overwrite value in configuration file.

## To run tests
see [here](tests/README.md)

## To install set up/update package library
see [PACKAGE.md](PACKAGE.md)
