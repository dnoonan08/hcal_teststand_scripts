#! /bin/env python

from ROOT import *
from commands import getoutput
from array import array
from sys import argv


if len(argv)>1:
    path=argv[1]
    if path[-1]!='/':
        path+='/'
    basetime=int(getoutput('date -d {0} +%s'.format(path.split('/')[-2])))
else:
    path='./'
    basetime=1438763742
if len(argv)>2:
    linknum=eval(argv[2])
else:
    linknum=[0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17]

def getdata(string):
    adctmps=getoutput("grep 'get {0}' {1}*.log".format(string,path)).split('\n')
    times=array("d")
    temps=array("d")
    for tmp in adctmps:
        if 'ERROR!!' in tmp: continue
        timest=tmp.split('/')[-1].split('.log:')[0].replace('_',' ')
        tmpst=tmp.split()[-1]
        hm=getoutput('date -d "{0}" +%s'.format(timest[:-2]))
        time=float(hm)+float(timest[-2:])-basetime
        temps.append(float(tmpst))
        times.append(time/3600)
    if len(times)==0:
        print 'ERROR: {0} has no data'.format(string)
        return TGraph()
    adctt=TGraph(len(times),times,temps)
    adctt.SetTitle('{0} vs t;t/h;'.format(string))
    return adctt

def adc58temphist():
    adctt=getdata('HF1-adc58_f')
    adctt.SetTitle('adc58_f T vs t;t/h;T/C')
    adctt.SetMinimum(0)
    adctt.SetMaximum(50)
    return adctt

def watemphist():
    watt=getdata('HF1-1wA_f')
    watt.SetTitle('1wA_f T vs t;t/h;T/C')
    watt.SetMinimum(0)
    watt.SetMaximum(50)
    return watt

def wbtemphist():
    wbtt=getdata('HF1-1wB_f')
    wbtt.SetTitle('1wB_f T vs t;t/h;T/C')
    wbtt.SetMinimum(0)
    wbtt.SetMaximum(50)
    return wbtt

def pwrbadhist():
    adctt=getdata('HF1-bkp_pwr_bad')
    adctt.SetTitle('PowerBad vs t;t/h;PowerBad')
    return adctt

def readvolt(cc):
    cc.cd()
    volt=[]
    label=['HF1-VIN_voltage_f','HF1-3V3_voltage_f','HF1-2V5_voltage_f','HF1-1V5_voltage_f','HF1-1V2_voltage_f']
    leg=TLegend(.8,.8,1,1)
    for i in range(len(label)):
        volt.append(getdata(label[i]))
        volt[i].SetLineColor(i+1)
        volt[i].SetFillColor(0)
        leg.AddEntry(volt[i],label[i])
        if i==0:
            volt[i].SetTitle('voltage vs time;time/h;voltage/V')
            volt[i].SetMinimum(0)
            volt[i].SetMaximum(10)
            volt[i].Draw("al")
        else:
            volt[i].Draw("same")
    leg.Draw('same')
    cc.Print('{0}Volt.png'.format(path))

def readcurr(cc):
    cc.cd()
    curr=[]
    label=['HF1-VIN_current_f','HF1-3V3_current_f','HF1-2V5_current_f','HF1-1V5_current_f']
    leg=TLegend(.8,.8,1,1)
    for i in range(len(label)):
        curr.append(getdata(label[i]))
        curr[i].SetLineColor(i+1)
        curr[i].SetFillColor(0)
        leg.AddEntry(curr[i],label[i])
        if i==0:
            curr[i].SetTitle('current vs time;time/h;I/A')
            curr[i].SetMinimum(0)
            curr[i].SetMaximum(4)
            curr[i].Draw("al")
        else:
            curr[i].Draw("same")
    leg.Draw('same')
    cc.Print('{0}Curr.png'.format(path))

def adcplt(listnum):
    files=getoutput("grep '{0}' {1}*.log".format(listnum,path).replace('[','\[').replace(']','\]')).split('\n')
    times=array('d')
    adccc=[]
    for i in range(len(listnum)*4):
        adccc.append(array('d'))
    for onefile in files:
        onefile=onefile.split(":")[0]
        timest=onefile.split('/')[-1][:-4].replace('_',' ')
        hm=getoutput('date -d "{0}" +%s'.format(timest[:-2]))
        time=float(hm)+float(timest[-2:])-basetime
        times.append(time/3600)
        adcs=eval(getoutput('grep "\[\[" {0}'.format(onefile)))
        adccs=[]
        for i in adcs: adccs.extend(i)
        for i in range(len(listnum)*4):
            adccc[i].append(float(adccs[i]))
    adccg=[]
    for i in range(len(listnum)*4):
        adccg.append(TGraph(len(times),times,adccc[i]))
        adccg[i].SetTitle('mean ADC vs t;t/h;ADC')
        adccg[i].SetMinimum(0)
    return adccg

def getlinkdata(string,linknum):
    adctmps=getoutput("grep '{0}' {1}*.log".format(string,path)).split('\n')
    times=array("d")
    bada=[]
    for i in range(len(linknum)):
        bada.append(array('d'))
    for tmp in range(len(adctmps)):
        if not tmp%2:
            tmps=adctmps[tmp]
            continue
        else:
            tmps+=adctmps[tmp].split(string)[-1]
        timest=tmps.split('/')[-1].split('.log:')[0].replace('_',' ')
        hm=getoutput('date -d "{0}" +%s'.format(timest[:-2]))
        time=float(hm)+float(timest[-2:])-basetime
        times.append(time/3600)
        ba=tmps.split(string)[-1].split()
        for i in range(len(linknum)):
            bada[i].append(float(ba[linknum[i]]))
    badas=[]
    for i in range(len(linknum)):
        badas.append(TGraph(len(times),times,bada[i]))
        badas[i].SetTitle('{1} link_{0} vs t;t/h;{1}'.format(linknum[i],string))
        badas[i].SetFillColor(0)
    return badas

