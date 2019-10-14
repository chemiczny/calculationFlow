#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:17:39 2018

@author: michal
"""
from os import getcwd, system
from time import time
import sys
from jobManager import JobManager

class SbatchManager(JobManager):
    def appendRunningCsv(self, jobId, timeStart, runDir, fileRun, comment):
        csv = open(self.runningCsvPath, 'a')
        csv.write(str(jobId)+"\t"+str(timeStart)+"\t"+runDir+"\t"+fileRun+"\t"+comment+"\n")
        csv.close()
        
    def readJobID(self):
        tempF = open(self.tempFilePath, 'r')
        line =tempF.readline()
        print( line[:-1])
        tempF.close()
        if "Submitted" in line:
            jobID = line.split()[-1]
            return jobID
        else:
            return None
        
    def sbatchPy(self, jobFile, comment = None):
        actualTime = time()
        actualDir = getcwd()
        comment2write = str(comment)
        system("sbatch "+jobFile+" &> " + self.tempFilePath)
        jobID = self.readJobID()
        
        if jobID:
            self.appendRunningCsv(jobID, actualTime, actualDir, jobFile, comment2write)
            return jobID
        else:
            return None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print( "Podaj zadanie")
    elif len(sys.argv) == 2:
        sm = SbatchManager()
        sm.sbatchPy(sys.argv[1])
    elif len(sys.argv) == 3:
        sm = SbatchManager()
        sm.sbatchPy(sys.argv[1], sys.argv[2])
    else:
        print( "cooooo?")
