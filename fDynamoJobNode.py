#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 15:17:36 2019

@author: michal
"""

from jobNode import JobNode
from os.path import join, isfile, expanduser
from shutil import copyfile, move
from os import getcwd, chdir, system, rename
from crdParser import getCoords, dist, atomsFromAtomSelection
import sys

class FDynamoNode(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
        self.logFile = "a.log"
        self.verification = []
        self.templateKey = ""
        self.additionalKeywords = {}
        
        self.templateDict = { "QMMM_opt_mopac" : [ "QMMM_opt.f90", "panadero.f90" ], 
                             "QMMM_opt_mopac_no_hess" : [ "QMMM_opt_noHess.f90" ] ,
                             "QMMM_opt_mopac_no_hess_restr" : [ "QMMM_opt_noHess_restr.f90" ] ,
                             "QMMM_irc_mopac" : [ "IRC.f90", "mep_project.f90" ] ,
                             "QMMM_scan1D_mopac" : [ "scan1D.f90" ],
                             "QMMM_pmf" : [ "pmf.f90" ] ,
                             "QMMM_pmf_restart" : [ "pmf_restart.f90" ],
                             "QMMM_sp" : [ "SP.f90" ], 
                             "QMMM_opt_gaussian" : [ "QMMM_opt_Gauss.f90", "panadero.f90", "keep_log", "with_gaussian.f90" ],
                             "QMMM_irc_gaussian" : [ "IRC_Gauss.f90" , "mep_project.f90", "keep_log", "with_gaussian.f90" ],
                             "QMMM_sp_gaussian" : [ "SP_Gauss.f90", "keep_log", "with_gaussian.f90"  ] }
        
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
        self.copyHessian = False
        self.copyVelocities = False
        self.readInitialScanCoord = False
        self.movePMFresults = False
        
        self.measureRCinOutput = False
        
        self.QMenergy = None
        self.PotentialEnergy = None
        self.parent_initial_rc = None
        
        self.moduleAddLines = ""
        
    def rebuild(self, inputFile, path, slurmFile):
        self.inputFile = inputFile
        self.path = path
        self.slurmFile = slurmFile
        self.getCoordsFromParent = True
        self.id = None
        self.results = []
        
    def analyseLog(self):
        # if not self.readResults:
        #     return
        
        if not isfile( join(self.path, self.logFile) ):
            print("File does not exists! ",join(self.path, self.logFile) )
            return

        lf = open(join(self.path, self.logFile))
        
        line = lf.readline()
        energy = ""
        
        while line:
            if "Potential Energy     =" in line:
                energy = line[:42]
                self.PotentialEnergy = float(line.split()[3])
                
            elif "QM Energy            =" in line:
                self.QMenergy = float( line.split()[3] )

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
        if "PMF_restart" in self.verification:
            res = res and self.verifyPMFrestart()

        if hasattr(self, "measureRCinOutput"):
            if self.measureRCinOutput:
                
                rc = self.measureRC( join(self.path, self.coordsOut))
                
                if rc < 0 :
                    copyfile( join(self.path, self.coordsOut), join(self.path, "RC_negative_" + self.coordsOut) )
                else:
                    copyfile( join(self.path, self.coordsOut), join(self.path, "RC_positive_" + self.coordsOut) )

        return res
    
    def verifyPMFrestart(self):
        if not isfile(join(self.path, "pmf_old.dat")):
            return True 

        # not execute this code twice
        if isfile(join(self.path, "pmf_fresh_part.dat")):
            return True 

        rename(join(self.path, "pmf.dat"), join(self.path, "pmf_fresh_part.dat"))

        with open(join(self.path, "pmf.dat"), 'w') as final_pmf:
            
            with open(join(self.path, "pmf_old.dat")) as pmf_part1:
                line = pmf_part1.readline()
                while line:
                    final_pmf.write(line)
                    line = pmf_part1.readline()

            with open(join(self.path, "pmf_fresh_part.dat")) as pmf_part1:
                line = pmf_part1.readline()
                line = pmf_part1.readline()
                while line:
                    final_pmf.write(line)
                    line = pmf_part1.readline()

        return True

    def measureRC(self, crdFile):
        if not "definedAtoms" in self.additionalKeywords:
            print("nie zdefiniowano atomow do RC!!!")
            
        atoms = atomsFromAtomSelection( self.additionalKeywords["definedAtoms"] )
        # print("Znaleziono: ", len(atoms), "atomow do wspolrzednej reakcji")
        getCoords( crdFile, atoms)
        
        if len(atoms) > 2:
            return  dist(atoms[0], atoms[1]) - dist(atoms[-1], atoms[-2])

        return  dist(atoms[0], atoms[1])
        
    def verifyScan1D(self):
        scanFile = join(self.path, "fort.900" )
        if not isfile(scanFile):
            print("There is no scan output data!")
            return False
            
        coordIndex = 0
        sf = open(scanFile, 'r')
        
        line = sf.readline()
        TSEnergy = float(line.split()[1])
        TSIndex = -1

        lastEnergy = TSEnergy

        TSEnergyCandidate = 0
        TSIndexCandidate = 0

        energyRisingPoints = 0
        energyRisingLimit = 2

        energyDecreasingPoints = 0
        energyDecreasinfLimit = 2

        state = "init"

        while line:
            
            energy = float(line.split()[1])

            if state == "init":
                #sprawdz czy energia rosnie monotonicznie przez jakis czas
                if energy > lastEnergy:
                    energyRisingPoints += 1
                else:
                    energyRisingPoints = 0

                if energy > lastEnergy and energyRisingPoints >= energyRisingLimit:
                    state = "beforeTS"
                    # print("init state eneded ", coordIndex)

                    
                #znajdz lokalne maksimum, pod warunkiem, ze jest najwieksze z dotychczas znalezionych
            elif state == "beforeTS":
                if energy < lastEnergy and lastEnergy > TSEnergy:
                    TSEnergyCandidate = lastEnergy
                    TSIndexCandidate = coordIndex - 1
                    energyDecreasingPoints = 1
                    state = "afterTS"

                    # print("TS candidate ", coordIndex-1)
                #zweryfikuj czy funkcja jest malejaca przez jakis czas
            elif state == "afterTS":
                if energy < lastEnergy:
                    energyDecreasingPoints += 1
                else:
                    energyDecreasingPoints = 0
                    energyRisingPoints = 1
                    state = "init"


                if energyDecreasingPoints >= energyDecreasinfLimit:
                    TSEnergy = TSEnergyCandidate
                    TSIndex = TSIndexCandidate
                    state = "init"

            
            line = sf.readline()
            coordIndex += 1
            lastEnergy = energy
        
        sf.close()
        
        coordsOut = ""
        
        if isfile( join(self.path, "seed.+"+str(TSIndex)) ):
            coordsOut = "seed.+"+str(TSIndex)
            
        elif isfile( join(self.path, "seed.-"+str(TSIndex)) ):
            coordsOut = "seed.-"+str(TSIndex)

        else:
            print("cannot find TS guess")
            return False
            
        self.coordsOut = coordsOut
        
        return True
    
    def verifySP(self):
        lf = open(join(self.path, self.logFile))
        
        result = False
        line = lf.readline()
        while line:
            
            if "CPU time used =" in line:
                # print("\tNormal termination of fDYNAMO")
                result = True
                # break

            if "Dynamics Results" in line:
                # print("\tNormal termination of fDYNAMO")
                result = True
                # break

            if "Data written to" in line:
                result = True

            if "Error in MOPAC_SCF:Excessive number of SCF iterations." in line:
            	print("\tfDYNAMO terminated abnormally: MOPAC error")
            	result = False
            
            line =lf.readline()
        
        lf.close()
        if not result:
            print("\tfDYNAMO terminated abnormally")
        else:
        	print("\tNormal termination of fDYNAMO")
        	
        return result
    
    def verifyOpt(self):
        lf = open(join(self.path, self.logFile))
        
        line = lf.readline()
        result=False
        while line:
            
            if "Baker Search Status:" in line or "Minimization Status:" in line:
                break
            
            line =lf.readline()
        else:
            lf.close()
            return result
        
        if "Gradient tolerance reached." in line:
            print(line.strip())
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
        timeRestrictions = False

        if "timeRestrictions" in slurmConfig:
            timeRestrictions = slurmConfig["timeRestrictions"].upper() == "TRUE"

        if timeRestrictions:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid\n\n")
            
#        if "additionalLines" in slurmConfig:
#            slurmFile.write(slurmConfig["additionalLines"]+"\n")
            
        if self.moduleAddLines:
            slurmFile.write(self.moduleAddLines+"\n\n")


        if "fDYNAMOcompilerModule" in slurmConfig:
            slurmFile.write("module load "+ slurmConfig["fDYNAMOcompilerModule"] + " \n\n")
            slurmFile.write("make -f "+self.fDynamoPath + " SRC="+self.inputFile+" &> build.log\n")
        # else:
        #     self.compileInput()
            
        
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

        if not isfile(join(self.path, self.forceField)):
            copyfile(join(parent.path, parent.forceField), join(self.path, self.forceField))
            
        if not self.flexiblePart and hasattr(parent, "flexiblePart"):
            self.flexiblePart = parent.flexiblePart
        if not isfile(join(self.path, self.flexiblePart)):
            copyfile(join(parent.path, parent.flexiblePart), join(self.path, self.flexiblePart))
            
        if not self.sequence and hasattr(parent, "sequence"):
            self.sequence = parent.sequence
        if not isfile( join(self.path, self.sequence) ):
            copyfile(join(parent.path, parent.sequence), join(self.path, self.sequence))
        
        if self.getCoordsFromParent:
            if self.anotherCoordsSource:
                copyfile(join(parent.path, self.anotherCoordsSource), join(self.path, self.coordsIn))
            else:
                copyfile(join(parent.path, parent.coordsOut), join(self.path, self.coordsIn))

        if self.copyVelocities:
            velocities_path = join(parent.path, "velocities.out")
            if isfile(velocities_path):
                copyfile(velocities_path, join(self.path, "velocities.in"))

        if self.movePMFresults:
            pmf_path = join(parent.path, "pmf.dat")
            if isfile(pmf_path):
                move(pmf_path, join(self.path, "pmf_old.dat"))


        if hasattr(parent, "additionalKeywords"):
            if "coordScanStart" in parent.additionalKeywords:
                self.parent_initial_rc = parent.additionalKeywords["coordScanStart"]
        #lol
        # if hasattr(self, "copyHessian"):
        #     if self.copyHessian:
        #         parentHessian = join(parent.path, "hessian.dump")
        #         if isfile(parentHessian):
        #             copyfile(parentHessian, join(self.path, "update.dump"))
                
        self.generateInput()
        
        if self.slurmFile:
            if isfile(join(self.path, self.slurmFile )):
                print("Using existing slurmFile: ", self.slurmFile)
            else:
                print("Generating slurmFile")
                self.writeSlurmScript("run.slurm", self.processors, self.time)
        else:
            print("Generating slurmFile")
            self.writeSlurmScript("run.slurm", self.processors, self.time)
        
        slurmConfig = self.readSlurmConfig()
        if not "fDYNAMOcompilerModule" in slurmConfig:
            self.compileInput()

       # self.compileInput()
        
    def compileInput(self):
        lastDir = getcwd()
        
        chdir(self.path)
        
        system("make -f "+self.fDynamoPath + " SRC="+self.inputFile)
        
        chdir(lastDir)

        compFile = join(self.path, "compile.sh")

        cf = open(compFile, 'w')
        cf.write("make -f "+self.fDynamoPath + " SRC="+self.inputFile+"\n")
        cf.close()
        
    def readInitialCoord(self):
        atoms = atomsFromAtomSelection( self.additionalKeywords["definedAtoms"] )
        getCoords( join(self.path, self.coordsIn), atoms)
        
        if len(atoms) > 2:
            return dist(atoms[0], atoms[1]) - dist(atoms[-2], atoms[-1])

        return dist(atoms[0], atoms[1])
        
    def generateInput(self):
        templateDir = join(sys.path[0], "fDYNAMO")
        files2process = self.templateDict[ self.templateKey ]
        
        self.inputFile = files2process[0]
        
        if "coordScanStart" in self.additionalKeywords and self.readInitialScanCoord:
            self.additionalKeywords["coordScanStart"] = self.readInitialCoord()
        elif "coordScanStart" in self.additionalKeywords:
            self.additionalKeywords["coordScanStart"] = self.parent_initial_rc
        
        formatDict = { "forcefield" : self.forceField, "sequence" : self.sequence,
                      "coordsIn" : self.coordsIn, "coordsOut" : self.coordsOut ,
                      "method" : self.method, "charge" : self.charge,
                      "qmSele" : self.qmSele, "flexiblePart" : self.flexiblePart}
        
        formatDict.update(self.additionalKeywords)

        if not "gradientTolerance" in formatDict:
            formatDict["gradientTolerance"] = "1.0"
        
        if not "ts_search" in formatDict:
            formatDict["ts_search"] = "true"
        
        for f2copy in files2process:
            print("Generating from template: ", f2copy)
            self.rewriteTemplate(join(templateDir, f2copy), join(self.path, f2copy), formatDict)
        
        
    def rewriteTemplate(self, template, destiny, formatDict):
        if isfile(destiny):
            print("Using existing file")
            return

        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **formatDict )
        
        inputF = open(destiny, 'w')
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