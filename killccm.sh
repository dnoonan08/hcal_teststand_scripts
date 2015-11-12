#!/bin/bash
i=0
#processes="$(ps o pid=,cmd= -C ngccm)"
processes="$(ps -e | grep ngccm)"
for process in $processes
do
#echo $process
if ! (( $i % 4 ))
then
t="$(ps -p $process -o etime=)"
t="$(echo $t | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')"
if [ "$t" -gt 3600 ]
then
#echo $(( $i / 4 ))':' $process '->' $t
kill -9 $process &> /dev/null
fi
fi
i=$(( $i + 1 ))
done
