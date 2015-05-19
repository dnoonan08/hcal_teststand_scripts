# HCAL Teststand Scripts
This is a collection of scripts to use on the HCAL teststands. The scripts should be written in a way that makes it easy to use their functions in your own scripts. Documentation for this might eventually appear.

## Installation

1. `git clone git@github.com:elliot-hughes/hcal_teststand_scripts.git` will create a directory called `hcal_teststand_scripts` with the scripts inside.<sup>[1](#footnote1)</sup>
1. `cd hcal_teststand_scripts`
1. Modify `configuration/teststands.txt` if you need to. (You should tell <code>tote@physics.rutgers.edu</code> what the correct settings should be.)
1. `python install.py` will create important configuration files and setup scripts from the information in the `configuration/teststands.txt` configuration file.

## Running Scripts

Make sure you connect to a machine with Python 2.6 or greater. For the 904 teststand, use `ssh hcal904daq01.cms904` from inside the head node.

1. `cd hcal_teststand_scripts`
1. Run `source configuration/setup_[teststand name].sh` where `[teststand name]` is what's used in `configuration/teststands.txt`.
1. `python [script_name].py [arguments]`

## Documentation
Here are short summaries of what the different scripts do:

* `pedestals.py`: Reads in 100 BXs and prints the average ADC and standard deviation for each QIE. This script can also find a channel map between QIE numbering and uHTR numbering, a function that should be moved into a different module some time. This script takes the teststand name as a commandline argument, like `python pedestals.py 904`. The default is `904`.
* `qie_card_valid.py`: Determines if a QIE card is operating correctly. This is very incomplete code; so far it just tests that the card's CIDs are rotating and synced.
* <a name="uhtr_map"></a>`uhtr_map.py`: For each QIE card, write the card's unique ID to an IGLOO register. Set the link test mode to type B. Then for each uHTR, read out the unique ID through SPY and map link number to unique ID. This script takes the teststand name as a commandline argument, like `python uhtr_map.py 904`. The default is `904`.
* `versions.py`: Displays software and firmware versions of the different teststand components. This script takes the teststand name as a commandline argument, like `python versions.py 904`. The default is `904`.

### Structure
Most teststand operations revolve around a `teststand` object (defined in `hcal_teststand.py`). To initialize one, use
```
from hcal_teststand import *
ts = hcal_teststand.teststand("[teststand name]")
```
where `[teststand name]` is what's used in `configuration/teststands.txt`, such as `bhm`. This object then has a number of attributes, like the MCH IP address, `ts.mch_ip`, and some methods, like `ts.status()`. Try running 
```
print ts.status()
```

Functions related to a specific component are located in of a module named after it. Here is a list of the different teststand component modules:

* `amc13.py`
* `mch.py`
* `glib.py`
* `uhtr.py`
* `ngccm.py`
* `qie.py`

### The `teststand` object
When you initialize a teststand (see above), it reads configuration information from `configuration/teststands.txt`. For example, the presence of front-end crates is specified by a list of identifying integers. The QIE cards are specified as sets of lists for each front-end crate, separated by semicolons. Both of these organizations are stored in the `fe` variable (a dictionary) of your teststand object.

# Recent Changes
* 150519: Tote fixed a minor bug in `ngccm.send_commands_parsed` to prevent commands from being interpreted as regular expressions. Tote also fixed a few problems with QIE settings functions. Tote added QIE mapping functions.
* 150515: Tote added the `ber_test.py` script to check writing and reading to Bridge scratch register.
* 150505: Tote turned all of the modules into a simple package called `hcal_teststand`. From now on, only keep scripts and `readme.md` in the main directory. Tote renamed `playground.py` to `example.py` and changed its contents a little to be slightly more educational. Tote changed the default teststand of each script to `904`. Tote fixed a minor bug in `ngccm.send_commands_parsed` that saved the wrong command result.
* 150429: Tote renamed `uhtr.get_links` to `uhtr.find_links`. The `uhtr.get_links` function now does something much more powerful, actually returning link objects which contain the "uHTR mapping" information. Tote moved `ngccm.set_unique_id` (and other similar functions) to the `qie` namespace.
* 150428: Tote moved some things around. Tote really likes the `uhtr.link` class, so he's going to finish implementing it everywhere tomorrow. This will integrate the "uhtr map" idea into the basic framework.
* 150424: Tote added `uhtr_map.py` (see [documentation above](#uhtr_map)). In doing this, Tote moved `uhtr.map_links` from `uhtr` to `uhtr_map` and renamed it to `read_links`, Tote fixed a minor "hardcode" bug in `ngccm.set_unique_id`, and Tote incorporated `ngccm.link_test_mode` and `ngccm.link_test_modeB` into `hcal_teststand.set_mode`.
* 150421: Tote updated the readme. He modified the 904 configuration (AMC13 IPs and QIE slot number). He also fixed minor bugs in `ngccm.send_commands` and `qie.get_info`.

# Notes
<a name="footnote1">1</a>: This assumes you have [SSH keys set up](https://help.github.com/articles/generating-ssh-keys/). If you don't, you can always use HTTPS: `git clone https://github.com/elliot-hughes/hcal_teststand_scripts.git`. If you see an error like `error: SSL certificate problem, verify that the CA cert is OK.`, you can set `git config --global http.sslVerify false` to ignore it. A more secure solution would be to update your OS or [set up the SSH keys](https://help.github.com/articles/generating-ssh-keys/).
