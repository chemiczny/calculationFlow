#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:13:54 2018

@author: michal
"""
import sys
from jobManager import JobManager

class SremoveManager(JobManager):
    def sremove( self, jobIds ):
        jobs = self.readRunningCsv()
        
        self.initRunningCsv()
        removedJobs = []
        csv = open(self.runningCsvPath, 'a')
        for key in jobs:
            if not key in jobIds:
                csv.write(jobs[key])
            else:
                removedJobs.append(key)
        csv.close()
        
        if removedJobs:
            self.append2Finished(jobs, removedJobs)
            
if len(sys.argv) == 1:
    print( "Podaj nr joba")
elif len(sys.argv) == 2:
    sm = SremoveManager()
    sm.sremove( [ sys.argv[1] ] )
else:
    sm = SremoveManager()
    sm.sremove( sys.argv[1:] )