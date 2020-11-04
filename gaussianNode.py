#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:36:50 2020

@author: michal
"""
from jobNode import JobNode
from parsers import getLastCoordsFromLog, writeNewInput, getFreqs, getCheckpointNameFromInput
from parsers import readG16Inp
from shutil import copyfile
from os.path import join, isfile
from math import sqrt

def dist(coords1, coords2):
    dist = 0
    for c1, c2 in zip(coords1, coords2):
        dist += ( float(c1) - float(c2))**2
        
    return sqrt(dist)

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
        self.partition = "plgrid"
        self.chk = "checkp.chk"
        self.getCoordsFromParent = True
        
        self.readResults = False
        self.copyChk = False
        self.results = []
        self.software = "Gaussian"
        self.structure2dump = ""
        
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
        self.readChk()
        self.getCoordsFromParent = True
        self.id = None
        self.results = []
        
    def analyseLog(self):
        if hasattr(self, "distances2measure"):
            if self.distances2measure:
                self.measuredDistances = {}
                self.measureDistances()

        if not self.readResults:
            return
        
        if not isfile( join(self.path, self.logFile) ):
            print("File does not exists! ",join(self.path, self.logFile) )
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
        if hasattr(self, "distances2measure"):
            if self.distances2measure:
                self.measureDistances()
                
        
        if self.verification == "SP":
            return self.verifySP()
        elif self.verification == "Opt":
            return self.verifyOpt()
        elif self.verification == "Freq":
            return self.verifyFreq()
        else:
            raise Exception("Not implemented node verification")
            
    def measureDistances(self):
        self.measuredDistances = {}
        inputPath = join(self.path, self.inputFile)
        logPath = join(self.path, self.logFile)
        
        frozenInd, coords, elements = readG16Inp(inputPath)
        lastCoords = getLastCoordsFromLog(logPath)
        
        for distance in self.distances2measure:
            a = distance[0]
            b = distance[1]
            
            aElement = elements[a]
            bElement = elements[b]
            
            aCoords = lastCoords[a]
            bCoords = lastCoords[b]
            
            key = aElement+" "+str(a+1) + " - " + bElement + " " +str(b+1)
            value = dist(aCoords, bCoords)
            
            self.measuredDistances[key] = value
            
    
    def verifySP(self):
        lf = open(join(self.path, self.logFile))
        
        # lf.seek(0, 2)
        # lf.seek(-100,2)
        
        result = False
        line = lf.readline()
        while line:
            
            if "Normal termination of Gaussian" in line:
                print("\tNormal termination of Gaussian")
                result = True
                break
            
            line =lf.readline()
        
        lf.close()
        if not result:
            print("\tGaussian terminated abnormally")
        return result
    
    def verifyOpt(self):
        lf = open(join(self.path, self.logFile))
        
        line = lf.readline()
        result=False
        while line:
            
            if "-- Stationary point found." in line:
                print("-- Stationary point found.")
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
                print("\tNormal termination of Gaussian")
                result = True
                break
            
            line =lf.readline()
        
        lf.close()
        return result
    
    def verifyFreq(self):
        result = self.verifySP()
        if not result:
            return result
        
        freqs = getFreqs(join(self.path, self.logFile) )
        imaginaryFreqs = 0
        
        for data in freqs:
            if float(data["Frequency"]) < 0:
                imaginaryFreqs += 1
                
        print("\t imaginary freq no: ", imaginaryFreqs)
        return imaginaryFreqs == self.noOfExcpectedImaginaryFrequetions
        
    def writeSlurmScript( self, filename, processors, time):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --cpus-per-task="+str(processors)+"\n")
                        
        timeRestrictions = True

        if "timeRestrictions" in slurmConfig:
            timeRestrictions = slurmConfig["timeRestrictions"].upper() == "TRUE"

        if timeRestrictions:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid\n\n")

        if not "gaussianModule" in slurmConfig:
            slurmFile.write("module add plgrid/apps/gaussian/g16.B.01\n")
        else:
            slurmFile.write("module add "+slurmConfig["gaussianModule"]+"\n")
            
        if "additionalLines" in slurmConfig:
            slurmFile.write(slurmConfig["additionalLines"]+"\n")
            
        gaussianCommand = "g16"
        if "gaussianCommand" in slurmConfig:
            gaussianCommand = slurmConfig["gaussianCommand"]
            
        slurmFile.write(gaussianCommand+ " " + self.inputFile + "\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def generateFromParent(self, parent):        
        parentLog = parent.logFile
        parentInp = parent.inputFile
        
        if hasattr(self, "getCoordsFromParent"):
            if self.getCoordsFromParent:
                lastCoords = getLastCoordsFromLog(join(parent.path, parentLog))
                writeNewInput(join(parent.path, parentInp), lastCoords, join(self.path, self.inputFile), 
                              self.routeSection, self.skipParentAdditionalSection, self.additionalSection)
            else:
                if not isfile( join(self.path, self.inputFile ) ):
                    raise Exception( "Input file does not exists! "+self.inputFile )
        else:
            lastCoords = getLastCoordsFromLog(join(parent.path, parentLog))
            writeNewInput(join(parent.path, parentInp), lastCoords, join(self.path, self.inputFile), 
                            self.routeSection, self.skipParentAdditionalSection, self.additionalSection)
        
        self.readChk()
        if self.slurmFile:
            if isfile(join(self.path, self.slurmFile )):
                print("Using existing slurmFile: ", self.slurmFile)
            else:
                print("Generating slurmFile")
                self.writeSlurmScript("run.slurm", self.processors, self.time)
        else:
            print("Generating slurmFile")
            self.writeSlurmScript("run.slurm", self.processors, self.time)
        
        if self.copyChk:
            copyfile(join(parent.path, parent.chk), join(self.path, self.chk))
            
    def shouldBeRestarted(self):
        slurmOk, comment = self.verifySlurm()
        
        if "DUE TO TIME LIMIT" in comment:
            return True
        
        logFile = join(self.path, self.logFile)
        if not isfile(logFile):
            return False
        
        lf = open(logFile, 'r')
        
        restartThisJob = False
        
        line = lf.readline()
        
        while line:
            if "Error imposing constraints" in line:
                restartThisJob = True
                break
            elif "FormBX had a problem." in line:
                restartThisJob = True
                break
            
            line = lf.readline()
        
        lf.close()
        
        return restartThisJob