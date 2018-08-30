#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:17:39 2018

@author: michal
"""
from os.path import isdir, join, isfile, expanduser
from os import mkdir, getcwd, system
from time import time
import datetime
import sys

jobManagerDir = expanduser( "~/jobManagerPro/")

if not isdir(jobManagerDir):
    mkdir(jobManagerDir)
    
runningCsv = "running.csv"
runningCsvPath = join(jobManagerDir, runningCsv)
finishedCsv = "finished.csv"
finishedCsvPath = join(jobManagerDir, finishedCsv)
tempFile = "fatality.log"
tempFilePath = join(jobManagerDir, tempFile)

def initRunningCsv():
    csv = open(runningCsvPath, 'w')
    csv.write("JobId\tTimeSbatch\tdirRun\tfileRun\tComment\n")
    csv.close()
    
def readRunningCsv():
    csv = open(runningCsvPath, 'r')
    #csv.write(str(jobId)+"\t"+str(timeStart)+"\t"+runDir+"\t"+fileRun+"\t"+comment+"\n")
    data = {}
    line = csv.readline()
    line = csv.readline()
    while line:
        data[ line.split()[0]  ] = line
        line = csv.readline()
    csv.close()

    return data

if not isfile(runningCsvPath):
    initRunningCsv()
    
def readSqueueLog():
    tempF = open(tempFilePath, 'r')
    line =tempF.readline()
    data = {}

    line = tempF.readline()
    while line:
        data[line.split()[0] ] = line
        line = tempF.readline()
    tempF.close()
    return data
    
def squeuePy(deleteFinished = False):
    system("squeue  &> " + tempFilePath)
    sqData = readSqueueLog()
    runningData = readRunningCsv()

    jobsInSq = list( set(runningData.keys()) & set(sqData.keys()))
    jobsNotInSq = list( set(runningData.keys()) - set(jobsInSq ))

    jobsInSq.sort()
    jobsNotInSq.sort()

    print "Joby uruchomione lub oczekujace:"

    for jobId in jobsInSq:
        #print runningData[jobId]
        #print sqData[jobId]
        prettyPrint(runningData[jobId], sqData[jobId])
    
    print "Joby ukonczone"
    for jobId in jobsNotInSq:
        #print runningData[jobId]
        prettyPrint(runningData[jobId])

    if deleteFinished:
        cleanRunning(runningData, jobsInSq)
        updateFinished(runningData, jobsNotInSq)

def prettyPrint( myData, sqData = False ):
    myDataS = myData.split()
    print "jobID\t\t"+myDataS[0]
    print "Running Dir\t" + myDataS[2]
    print "Script file:\t" + myDataS[3]
    if myDataS[4] != "None":
        print "Comment\t\t"+myData[4]

    if sqData:
        sqS = sqData.split()
        print "Status\t\t" + sqS[4]
        print "Time:\t\t"+sqS[5]
        print "Partition\t"+sqS[1]
        if "PD" in sqS[4]:
            timeStart = float(myDataS[1])
            timeNow = time()
            timeDiff = timeNow - timeStart
            print "Waiting:\t"+str(datetime.timedelta(seconds=timeDiff))

    print 70*"#"

def cleanRunning(data, runningKeys):
    initRunningCsv()
    csv = open(runningCsvPath, 'a')
    for key in runningKeys:
        csv.write(data[key])
    csv.close()

def updateFinished(data, finishedKeys):
    csv = open(finishedCsvPath, 'a+')
    for key in finishedKeys:
        csv.write(data[key])
    csv.close()

if len(sys.argv) == 1:
    squeuePy()
elif len(sys.argv) == 2:
    squeuePy(True)
else:
    print "cooooo?"
