#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 19:41:50 2020

@author: michal
"""

from jobNode import JobNode
from os.path import join, expanduser, basename, isfile
from glob import glob
from shutil import copyfile
import sys

class AmberNode(JobNode):
    def __init__(self, inputFile, path, mdDirectory, topologyFile, coordinatesIn= None):
        JobNode.__init__(self,inputFile, path)
        
        self.time = None
        self.partition = None
        self.processors = 24
        self.mdDirectory = mdDirectory
        self.topology = topologyFile
        self.coordsIn = coordinatesIn
        self.coordsOut = None
        
        self.NoSolventResidues = None
        self.runType = None
        self.nsOfSimulation = None
        
        self.templateDict = { "standardOptimization" : "standardOptimization.slurm" , "standardHeating" : "standardHeating.slurm", 
            "standardMD" : "standardMD.slurm" ,"standardCooling" : "standardCooling.slurm" }
        
    def generateFromParent(self, parentData):
        if hasattr(parentData, "topology"):
            copyfile( join(parentData.path, parentData.topology), join(self.path, self.topology) )
        
        if self.coordsIn == None:
            self.coordsIn = "initial_rst.nc"

        if hasattr(parentData, "coordsOut"):
            if parentData.coordsOut != None:
                copyfile( join(parentData.path, parentData.coordsOut), join(self.path, self.coordsIn) )
        
        self.writeSlurmScript(self.inputFile)
    
    def setupStandardOptimization(self, scriptFile, template):
        replaceDict = { "topology" : self.topology, "coordsIn" : self.coordsIn, "noSolventNo" : self.NoSolventResidues }
        self.coordsOut = "min5_true_rst.nc"
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def setupStandardHeating(self, scriptFile, template):
        replaceDict = { "topology" : self.topology, "coordsIn" : self.coordsIn, "noSolventNo" : self.NoSolventResidues }
        self.coordsOut = "md_rst_0.nc"
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def setupStandardCooling(self, scriptFile, template):
        self.coordsOut = "cooled.nc"
        replaceDict = { "topology" : self.topology, "coordsIn" : self.coordsIn, "processors" : self.processors, "coordsOut" : self.coordsOut }
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        
        inputText = inputTemplate.format( **replaceDict )
        
        scriptFile.write(inputText)
    
    def setupStandardMD(self, scriptFile, template):
        mdFiles = list(glob( join(self.mdDirectory, "md_rst_*.nc") ))
        highestNs = 0
        for mdFile in mdFiles:
            nsNumber = int( basename(mdFile).replace("md_rst_", "").replace(".nc", "") )
            highestNs = max(highestNs, nsNumber)
        
        ns2run = list(range( highestNs, highestNs + self.nsOfSimulation ))
        ns2run = [ str(ns) for ns in ns2run]
        replaceDict = { "topology" : self.topology , "mdDir" : self.mdDirectory, "ns" : " ".join(ns2run) }
        
        inputTemplateFile = open(template, 'r')
        inputTemplate = inputTemplateFile.read()
        inputTemplateFile.close()
        # print("zczytane z szablonu:")
        # print(inputTemplate)
        inputText = inputTemplate.format( **replaceDict )
        # print("po uzupelnieniu:")
        # print(inputText)
        scriptFile.write(inputText)
    
    def writeSlurmScript( self, filename):
        # print("Writing new slurm file ...")
        fullPath = join(self.path, filename)
        # print(fullPath)
        self.slurmFile = filename
        if isfile(fullPath):
            print("Slurm file already exists! Not generating!")
            return
            
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()

        processors = str(self.processors)
        time = self.time
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --ntasks-per-node="+str(processors)+"\n")
                        
        timeRestrictions = True

        if timeRestrictions in slurmConfig:
            timeRestrictions = slurmConfig["timeRestrictions"]

        if timeRestrictions:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid\n\n")
            
        if "additionalLines" in slurmConfig:
            slurmFile.write(slurmConfig["additionalLines"]+"\n")
            
        slurmFile.write("module add plgrid/apps/amber/18\n")
            
        templateDir = join(sys.path[0], "amber")
        template = join( templateDir, self.templateDict[self.runType] )
        
        if self.runType == "standardOptimization":
            self.setupStandardOptimization(slurmFile, template)
        elif self.runType == "standardHeating":
            self.setupStandardHeating(slurmFile, template)
        elif self.runType == "standardMD":
            self.setupStandardMD(slurmFile, template)
        elif self.runType == "standardCooling":
            self.setupStandardCooling(slurmFile, template)
        else:
            raise Exception("not implemented")
        
        slurmFile.close()
        
        # self.slurmFile = filename
        
    def verifyLog(self):
        return True

    def analyseLog(self):
    	pass