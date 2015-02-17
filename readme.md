# Overview
This is a collection of scripts to use on the HCAL teststands. The scripts should be written in a way that makes it easy to use their functions in your own scripts. Documentation for this might eventually appear.

# Installation

* Running `git clone git@github.com:elliot-hughes/hcal_teststand_scripts.git` will create a directory called `hcal_teststand_scripts` with the scripts inside.

# Running Scripts

* `cd hcal_teststand_scripts`
* Before running the scripts, you should run `source setup.sh`
* `python [script_name].py`

# Documentation
Here are short summaries of what the different scripts do:

* `versions.py`: Displays software and firmware versions of the different teststand components.
* `qie_card_valid.py`: Determines if a QIE card is operating correctly. This is very incomplete code; so far it just tests that the card's CIDs are rotating and synched. 
