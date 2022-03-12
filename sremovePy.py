#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:13:54 2018

@author: michal
"""
import sys
from jobManager import JobManager

class SremoveManager(JobManager):
    def sremove( self, jobIds, byString = False ):
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
            
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print( "Usage: sremove jobId1, jobId2 ...")
    else:
        sm = SremoveManager()
        sm.sremove( sys.argv[1:] )
