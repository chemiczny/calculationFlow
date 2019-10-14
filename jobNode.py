#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:08:06 2019

@author: michal
"""
from os import getcwd, chdir
from sbatchPy import SbatchManager
from parsers import getLastCoordsFromLog, writeNewInput, getFreqs
from os.path import join

class JobNode:
    def __init__(self, logFile, path):
        self.logFile = logFile
        self.id = None
        self.path = path
        self.done = False
        self.slurmFile = None
        self.id = None
        self.status = "waitingForParent"
        
    def verifySlurm(self):
        slurmFile = join( self.path, "slurm-"+str(self.id)+".out" )
        
        sf = open(slurmFile, 'r')
        line = sf.readline()
        result = True
        comment = ""
        while line:
            if "ERROR" in line.upper():
                result = False
                comment = line
            line = sf.readline()
        
        sf.close()
        
        return result, comment
    
    def run(self):
        lastDir = getcwd()
        
        chdir(self.path)
        if not self.slurmFile:
            self.generateSlurmFile("run.slurm")
            
        sm = SbatchManager()
        self.id = sm.sbatchPy(self.slurmFile, "Controlled by graph")
        
        chdir(lastDir)
        self.status = "running"
    
#    def restart(self):
#        pass
    
#    def generateSlurmFile(self):
#        pass
    
class GaussianNode(JobNode):
    def __init__(self, logFile, path):
        JobNode.__init__(self,logFile, path)
        self.routeSection = None
        self.additionalSection = None
        self.skipParentAdditionalSection = True
        self.inputFile = self.logFile.replace("log", "inp")
        self.verification = None
        self.noOfExcpectedImaginaryFrequetions = -1
        self.processors = 24
        self.time = "72:00:00"
        
    def verifyLog(self):
        if self.verification == "SP":
            return self.verifySP()
        elif self.verification == "Opt":
            return self.verifyOpt()
        elif self.verification == "Freq":
            return self.verifyFreq()
        else:
            raise Exception("Not implemented node verification")
    
    def verifySP(self):
        lf = open(self.logFile)
        
        lf.seek(-100)
        
        result = False
        line = lf.readline()
        while line:
            
            if "Normal termination of Gaussian" in line:
                result = True
                break
            
            line =lf.readline()
        
        lf.close()
        return result
    
    def verifyOpt(self):
        lf = open(self.logFile)
        
        line = lf.readline()
        while line:
            
            if "-- Stationary point found." in line:
                result = True
                break
            
            line =lf.readline()
        else:
            lf.close()
            return result
        
        lf.seek(-100)
        
        result = False
        line = lf.readline()
        while line:
            
            if "Normal termination of Gaussian" in line:
                result = True
                break
            
            line =lf.readline()
        
        lf.close()
        return result
    
    def verifyFreq(self):
        result = self.verifySP()
        if not result:
            return result
        
        freqs = getFreqs(self.logFile)
        imaginaryFreqs = 0
        
        for data in freqs:
            if float(data["Frequency"]) < 0:
                imaginaryFreqs += 1
                
        return imaginaryFreqs == self.noOfExcpectedImaginaryFrequetions
        
    def writeSlurmScript( self, filename, processors, time):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        slurmFile.write("#!/bin/env bash\n")
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --cpus-per-task="+str(processors)+"\n")
        slurmFile.write("#SBATCH --time="+str(time)+"\n")
        slurmFile.write("#SBATCH -p plgrid\n\n")

        slurmFile.write("module add plgrid/apps/gaussian/g16.B.01\n")
        slurmFile.write("g16 " + self.inputFile + "\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def generateFromParent(self, parent):        
        parentLog = parent.logFile
        parentInp = parent.inputFile
        
        lastCoords = getLastCoordsFromLog(parentLog)
        writeNewInput(join(parent.path, parentInp), lastCoords, join(self.path, self.inputFile), 
                      self.routeSection, self.skipParentAdditionalSection, self.additionalSection)
        self.writeSlurmScript("run.slurm", self.processors, self.time)
        
        
        