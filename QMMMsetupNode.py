from jobNode import JobNode
from os.path import join, isfile, abspath, basename, dirname, expanduser
from os import getcwd
import networkx as nx
from shutil import copyfile
import sys

class QMMMsetupNode(JobNode):
    def __init__(self, inputFile, path, topology, coordinates):
        JobNode.__init__(self,inputFile, path)
        self.topology = topology
        self.coordsIn = coordinates
        self.partition = "plgrid-short"
        self.time = "0:15:00"

        self.coordsOut = "test.crd"
        self.flexiblePart = "in20.f90"
        self.sequence = "test.seq"

        
    def generateFromParent(self, parentData):
        copyfile( join(parentData.path, parentData.topology), join(self.path, self.topology) )
        copyfile( join(parentData.path, parentData.coordsOut), join(self.path, self.coordsIn) )
        
        self.generateSrcipts()
        self.writeSlurmScript("run.slurm")
    
    def generateSrcipts(self):
        tclTemplateDir = expanduser("~/jobManagerPro/tcl")
        ecmbTemplateDir = expanduser("~/jobManagerPro/ecmb")

        copyfile( join( tclTemplateDir, "saveCRD.tcl" ), join(self.path, "saveCRD.tcl") )
        copyfile( join(ecmbTemplateDir, "ecmb.py"), join(self.path, "ecmb.py") )
        copyfile( join(ecmbTemplateDir, "in20.py"), join(self.path, "in20.py")  )
    
    
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


        slurmFile.write("module load test/vmd/1.9.4a37\n")
            
        slurmFile.write("vmd -dispdev text -e saveCRD.tcl\n")
        slurmFile.write("python in20.py\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        if not isfile( join( self.path, "test.crd" ) ):
            print("Files not generated!")
            return False

        return True

    def analyseLog(self):
    	pass