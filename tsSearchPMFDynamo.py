#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:07:14 2019

@author: michal
"""

import networkx as nx
from os import getcwd, makedirs
from os.path import join, isdir, basename
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from graphManager import GraphManager
import sys
from glob import glob
from shutil import copyfile
#from crdParser import getCoords, dist, atomsFromAtomSelection
def rewriteFlexibleSeleFile( original ):
    inF = open(original, 'r')
    line = inF.readline().upper()
    
    corrected = ""
    
    if "MY_SELE_QMNB" in line:
        corrected = original
    else:
        corrected = original.replace(".f90", "_qmnb.f90")
        
        cF = open(corrected, 'w')
        cF.write( line.replace("MY_SELE(" , "MY_SELE_QMNB(") )
        
        line = inF.readline()
        while line:
            cF.write(line)
            line = inF.readline()
    
    inF.close()
    
    return corrected

def generateTSsearchDynamoPMF(compFile, onlyPrepare, onlyRun, runDFT):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    rootDir = currentDir
    data = parseFDynamoCompileScript(compFile)

    ########## INITIAL SCAN ###########################
    definedAtoms = data["definedAtoms"]
    constraints = data["constraints"]
    newNode = FDynamoNode(data["inputFile"], currentDir)
    newNode.coordsIn = data["coordsIn"]
    newNode.verification = [ "scan1D" ]
    newNode.slurmFile = None
    newNode.autorestart = False
    newNode.readInitialScanCoord = True
#    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.forceField = data["forceField"]
    newNode.flexiblePart = data["flexiblePart"]
    newNode.sequence = data["sequence"]
    newNode.qmSele = data["qmSele"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.fDynamoPath = data["fDynamoPath"]
    newNode.charge = data["charge"]
    newNode.method = data["method"]
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" ,
         "iterNo" : "80", "definedAtoms" : definedAtoms, "constraints" : constraints }
    
    if not onlyRun:
        jobGraph.add_node( currentDir , data = newNode )
        newNode.generateInput()
        # newNode.compileInput()
    
    ################## TS SEARCH #####################################
    startDir, currentDir = currentDir, join(currentDir, "ts_search")
    newNode = FDynamoNode("tsSearch.f90", currentDir)
    newNode.verification = ["Opt" , "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "true" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    if not onlyRun:
        jobGraph.add_node(currentDir, data = newNode)
        jobGraph.add_edge(startDir, currentDir)
    
    tsFoundDir = currentDir

    if runDFT:
        gaussianFlexibleSele = rewriteFlexibleSeleFile(  join(rootDir, data["flexiblePart"]) )
        tsGaussianDir = join(tsFoundDir, "b3lyp")

        if not isdir(tsGaussianDir):
            makedirs(tsGaussianDir)

        newNode = FDynamoNode("tsSearch", tsGaussianDir)
        newNode.verification = ["Opt" , "Freq"]
        newNode.noOfExcpectedImaginaryFrequetions = 1
        newNode.templateKey = "QMMM_opt_gaussian"
        newNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
        newNode.additionalKeywords =  { "ts_search" : "true", "method" : "B3LYP", "basis" : "6-31G(d,p)" , "multiplicity" : 1, "otherOptions" : "" }
        newNode.coordsIn = "coordsStart.crd"
        newNode.coordsOut = "coordsDone.crd"
        newNode.flexiblePart = basename(gaussianFlexibleSele)
        newNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        copyfile( gaussianFlexibleSele, join(tsGaussianDir, newNode.flexiblePart) )
        newNode.processors = 24
        newNode.time = "30:00:00"
        newNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(tsGaussianDir, data = newNode)
        jobGraph.add_edge( tsFoundDir, tsGaussianDir )

        spDir = join(tsGaussianDir, "SP")
        dftNode = FDynamoNode("DFT-SP-", spDir)
        dftNode.verification = ["SP"]
        dftNode.templateKey = "QMMM_sp_gaussian"
        dftNode.additionalKeywords =  {  "method" : "B3LYP", "basis" : "6-311++G(2d,2p)" , "multiplicity" : 1, "otherOptions" : ""   }
        dftNode.coordsIn = "coordsStart.crd"
        dftNode.coordsOut = "coordsDone.crd"
        dftNode.flexiblePart = basename(gaussianFlexibleSele)
        dftNode.processors = 24
        dftNode.time = "30:00:00"
        dftNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        dftNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(spDir, data = dftNode)
        jobGraph.add_edge(tsGaussianDir, spDir)



    
    newDir = join(currentDir, "irc_reverse")
    newNode = FDynamoNode("irc_reverse.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "-1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    if not onlyRun:
        jobGraph.add_node(newDir, data = newNode)
        jobGraph.add_edge(currentDir, newDir)
    
    optDir = join(newDir, "opt")
    
    newNode = FDynamoNode("opt.f90", optDir)
    newNode.verification = ["Opt", "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 0
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "false" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    if not onlyRun:
        jobGraph.add_node(optDir, data = newNode)
        jobGraph.add_edge( newDir, optDir)

    if runDFT:
        tsGaussianDir = join(optDir, "b3lyp")

        if not isdir(tsGaussianDir):
            makedirs(tsGaussianDir)

        newNode = FDynamoNode("opt", tsGaussianDir)
        newNode.verification = ["Opt" , "Freq"]
        newNode.noOfExcpectedImaginaryFrequetions = 0
        newNode.templateKey = "QMMM_opt_gaussian"
        newNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
        newNode.additionalKeywords =  { "ts_search" : "false", "method" : "B3LYP", "basis" : "6-31G(d,p)" , "multiplicity" : 1, "otherOptions" : "" }
        newNode.coordsIn = "coordsStart.crd"
        newNode.coordsOut = "coordsDone.crd"
        newNode.flexiblePart = basename(gaussianFlexibleSele)
        copyfile( gaussianFlexibleSele, join(tsGaussianDir, newNode.flexiblePart) )
        newNode.processors = 24
        newNode.time = "30:00:00"
        newNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        newNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(tsGaussianDir, data = newNode)
        jobGraph.add_edge( optDir, tsGaussianDir )

        spDir = join(tsGaussianDir, "SP")
        dftNode = FDynamoNode("DFT-SP-", spDir)
        dftNode.verification = ["SP"]
        dftNode.templateKey = "QMMM_sp_gaussian"
        dftNode.additionalKeywords =  {  "method" : "B3LYP", "basis" : "6-311++G(2d,2p)" , "multiplicity" : 1 , "otherOptions" : ""  }
        dftNode.coordsIn = "coordsStart.crd"
        dftNode.coordsOut = "coordsDone.crd"
        dftNode.flexiblePart = basename(gaussianFlexibleSele)
        dftNode.processors = 24
        dftNode.time = "30:00:00"
        dftNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        dftNode.moduleAddLines ="module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(spDir, data = dftNode)
        jobGraph.add_edge(tsGaussianDir, spDir)
    
    newDir = join(currentDir, "irc_forward")
    newNode = FDynamoNode("irc_forward.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    if not onlyRun:
        jobGraph.add_node(newDir, data = newNode)
        jobGraph.add_edge(currentDir, newDir)
    
    optDir = join(newDir, "opt")
    
    newNode = FDynamoNode("opt.f90", optDir)
    newNode.verification = ["Opt", "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 0
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "false" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    if not onlyRun:
        jobGraph.add_node(optDir, data = newNode)
        jobGraph.add_edge( newDir, optDir)

    if runDFT:
        tsGaussianDir = join(optDir, "b3lyp")

        if not isdir(tsGaussianDir):
            makedirs(tsGaussianDir)

        newNode = FDynamoNode("opt", tsGaussianDir)
        newNode.verification = ["Opt" , "Freq"]
        newNode.noOfExcpectedImaginaryFrequetions = 0
        newNode.templateKey = "QMMM_opt_gaussian"
        newNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
        newNode.additionalKeywords =  { "ts_search" : "false", "method" : "B3LYP", "basis" : "6-31G(d,p)" , "multiplicity" : 1 , "otherOptions" : ""}
        newNode.coordsIn = "coordsStart.crd"
        newNode.coordsOut = "coordsDone.crd"
        newNode.flexiblePart = basename(gaussianFlexibleSele)
        copyfile( gaussianFlexibleSele, join(tsGaussianDir, newNode.flexiblePart) )
        newNode.processors = 24
        newNode.time = "30:00:00"
        newNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        newNode.moduleAddLines ="module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(tsGaussianDir, data = newNode)
        jobGraph.add_edge( optDir, tsGaussianDir )

        spDir = join(tsGaussianDir, "SP")
        dftNode = FDynamoNode("DFT-SP-", spDir)
        dftNode.verification = ["SP"]
        dftNode.templateKey = "QMMM_sp_gaussian"
        dftNode.additionalKeywords =  {  "method" : "B3LYP", "basis" : "6-311++G(2d,2p)" , "multiplicity" : 1, "otherOptions" : ""   }
        dftNode.coordsIn = "coordsStart.crd"
        dftNode.coordsOut = "coordsDone.crd"
        dftNode.flexiblePart = basename(gaussianFlexibleSele)
        dftNode.processors = 24
        dftNode.time = "30:00:00"
        dftNode.partition = "plgrid-gpu\n#SBATCH --gres=gpu:1\n#SBATCH -A plgksdhphdgpu"
        dftNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"

        jobGraph.add_node(spDir, data = dftNode)
        jobGraph.add_edge(tsGaussianDir, spDir)
    
    ####################### SCAN FROM TS #########################
    
    scanSteps = 40

    reverseScan = join(startDir, "TS1reverseScan")
    
    newNode = FDynamoNode("scan.f90", reverseScan)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" ,
         "iterNo" : str(scanSteps), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(reverseScan, data = newNode)
    if onlyRun:
        newNode.forceField = data["forceField"]
        newNode.flexiblePart = data["flexiblePart"]
        newNode.sequence = data["sequence"]
        newNode.qmSele = data["qmSele"]
        newNode.templateKey = "QMMM_scan1D_mopac"
        newNode.fDynamoPath = data["fDynamoPath"]
        newNode.charge = data["charge"]
        newNode.method = data["method"]

        newNode.status = "examined"
    else:
        jobGraph.add_edge( tsFoundDir, reverseScan)
    
    if not onlyPrepare:
        pmfDir = join( startDir, "PMF" )
        for i in range(scanSteps+1):
            stepDir = join(pmfDir, "pmfRev"+str(i))
            
            newNode = FDynamoNode("pmfStep.f90", stepDir)
            newNode.verification = ["SP"]
            newNode.partition = "plgrid"
            newNode.time = "72:00:00"
            newNode.templateKey = "QMMM_pmf"
            newNode.readInitialScanCoord = True
            newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints}
            newNode.coordsIn = "seed.-"+str(i)
            newNode.anotherCoordsSource = "seed.-"+str(i)
            
            jobGraph.add_node(stepDir, data = newNode)
            jobGraph.add_edge( reverseScan, stepDir)
        
    forwardScan = join(startDir, "TS1forwardScan")
    
    newNode = FDynamoNode("scan.f90", forwardScan)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" ,
         "iterNo" : str(scanSteps), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(forwardScan, data = newNode)

    if onlyRun:
        newNode.forceField = data["forceField"]
        newNode.flexiblePart = data["flexiblePart"]
        newNode.sequence = data["sequence"]
        newNode.qmSele = data["qmSele"]
        newNode.templateKey = "QMMM_scan1D_mopac"
        newNode.fDynamoPath = data["fDynamoPath"]
        newNode.charge = data["charge"]
        newNode.method = data["method"]

        newNode.status = "examined"
    else:
        jobGraph.add_edge( tsFoundDir, forwardScan)
    
    if not onlyPrepare:
        for i in range(1,scanSteps+1):
            stepDir = join(pmfDir, "pmfForw"+str(i))
            
            newNode = FDynamoNode("pmfStep.f90", stepDir)
            newNode.verification = ["SP"]
            newNode.partition = "plgrid"
            newNode.time = "72:00:00"
            newNode.templateKey = "QMMM_pmf"
            newNode.readInitialScanCoord = True
            newNode.anotherCoordsSource = "seed.+"+str(i)
            newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints}
            newNode.coordsIn = "seed.+"+str(i)
            
            jobGraph.add_node(stepDir, data = newNode)
            jobGraph.add_edge( forwardScan, stepDir)
    
    
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: initTSsearchDynamoPMF compileScanScript.sh [ state: normal(default), onlyPrepare, onlyRun ] [ DFT: true, false(default) ]")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        onlyPrepare = False
        onlyRun = False
        runDFT = False
        if len(sys.argv) > 2:
            if sys.argv[2].upper() == "ONLYRUN":
                onlyRun = True
            elif sys.argv[2].upper() == "ONLYPREPARE":
                onlyPrepare = True

        if len(sys.argv) > 3:
            if sys.argv[3].upper() == "TRUE":
                runDFT = True
            elif sys.argv[3].upper() == "FALSE":
                runDFT = True
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchDynamoPMF(compFile, onlyPrepare, onlyRun, runDFT)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")