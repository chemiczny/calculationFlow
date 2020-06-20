#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 11:59:09 2020

@author: michal
"""

from jobNode import JobNode
from os.path import join, basename
from shutil import copyfile
from glob import glob

class CppTrajNode(JobNode):
    def __init__(self, inputFile, path, topologyFile, mdDir):
        JobNode.__init__(self,inputFile, path)
        self.topology = topologyFile
        self.mdDir = mdDir
        
    def generateFromParent(self, parentData):
        copyfile( join(parentData.path, parentData.topology), join(self.path, self.topology) )
        
        self.writeRmsdScript()
        self.writeSlurmScript(self.inputFile)
    
    def writeRmsdScript(self):
        rmsdFile = open( join(self.path, "rmsd.in"), 'w' )
        baseCoords = join( self.mdDir, "md0.rst7" )
        rmsdFile.write("trajin "+baseCoords + "\n")
        
        mdFiles = list(glob( join(self.mdDir, "md*.nc") ))
        ns2file = {}
        for mdFile in mdFiles:
            nsNumber = int( basename(mdFile).replace("md", "").replace(".nc", "") )
            ns2file[nsNumber] = join(self.mdDir, basename(mdFile))
            
            
        for ns in sorted(list(ns2file.keys())):
            rmsdFile.write("trajin "+ns2file[ns] + "\n")
        
        rmsdFile.write("strip :WAT\nstrip :Na+\nstrip :Cl-\n")
        rmsdFile.write("rms first rmsd.dat  @C,N,CA\n")
        
        rmsdFile.close()
    
    def writeSlurmScript( self, filename):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --ntasks-per-node=1\n")
                        
        if not slurmConfig:
            slurmFile.write("#SBATCH --time=1:00:00\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p {partition}\n\n".format(partition = self.partition))
            else:
                slurmFile.write("#SBATCH -p plgrid\n\n")


        slurmFile.write("module add plgrid/apps/amber/18\n")
            
            
        slurmFile.write("cpptraj -p "+self.topology+" -i rmsd.in > rmsd.log\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        return True

    def analyseLog(self):
    	pass