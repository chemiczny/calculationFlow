#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:17:39 2018

@author: michal
"""
from os.path import isdir, join, isfile, expanduser
from os import mkdir, getcwd, system
from time import time
import sys

jobManagerDir = expanduser("~/jobManagerPro/")

if not isdir(jobManagerDir):
    mkdir(jobManagerDir)
    
runningCsv = "running.csv"
runningCsvPath = join(jobManagerDir, runningCsv)
tempFile = "fatality.log"
tempFilePath = join(jobManagerDir, tempFile)

def initRunningCsv():
    csv = open(runningCsvPath, 'w')
    csv.write("JobId\tTimeSbatch\tdirRun\tfileRun\tComment\n")
    csv.close()
    
def appendRunningCsv(jobId, timeStart, runDir, fileRun, comment):
    csv = open(runningCsvPath, 'a')
    csv.write(str(jobId)+"\t"+str(timeStart)+"\t"+runDir+"\t"+fileRun+"\t"+comment+"\n")
    csv.close()

if not isfile(runningCsvPath):
    initRunningCsv()
    
def readJobID():
    tempF = open(tempFilePath, 'r')
    line =tempF.readline()
    print line[:-1]
    tempF.close()
    jobID = line.split()[-1]
    return jobID
    
def sbatchPy(jobFile, comment = None):
    actualTime = time()
    actualDir = getcwd()
    comment2write = str(comment)
    system("sbatch "+jobFile+" &> " + tempFilePath)
    jobID = readJobID()
    
    appendRunningCsv(jobID, actualTime, actualDir, jobFile, comment2write)

if len(sys.argv) == 1:
    print "Podaj zadanie"
elif len(sys.argv) == 2:
    sbatchPy(sys.argv[1])
elif len(sys.argv) == 3:
    sbatchPy(sys.argv[1], sys.argv[2])
else:
    print "cooooo?"
