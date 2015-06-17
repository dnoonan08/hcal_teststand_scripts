#! /bin/bash
isrun=`ps aux|grep restart.sh|grep -v grep`
if [ -z "$isrun" ]; then
    nohup /home/daq/ngFEC/ngccm-0.0.2-1.x86_64/opt/ngccm/bin/restart.sh >> /tmp/ngcc_output7.txt 2>&1 &
fi

cd ~/hcal_teststand_scripts

#screen -dm -S logger bash -c "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH && (python -u log_teststand.py 2>&1 | tee logger.log)" 
screen -dm -S logger bash -c "source ~/setup.sh && (python -u log_teststand.py 2>&1 | tee logger.log)" 
screen -dm -S monitor bash -c "source ~/setup.sh && (python -u monitor_teststand.py 2>&1 | tee monitor.log)"

