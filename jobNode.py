#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:08:06 2019

@author: michal
"""
from os import getcwd, chdir
from sbatchPy import SbatchManager
from parsers import getLastCoordsFromLog, writeNewInput, getFreqs, getCheckpointNameFromInput
from os.path import join, isfile
from shutil import copyfile

class JobNode:
    def __init__(self, inputFile, path):
        self.inputFile = inputFile
        self.id = None
        self.path = path
        self.slurmFile = None
        self.status = "waitingForParent"
        self.valueForSorting = None
        self.software = None
        
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
            self.writeSlurmFile("run.slurm")
            
        sm = SbatchManager()
        self.id = sm.sbatchPy(self.slurmFile, "Controlled by graph")
        
        chdir(lastDir)
        self.status = "running"
    
#    def restart(self):
#        pass
    
#    def generateSlurmFile(self):
#        pass
    
class GaussianNode(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
        self.routeSection = None
        self.additionalSection = None
        self.skipParentAdditionalSection = True
        self.logFile = self.inputFile.split(".")[0]+".log"
        self.verification = None
        self.noOfExcpectedImaginaryFrequetions = -1
        self.processors = 24
        self.time = "72:00:00"
        self.chk = "checkp.chk"
        
        self.readResults = False
        self.copyChk = False
        self.results = []
        self.software = "Gaussian"
        
    def readChk(self):
        if isfile( join( self.path, self.inputFile )):
            chkName = getCheckpointNameFromInput( join(self.path, self.inputFile) )
            if chkName:
                self.chk = chkName
        
    def rebuild(self, inputFile, path, slurmFile):
        self.inputFile = inputFile
        self.path = path
        self.logFile = self.inputFile.split(".")[0]+".log"
        self.slurmFile = slurmFile
        
    def analyseLog(self):
        if not self.readResults:
            return
        
        lf = open(join(self.path, self.logFile))
        
        line = lf.readline()
        energy = ""
        zpe = ""
        while line:
            if "E(" in line:
                energy = line
            elif "Zero-point correction=" in line:
                zpe = line

            line = lf.readline()
        
        lf.close()
        
        if energy:
            self.results.append(energy.strip())
            self.valueForSorting = float( energy.split()[4] )
            
        if zpe:
            self.results.append(zpe.strip())
        
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
        lf = open(join(self.path, self.logFile))
        
        # lf.seek(0, 2)
        # lf.seek(-100,2)
        
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
        
        # lf.seek(0, 2)
        # lf.seek(-100, 2)
        
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
        
        lastCoords = getLastCoordsFromLog(join(parent.path, parentLog))
        writeNewInput(join(parent.path, parentInp), lastCoords, join(self.path, self.inputFile), 
                      self.routeSection, self.skipParentAdditionalSection, self.additionalSection)
        
        self.readChk()
        self.writeSlurmScript("run.slurm", self.processors, self.time)
        
        if self.copyChk:
            copyfile(join(parent.path, parent.chk), join(self.path, self.chk))
        
        
        