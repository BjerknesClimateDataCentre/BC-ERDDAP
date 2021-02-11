# BC-ERDDAP

---
## To run 'package' from terminal
$ python3 -m bcedd

### To get help/usage message
$ python3 -m bcedd --help

## To run bcedd inside a wrapper
$ python3 wrapper.py

## Configuration file
put your own configuration file in `~/.config/bcedd/config.yaml`

```python
# This is the default config file for bcedd

paths:
    # erddap: path of the main ERDDAP repository [tomcat]
    erddap: '/home/jpa029/Code/apache-tomcat-8.5.57'
    # dataset: path where store file from each dataset
    dataset:
        # path where store xml file from ICOS CP for each dataset
        xml: '/home/jpa029/Data/BC-ERDDAP/dataset/xml'
    # log: path where store output log file
    log: '/home/jpa029/Data/BC-ERDDAP/log'

update:
    # freq: updating frequency to be applied ['weekly', 'monthly']
    freq: 'monthly'
    # eddyaml: yaml filename of remote ERDDAP server to work with
    erddap: 'erddap.yaml'
    # datasetid: yaml filename of datasetIDs to keep
    datasetid: 'datasetid.yaml'

log:
    # filename: logger filename
    # filename:
    # below, apply only on standard output log
    # verbose: activate verbose mode [True|False]
    verbose: False
    # level: log level [DEBUG, INFO, WARN, ERROR, CRITICAL]
    level: 'INFO'
```

> **NOTE:** arguments overwrite value in configuration file.

## To run tests
see [HERE](tests/README.md)

## To install set up/update package library
see [PACKAGE.md](PACKAGE.md)

## Use cron to schedule job
$ crontab -e  
```bash
# crontab -e
SHELL=/bin/bash
MAILTO=jpa029@uib.no

# Example of job definition:
# m h dom mon dow   command

# * * * * *  command to execute
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59)

# For details see man 4 crontabs

# weekly update (monday at 01:30) of ERDDAP server
30 01 * * 1 python3 -m bcedd -f 'weekly' --log_filename 'debug.weekly.log'

# monthly update (first day of each month at 02:30) of ERDDAP server
30 02 1 * * python3 -m bcedd -f 'monthly' --log_filename 'debug.monthly.log'
```
