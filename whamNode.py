from networkx.algorithms.isomorphism import GraphMatcher
import numpy as np
import math
from jobNode import JobNode
from os.path import join, isfile, abspath, basename, dirname, expanduser
from os import getcwd
import networkx as nx
from shutil import copyfile
import sys


class WhamNode(JobNode):
    def __init__(self, inputFile, path, pmfOutputs):
        JobNode.__init__(self,inputFile, path)
        self.pmfOutputs = pmfOutputs
        self.time = "00:20:00"
        
    def generateFromParent(self, parentData):
        templateDir = expanduser("~/jobManagerPro/fDYNAMO")
        template = join( templateDir, "wham.py" )
        
        copyfile(template, join(self.path, "wham.py"))
        
        self.writeSlurmScript("run.slurm")

    def generateFromParents(self, graph, parentsData):
        self.generateFromParent(parentsData)
    
    
    def writeSlurmScript( self, filename):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --cpus-per-task=1\n")
        time = self.time

        timeRestrictions = True

        if timeRestrictions in slurmConfig:
            timeRestrictions = slurmConfig["timeRestrictions"]

        if timeRestrictions:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid-short\n\n")

            
            
        slurmFile.write("python wham.py "+self.pmfOutputs +" &> wham.log\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        if not isfile( join( self.path, "wham.log" ) ):
            print("Files not generated!")
            return False

        return True

    def analyseLog(self):
    	pass
        

    
    