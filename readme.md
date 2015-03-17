# HCAL Teststand Scripts
This is a collection of scripts to use on the HCAL teststands. The scripts should be written in a way that makes it easy to use their functions in your own scripts. Documentation for this might eventually appear.

## Installation

* `git clone git@github.com:elliot-hughes/hcal_teststand_scripts.git` will create a directory called `hcal_teststand_scripts` with the scripts inside.
* `cd hcal_teststand_scripts`
* Modify `configuration/teststands.txt` if you need to. (You should tell <code>tote@physics.rutgers.edu</code> what the correct settings should be.)
* `python install.py` will create important configuration files and setup scripts from the information in the `configuration/teststands.txt` configuration file.

## Running Scripts

* `cd hcal_teststand_scripts`
* Run `source configuration/setup_[teststand name].sh` where `[teststand name]` is what's used in `configuration/teststands.txt`.
* `python [script_name].py [arguments]`

## Documentation
Here are short summaries of what the different scripts do:

* `pedestals.py`: Reads in 100 BXs and prints the average ADC and standard deviation for each QIE. This script can also find a channel map between QIE numbering and uHTR numbering, a function that should be moved into a different module some time. This script takes the teststand name as a commandline argument, like `python pedestals.py bhm`. The default is `bhm`.
* `qie_card_valid.py`: Determines if a QIE card is operating correctly. This is very incomplete code; so far it just tests that the card's CIDs are rotating and synced.
* `versions.py`: Displays software and firmware versions of the different teststand components. This script takes the teststand name as a commandline argument, like `python versions.py bhm`. The default is `bhm`.

### Structure
*While this isn't implemented in the scripts, yet, this structure is where we're headed. __This is currently very incomplete documentation.__*

Most teststand operations revolve around a `teststand` object (defined in `hcal_teststand.py`). To initialize one, use
```
from hcal_teststand import *
ts = teststand("[teststand name]")
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