def getlinkFB(string):
    adctmps=getoutput("grep '{0}' {1}*.log".format(string,path)).split('\n')
    times=array("d")
    temps1=array("d")
    temps2=array("d")
    for tmp in adctmps:
        if 'ERROR!!' in tmp: continue
        timest=tmp.split('/')[-1].split('.log:')[0].replace('_',' ')
        tmpst1=tmp.split()[-2]
        tmpst2=tmp.split()[-1]
        hm=getoutput('date -d "{0}" +%s'.format(timest[:-2]))
        time=float(hm)+float(timest[-2:])-basetime
        temps1.append(float(tmpst1))
        temps2.append(float(tmpst2))
        times.append(time/3600)
    adctt=[TGraph(len(times),times,temps1),TGraph(len(times),times,temps2)]
    adctt[0].SetTitle('{0} vs t;t/h;{0}'.format(string))
    adctt[0].SetMaximum(temps1[0]*1.5)
    adctt[0].SetMinimum(0)
    adctt[0].SetMarkerColor(2)
    adctt[1].SetMarkerColor(3)
    adctt[0].SetFillColor(0)
    adctt[1].SetFillColor(0)
    adctt[0].SetMarkerStyle(7)
    adctt[1].SetMarkerStyle(7)
    leg=TLegend(.6,.85,1,1)
    leg.AddEntry(adctt[0],"FrontFPGA "+string)
    leg.AddEntry(adctt[1],"BackFPGA "+string)
    adctt.append(leg)
    return adctt
    

if __name__=='__main__':
    c0=TCanvas('c0','c0',600,600)

    #temperature vs time
    print '\n===reading temperature'
    adctt=adc58temphist()
    watt=watemphist()
    wbtt=wbtemphist()
    adctt.SetMarkerStyle(7)
    adctt.Draw("ap")
    c0.Print('{0}ADC58TMP.png'.format(path))

    watt.SetMarkerStyle(7)
    watt.Draw("ap")
    c0.Print('{0}1waTMP.png'.format(path))

    wbtt.SetMarkerStyle(7)
    wbtt.Draw("ap")
    c0.Print('{0}1wbTMP.png'.format(path))

    #pwrbad vs time
    print '\n===reading powerbad'
    pwrbad=pwrbadhist()
    pwrbad.SetMarkerStyle(7)
    pwrbad.Draw('ap')
    c0.Print('{0}pwrbad.png'.format(path))
    #adc vs time
    print '\n===reading mean adc'
    adccg=adcplt(linknum)
    for n in range(len(linknum)):
        for i in range(4):
            adccg[n*4+i].SetMarkerStyle(7)
            adccg[n*4+i].SetTitle('mean ADC link{0}ch{1} vs t;t/h;ADC'.format(linknum[n],i))
            adccg[n*4+i].Draw('ap')
            c0.Print("{0}adcplt{1}ch{2}.png".format(path,linknum[n],i))

    #bad align vs time
    print '\n===reading bad align'
    badas=getlinkdata('Bad align',linknum)
    for n in range(len(linknum)):
        badas[n].SetMarkerStyle(7)
        badas[n].SetMinimum(0)
        badas[n].Draw('ap')
        c0.Print("{0}badalign{1}.png".format(path,linknum[n]))

    #bad data vs time
    print '\n===reading bad data'
    baddata=getlinkdata('Bad Data',linknum)
    for n in range(len(linknum)):
        baddata[n].SetMarkerStyle(7)
        baddata[n].SetMinimum(0)
        baddata[n].Draw('ap')
        c0.Print("{0}baddata{1}.png".format(path,linknum[n]))

    #orbit rate vs time
    print '\n===reading orbit rate'
    orrate=getlinkdata('OrbitRate(kHz)',linknum)
    fborr=getlinkFB('RATE_ORBIT (kHz)')
    leg=TLegend(0.6,.8,1,1)
    leg.AddEntry(orrate[0],'Link OrbitRate')
    leg.AddEntry(fborr[0],'FrontFPGA OrbitRate')
    leg.AddEntry(fborr[1],'BackFPGA OrbitRate')
    for n in range(len(linknum)):
        orrate[n].SetMarkerStyle(7)
        orrate[n].SetMaximum(13)
        orrate[n].SetMinimum(9)
        orrate[n].Draw('ap')
        fborr[0].Draw('samep')
        fborr[1].Draw('samep')
        leg.Draw('same')
        c0.Print("{0}OrbitRate{1}.png".format(path,linknum[n]))

    #Error data vs time
    print '\n===reading Error information'
    errinfo=[getlinkFB('BC0 Error'),getlinkFB('Single Error'),getlinkFB('Double Error')]
    for i in range(3):
        errinfo[i][0].Draw('ap')
        errinfo[i][1].Draw('samep')
        errinfo[i][2].Draw('same')
        c0.Print('{0}ErrorData{1}.png'.format(path,i))

    #I/V vs time
    print '\n===reading I/V information'
    readvolt(c0)
    readcurr(c0)



