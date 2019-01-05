#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:17:39 2018

@author: michal
"""
from os import system
from time import time
import datetime
import sys
from jobManager import JobManager

class SqueueManager(JobManager):        
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
        
    def squeuePy(self, deleteFinished = False, jobFilter = "" ):
        system("squeue  &> " + self.tempFilePath)
        sqData = self.readSqueueLog()
        runningData = self.readRunningCsv()
    
        jobsInSq = list( set(runningData.keys()) & set(sqData.keys()))
        jobsNotInSq = list( set(runningData.keys()) - set(jobsInSq ))
    
        jobsInSq.sort()
        jobsNotInSq.sort()
    
        print( "Joby uruchomione lub oczekujace:")
    
        for jobId in jobsInSq:
            if jobFilter != "" and not jobFilter in runningData[jobId]:
                continue
            
            self.prettyPrint(runningData[jobId], sqData[jobId])
        
        print( "Joby ukonczone")
        for jobId in jobsNotInSq:
            if jobFilter != "" and not jobFilter in runningData[jobId]:
                continue
            self.prettyPrint(runningData[jobId])
    
        if deleteFinished:
            self.cleanRunning(runningData, jobsInSq)
            self.append2Finished(runningData, jobsNotInSq)
    
    def prettyPrint( self, myData, sqData = False ):
        myDataS = myData.split()
        print( "jobID\t\t"+myDataS[0])
        print( "Running Dir\t" + myDataS[2])
        print( "Script file:\t" + myDataS[3])
        if myDataS[4] != "None":
            print( "Comment\t\t"+myDataS[4])
    
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

if len(sys.argv) == 1:
    sm = SqueueManager()
    sm.squeuePy()
elif len(sys.argv) == 2:
    sm = SqueueManager()
    if sys.argv[1] == "-r":
        sm.squeuePy(deleteFinished = True)
    else:
        sm.squeuePy(jobFilter = sys.argv[1])
else:
    print( "cooooo?")
