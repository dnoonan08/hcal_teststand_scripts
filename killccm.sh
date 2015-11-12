#!/bin/bash
#processes="$(ps o pid=,cmd= -C ngccm)"
pids="$(pgrep -u `whoami` ngccm)"
for pid in $pids
do
t="$(ps -p $pid -o etime=)"
t="$(echo $t | awk -F: '{ print ($1 * 60) + $2 }')"
if [ "$t" -gt 3600 ]
then
kill -9 $pid &> /dev/null
fi
done
