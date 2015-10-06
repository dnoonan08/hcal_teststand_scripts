#! /bin/bash

if [ "$HOSTNAME" == 'vmepc-e1x07-06-01' ];then
    isrun=`ps ux|grep log_teststand.py|grep -v grep`
    if [ -z "$isrun" ]; then
	echo -e '\nNo log_teststand.py is running' >&2
	echo -e 'restarting log_teststand.py\n' >&2
	cd ~/hcal_teststand_scripts
	screen -dm -S logger bash -c ". configuration/setup_904.sh;(python log_teststand.py -s 5 -f 20)"
    else
	echo -e '\nlog_teststand.py is running' >&2
    fi
else
    ssh hcal904daq01 $0
fi
