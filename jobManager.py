#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 11:42:00 2018

@author: michal
"""
from os.path import expanduser, join, isdir, isfile
from os import mkdir


class JobManager:
    def __init__(self):
        self.jobManagerDir = expanduser("~/.calculationFlow/")

        if not isdir(self.jobManagerDir):
            mkdir(self.jobManagerDir)
            
        runningCsv = "running.csv"
        self.runningCsvPath = join(self.jobManagerDir, runningCsv)
        tempFile = "fatality.log"
        self.tempFilePath = join(self.jobManagerDir, tempFile)
        finishedCsv = "finished.csv"
        self.finishedCsvPath = join(self.jobManagerDir, finishedCsv)
        
        if not isfile(self.runningCsvPath):
            self.initRunningCsv()
            
        
    def initRunningCsv(self):
        csv = open(self.runningCsvPath, 'w')
        csv.write("JobId\tTimeSbatch\tdirRun\tfileRun\tComment\n")
        csv.close()
        
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
    
    def append2Finished(self, data, finishedKeys):
        csv = open(self.finishedCsvPath, 'a+')
        for key in finishedKeys:
            csv.write(data[key])
        csv.close()
