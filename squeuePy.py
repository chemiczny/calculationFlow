#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:17:39 2018

@author: michal
"""
from os.path import isdir, join, isfile, expanduser
from os import mkdir, system
from time import time
import datetime
import sys
from jobManager import JobManager

class SqueueManager(JobManager):
    def readRunningCsv(self):
        csv = open(self.runningCsvPath, 'r')
        data = {}
        line = csv.readline()
        line = csv.readline()
        while line:
            data[ line.split()[0]  ] = line
            line = csv.readline()
        csv.close()
    
        return data
        
    def readSqueueLog(self):
        tempF = open(self.tempFilePath, 'r')
        line =tempF.readline()
        data = {}
    
        line = tempF.readline()
        while line:
            data[line.split()[0] ] = line
            line = tempF.readline()
        tempF.close()
        return data
        
    def squeuePy(self, deleteFinished = False):
        system("squeue  &> " + self.tempFilePath)
        sqData = self.readSqueueLog()
        runningData = self.readRunningCsv()
    
        jobsInSq = list( set(runningData.keys()) & set(sqData.keys()))
        jobsNotInSq = list( set(runningData.keys()) - set(jobsInSq ))
    
        jobsInSq.sort()
        jobsNotInSq.sort()
    
        print( "Joby uruchomione lub oczekujace:")
    
        for jobId in jobsInSq:
            self.prettyPrint(runningData[jobId], sqData[jobId])
        
        print( "Joby ukonczone")
        for jobId in jobsNotInSq:
            #print runningData[jobId]
            self.prettyPrint(runningData[jobId])
    
        if deleteFinished:
            self.cleanRunning(runningData, jobsInSq)
            self.updateFinished(runningData, jobsNotInSq)
    
    def prettyPrint( self, myData, sqData = False ):
        myDataS = myData.split()
        print( "jobID\t\t"+myDataS[0])
        print( "Running Dir\t" + myDataS[2])
        print( "Script file:\t" + myDataS[3])
        if myDataS[4] != "None":
            print( "Comment\t\t"+myData[4])
    
        if sqData:
            sqS = sqData.split()
            print( "Status\t\t" + sqS[4])
            print( "Time:\t\t"+sqS[5])
            print( "Partition\t"+sqS[1])
            if "PD" in sqS[4]:
                timeStart = float(myDataS[1])
                timeNow = time()
                timeDiff = timeNow - timeStart
                print( "Waiting:\t"+str(datetime.timedelta(seconds=timeDiff)))
    
        print( 70*"#")
    
    def cleanRunning( self, data, runningKeys):
        self.initRunningCsv()
        csv = open(self.runningCsvPath, 'a')
        for key in runningKeys:
            csv.write(data[key])
        csv.close()
    
    def updateFinished(self, data, finishedKeys):
        csv = open(self.finishedCsvPath, 'a+')
        for key in finishedKeys:
            csv.write(data[key])
        csv.close()

if len(sys.argv) == 1:
    sm = SqueueManager()
    sm.squeuePy()
elif len(sys.argv) == 2:
    sm = SqueueManager()
    sm.squeuePy(True)
else:
    print( "cooooo?")
