#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:08:06 2019

@author: michal
"""
from os import getcwd, chdir
from sbatchPy import SbatchManager
from parsers import getLastCoordsFromLog, writeNewInput, getFreqs, getCheckpointNameFromInput
from os.path import join, isfile, expanduser
from shutil import copyfile
import json

class JobNode:
    def __init__(self, inputFile, path):
        self.inputFile = inputFile
        self.id = None
        self.path = path
        self.slurmFile = None
        self.status = "waitingForParent"
        self.valueForSorting = None
        self.software = None
        self.logFile = None
        
    def verifySlurm(self):
        if not self.id:
            return True, "No slurm id!"
            
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
        
    def readSlurmConfig(self):
        configPath = expanduser("~/jobManagerPro/config.json")
        slurmConfig = {}
        if not isfile(configPath):
            return slurmConfig
        
        configFile = open(configPath)
        slurmConfig = json.load(configFile)
        configFile.close()

        return slurmConfig
        
    
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
                        
        if not slurmConfig:
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
        
        
        