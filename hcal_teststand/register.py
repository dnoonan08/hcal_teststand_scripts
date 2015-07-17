##############################################
# Register.py - 
#    class to implement simple read/write actions
#
# Author: A. Whitbeck - July 11, 2015
##############################################

import ngccm
from hcal_teststand import *

class register : 
    
    # CONSTRUCTOR
    def __init__( self , 
                  ts        ,
                  name = "" ,  # currently, name should corerspond to the name used by the ngccm, ignoring HF<crate>-<slot>-  
                  size = 1     # size should be number of bits
                  ):

        self.verbosity = 0 

        #output = ngccm.send_commands_parsed(ts, ["ls"] )["output"]
        #if self.verbosity >= 1 :
        #    print "REGISTER CONSTRUCTOR --"
        #    print output

        self.ts        = ts
        self.name      = name
        self.size      = size
        self.commandCache = []

    def setVerbosity( self , verb ) :
        self.verbosity = verb

    def testCache( self ) :
        
        errors = 0 
        executeErrors = 0 
        totalTests = 0 

        output = ngccm.send_commands_parsed( self.ts , self.commandCache )["output"]

        if self.verbosity >= 1 :
            print output
        
        if len( output ) % 2 != 0 : 
            print "ERROR, register::testCach() - the wrong number of commands were executed"
            return -999 
        for i in range( len( output ) / 2 ) :
            if output[i*2]["cmd"].find("put ") == -1 :
                print "ERROR, register::testCach() - commands executed in wrong order??"
                return -999 
            else :
                value = output[i*2]["cmd"].split()[2:]

            if self.verbosity >= 1 : 
                print "value:",value

            valueNum = []
            for v in value :
                valueNum.append( int(v,16) )

            if output[i*2]["result"] != "OK" : 
                executeErrors = executeErrors + 1
                continue
            else :
                totalTests = totalTests + 1

            if output[i*2+1]["cmd"].find("get ") == -1 :
                print "ERROR, register::testCach() - commands executed in wrong order??"
                return -999 
            else : 
                #check = output[i*2+1]["result"].split("'")[1].split()
                check = output[i*2+1]["result"].split()

            if self.verbosity >= 1 :
                print "check:",check

            checkNum = []
            for c in check[::-1] :
                checkNum.append( int(c,16) )

            ### valueNum and checkNum are compared so that
            ### leading zeroes will be conveniently ignored
            if valueNum != checkNum : 
                errors = errors + 1

        print "--------------------------------"
        print "REGISTER:",self.name
        print "--------------------------------"
        print "errors:",errors
        print "execution errors:",executeErrors
        print "success rate:", 100. * ( 1. - float( errors ) / float( totalTests ) ),"%"

    def addTestToCache( self, value ) :

        self.commandCache.append( "put {0} {1}".format( self.name , value ) )
        self.commandCache.append( "get {0}".format( self.name , value ) )
        
    def read( self ) :
        
        output = ngccm.send_commands_parsed( self.ts, ["get {0}".format(self.name)] )["output"][0]["result"]
        if self.verbosity >= 1 : 
            print "REGISTER::READ() --"
            print output

        return output

    def write( self , value = '') :
        
        output = ngccm.send_commands_parsed(self.ts, ["put {0} {1}".format(self.name,value)] )["output"][0]["result"]
        if self.verbosity >= 1 : 
            print "REGISTER::WRITE() --"
            print output
        
        if output.find("ERROR!") != -1 : 
            return False
        else : 
            return True
        
