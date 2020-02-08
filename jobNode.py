#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:08:06 2019

@author: michal
"""
from os import getcwd, chdir
from sbatchPy import SbatchManager
from os.path import join, isfile, expanduser
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
        self.autorestart = False
        self.distances2measure = []
        self.measuredDistances = {}
        
        self.moduleAddLines = ""
        
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
            self.writeSlurmScript("run.slurm")
            
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
    
    def generateFromParents(self, graph, parents):
        bestParent = None
        highestEnergy = None
        
        for p in parents:
            parentData = graph.nodes[p]["data"]
            if not parentData.valueForSorting:
                oldReadingValue = parentData.readResults
                parentData.readResults = True
                
                parentData.analyseLog()
                parentData.readResults = oldReadingValue
                if not parentData.valueForSorting:
                    continue
                
            if not bestParent:
                bestParent = p
                highestEnergy = parentData.valueForSorting
                
            elif parentData.valueForSorting > highestEnergy:
                bestParent = p
                highestEnergy = parentData.valueForSorting
        
        print("generate from parent: ")
        print(graph.nodes[bestParent]["data"].logFile)
        
        self.generateFromParent(graph.nodes[bestParent]["data"])
        
    def generateFromParent(self, parent):
        pass
    
#    def restart(self):
#        pass
    
#    def generateSlurmFile(self):
#        pass
    
        
        