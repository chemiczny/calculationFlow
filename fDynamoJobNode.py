#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 15:17:36 2019

@author: michal
"""

from jobNode import JobNode
from os.path import join, isfile, expanduser
from shutil import copyfile
from os import getcwd, chdir, system
from crdParser import getCoords, dist, atomsFromAtomSelection

class FDynamoNode(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
        self.logFile = "a.log"
        self.verification = []
        self.templateKey = ""
        self.additionalKeywords = {}
        
        self.templateDict = { "QMMM_opt_mopac" : [ "QMMM_opt.f90", "panadero.f90" ], 
                             "QMMM_irc_mopac" : [ "IRC.f90", "mep_project.f90" ] ,
                             "QMMM_scan1D_mopac" : [ "scan1D.f90" ],
                             "QMMM_pmf" : [ "pmf.f90" ] }
        
        self.noOfExcpectedImaginaryFrequetions = -1
        self.processors = 1
        self.time = "1:00:00"
        self.partition = "plgrid-short"
        self.getCoordsFromParent = True
        
        self.readResults = False
        self.results = []
        self.software = "fDynamo"
        self.structure2dump = ""
        
        self.forceField = ""
        self.flexiblePart = ""
        self.sequence = ""
        self.qmSele = ""
        self.fDynamoPath = ""
        self.charge = None
        self.method = ""
        
        self.coordsIn = ""
        self.coordsOut = ""
        
        self.anotherCoordsSource = ""
        self.readInitialScanCoord = False
        
        self.measureRCinOutput = False
        
    def rebuild(self, inputFile, path, slurmFile):
        self.inputFile = inputFile
        self.path = path
        self.slurmFile = slurmFile
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
        
        while line:
            if "Potential Energy     =" in line:
                energy = line[:42]

            line = lf.readline()
        
        lf.close()
        
        if energy:
            self.results.append(energy.strip())
            self.valueForSorting = float( energy.split()[3] )
            
        
    def verifyLog(self):
        res = True
        if "SP" in self.verification:
            res = res and self.verifySP()
        if "Opt" in self.verification:
            res = res and self.verifyOpt()
        if "Freq" in self.verification:
            res = res and self.verifyFreq()
        if "scan1D" in self.verification:
            res = res and self.verifyScan1D()

        if hasattr(self, "measureRCinOutput"):
            if self.measureRCinOutput:
                atoms = atomsFromAtomSelection( self.additionalKeywords["definedAtoms"] )
                getCoords( join(self.path, self.coordsOut), atoms)
                
                rc =  dist(atoms[0], atoms[1]) - dist(atoms[1], atoms[2])
                
                if rc < 0 :
                    copyfile( join(self.path, self.coordsOut), join(self.path, "RC_negative_" + self.coordsOut) )
                else:
                    copyfile( join(self.path, self.coordsOut), join(self.path, "RC_positive_" + self.coordsOut) )

        return res
        
    def verifyScan1D(self):
        scanFile = join(self.path, "fort.900" )
        if not isfile(scanFile):
            raise Exception("File with scan results not found")
            
        coordIndex = 0
        sf = open(scanFile, 'r')
        
        line = sf.readline()
        highestEnergy = float(line.split()[1])
        highestIndex = coordIndex
        while line:
            
            energy = float(line.split()[1])
            if energy > highestEnergy:
                highestEnergy = energy
                highestIndex = coordIndex
            
            line = sf.readline()
            coordIndex += 1
        
        sf.close()
        
        coordsOut = ""
        
        if isfile( join(self.path, "seed.+"+str(highestIndex)) ):
            coordsOut = "seed.+"+str(highestIndex)
            
        elif isfile( join(self.path, "seed.-"+str(highestIndex)) ):
            coordsOut = "seed.-"+str(highestIndex)
            
        self.coordsOut = coordsOut
        
        return True
    
    def verifySP(self):
        lf = open(join(self.path, self.logFile))
        
        result = False
        line = lf.readline()
        while line:
            
            if "Potential Energy Terms" in line:
                print("\tNormal termination of fDYNAMO")
                result = True
                break
            
            line =lf.readline()
        
        lf.close()
        if not result:
            print("\tfDYNAMO terminated abnormally")
        return result
    
    def verifyOpt(self):
        lf = open(join(self.path, self.logFile))
        
        line = lf.readline()
        result=False
        while line:
            
            if "Baker Search Status:" in line:
                break
            
            line =lf.readline()
        else:
            lf.close()
            return result
        
        if "Gradient tolerance reached." in line:
            result = True

        return result
    
    def verifyFreq(self):
        freqs = []
        
        freqsFile = open(join(self.path, self.logFile), 'r' )
        line = freqsFile.readline()
        
        while line and not "------ Harmonic Frequencies" in line:
            line = freqsFile.readline()
        
        
        if "Harmonic Frequencies" in line:
            line = freqsFile.readline()
            
            freqsStr = line.split()
            freqs = [ float(f) for f in freqsStr ]
        
        
        freqsFile.close()
        
        if not freqs:
            print("No frequencies in file!")
            return False
        
        imaginaryFreqs = 0
        zeroFreqs = 0
        
        for f in freqs:
            if f < 0:
                imaginaryFreqs += 1
                
            if abs(f) < 0.000001:
                zeroFreqs += 1
                
        print("\t imaginary freq no: ", imaginaryFreqs)
        print("\t zero freq no: ", zeroFreqs)
        
        
        if imaginaryFreqs != self.noOfExcpectedImaginaryFrequetions:
            print("Wrong number of imaginary freqs!")
            return False
        
        if zeroFreqs != 6:
            print("Wrong number of zero freqs!")
            return False
        
        return True
        
    def writeSlurmScript( self, filename, processors = "", time = ""):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()

        if not processors:
            processors = str(self.processors)

        if not time:
            time = self.time
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --cpus-per-task="+str(processors)+"\n")
                        
        if not slurmConfig:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            
        if "additionalLines" in slurmConfig:
            slurmFile.write(slurmConfig["additionalLines"]+"\n")
            
        slurmFile.write("./a.out &> " + self.logFile + "\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def generateFromParent(self, parent):        
        if not self.qmSele and hasattr(parent, "qmSele"):
            self.qmSele = parent.qmSele
            
        if not self.coordsIn and hasattr(parent, "coordsIn"):
            self.coordsIn = parent.coordsIn
            
        if not self.coordsOut and hasattr(parent, "coordsOut"):
            self.coordsOut = parent.coordsOut
            
        if not self.method and hasattr(parent, "method"):
            self.method = parent.method
            
        if not self.charge and hasattr(parent, "charge"):
            self.charge = parent.charge
            
        if not self.fDynamoPath and hasattr(parent, "fDynamoPath"):
            self.fDynamoPath = parent.fDynamoPath
            
        if not self.forceField and hasattr(parent, "forceField"):
            self.forceField = parent.forceField
            
        if not self.flexiblePart and hasattr(parent, "flexiblePart"):
            self.flexiblePart = parent.flexiblePart
            
        if not self.sequence and hasattr(parent, "sequence"):
            self.sequence = parent.sequence
        
        if self.getCoordsFromParent:
            if self.anotherCoordsSource:
                copyfile(join(parent.path, self.anotherCoordsSource), join(self.path, self.coordsIn))
            else:
                copyfile(join(parent.path, parent.coordsOut), join(self.path, self.coordsIn))
                
            copyfile(join(parent.path, parent.forceField), join(self.path, self.forceField))
            copyfile(join(parent.path, parent.flexiblePart), join(self.path, self.flexiblePart))
            copyfile(join(parent.path, parent.sequence), join(self.path, self.sequence))
        
        if self.slurmFile:
            if isfile(join(self.path, self.slurmFile )):
                print("Using existing slurmFile: ", self.slurmFile)
            else:
                print("Generating slurmFile")
                self.writeSlurmScript("run.slurm", self.processors, self.time)
        else:
            print("Generating slurmFile")
            self.writeSlurmScript("run.slurm", self.processors, self.time)
        
        self.generateInput()
        self.compileInput()
        
    def compileInput(self):
        lastDir = getcwd()
        
        chdir(self.path)
        
        system("make -f "+self.fDynamoPath + " SRC="+self.inputFile)
        
        chdir(lastDir)
        
    def readInitialCoord(self):
        atoms = atomsFromAtomSelection( self.additionalKeywords["definedAtoms"] )
        getCoords( join(self.path, self.coordsIn), atoms)
        
        return dist(atoms[0], atoms[1]) - dist(atoms[1], atoms[2])
        
    def generateInput(self):
        templateDir = expanduser("~/jobManagerPro/fDYNAMO")
        files2process = self.templateDict[ self.templateKey ]
        
        self.inputFile = files2process[0]
        file2copy = files2process[1:]
        
        for f2copy in file2copy:
            copyfile(join(templateDir, f2copy), join(self.path, f2copy))
            
        inputTemplateFile = open(join(templateDir, self.inputFile), 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        if "coordScanStart" in self.additionalKeywords and self.readInitialScanCoord:
            self.additionalKeywords["coordScanStart"] = self.readInitialCoord()
        
        formatDict = { "forcefield" : self.forceField, "sequence" : self.sequence,
                      "coordsIn" : self.coordsIn, "coordsOut" : self.coordsOut ,
                      "method" : self.method, "charge" : self.charge,
                      "qmSele" : self.qmSele, "flexiblePart" : self.flexiblePart}
        
        formatDict.update(self.additionalKeywords)
        
        inputText = inputTemplate.format( **formatDict )
        
        inputF = open(join(self.path, self.inputFile), 'w')
        inputF.write(inputText)
        inputF.close()
            
    def shouldBeRestarted(self):
        slurmOk, comment = self.verifySlurm()
        
        if "DUE TO TIME LIMIT" in comment:
            return True
        
        return False
#        logFile = join(self.path, self.logFile)
#        if not isfile(logFile):
#            return False
#        
#        lf = open(logFile, 'r')
#        
#        restartThisJob = False
#        
#        line = lf.readline()
#        
#        while line:
#            if "New curvilinear step not converged." in line:
#                restartThisJob = True
#                break
#            elif "FormBX had a problem." in line:
#                restartThisJob = True
#                break
#            
#            line = lf.readline()
#        
#        lf.close()
#        
#        return restartThisJob