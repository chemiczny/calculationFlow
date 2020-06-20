#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 19:41:50 2020

@author: michal
"""

from jobNode import JobNode
from os.path import join, expanduser, basename
from glob import glob
from shutil import copyfile

class AmberNode(JobNode):
    def __init__(self, inputFile, path, mdDirectory, topologyFile, coordinatesIn= None):
        JobNode.__init__(self,inputFile, path)
        
        self.time = None
        self.partition = None
        self.mdDirectory = mdDirectory
        self.topology = topologyFile
        self.coordinatesIn = coordinatesIn
        self.coordsOut = None
        
        self.NoSolventResidues = None
        self.runType = None
        self.nsOfSimulation = None
        
        self.templateDict = { "standardOptimization" : "standardOptimization.slurm" }
        
    def generateFromParent(self, parentData):
        copyfile( join(parentData.path, parentData.topology), join(self.path, self.topology) )
        
        if parentData.coordsOut != None:
            copyfile( join(parentData.path, parentData.coordsOut), join(self.path, self.coordsIn) )
        
        self.writeSlurmScript(self.inputFile)
    
    def setupStandardOptimization(self, scriptFile, template):
        replaceDict = { "topology" : self.topology, "coordsIn" : self.coordinatesIn, "noSolventNo" : self.NoSolventResidues }
        self.coordsOut = "min5_true.rst7"
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def setupStandardHeating(self, scriptFile, template):
        replaceDict = { "topology" : self.topology, "coordsIn" : self.coordinatesIn, "noSolventNo" : self.NoSolventResidues }
        self.coordsOut = "md0.rst7"
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def setupStandardCooling(self, scriptFile, template):
        pass
    
    def setupStandardMD(self, scriptFile, template):
        mdFiles = list(glob( join(self.mdDirectory, "md*.rst7") ))
        highestNs = 0
        for mdFile in mdFiles:
            nsNumber = int( basename(mdFile).replace("md", "").replace(".rst7", "") )
            highestNs = max(highestNs, nsNumber)
        
        ns2run = list(range( highestNs, highestNs + self.nsOfSimulation ))
        ns2run = [ str(ns) for ns in ns2run]
        replaceDict = { "topology" : self.topology , "mdDir" : self.mdDirectory, "ns" : " ".join(ns2run) }
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def writeSlurmScript( self, filename):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()

        processors = str(self.processors)
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
            
        slurmFile.write("module add plgrid/apps/amber/18\n")
            
        templateDir = expanduser("~/jobManagerPro/amber")
        template = join( templateDir, self.templateDict[self.runType] )
        
        if self.runType == "standardOptimization":
            self.setupStandardOptimization(slurmFile, template)
        elif self.runType == "standardHeating":
            self.setupStandardHeating(slurmFile, template)
        elif self.runType == "stardardMD":
            self.setupStandardMD(slurmFile, template)
        else:
            print("Not implemented")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        pass

    def analyseLog(self):
    	pass