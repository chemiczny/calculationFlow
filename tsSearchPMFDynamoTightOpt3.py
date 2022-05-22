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
from whamNode import WhamNode
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

def generateTSsearchDynamoPMF(compFile):
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
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "1.0",
         "iterNo" : "80", "definedAtoms" : definedAtoms, "constraints" : constraints }
    
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
    
    jobGraph.add_node(currentDir, data = newNode)
    jobGraph.add_edge(startDir, currentDir)
    
    tsFoundDir = currentDir

    stepOptDir = join(currentDir, "tsTightOpt")

    newNode = FDynamoNode("optStep.f90", stepOptDir)
    newNode.verification = ["Opt"]
    newNode.partition = "plgrid-short"
    newNode.time = "1:00:00"
    newNode.templateKey = "QMMM_opt_mopac_no_hess_restr"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "gradientTolerance" : "0.1"}

    jobGraph.add_node(stepOptDir, data = newNode)
    jobGraph.add_edge( tsFoundDir, stepOptDir)

    
    newDir = join(currentDir, "irc_reverse")
    newNode = FDynamoNode("irc_reverse.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "-1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
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
    
    jobGraph.add_node(optDir, data = newNode)
    jobGraph.add_edge( newDir, optDir)


    
    newDir = join(currentDir, "irc_forward")
    newNode = FDynamoNode("irc_forward.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
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
    
    jobGraph.add_node(optDir, data = newNode)
    jobGraph.add_edge( newDir, optDir)

    
    pmfDir = join( startDir, "PMF" )
    reverseI = 0
    forwardI = 0

    whamDir = join(pmfDir, "wham")
    whamN = WhamNode("wham.py", whamDir, "../*/pmf.dat")
    jobGraph.add_node(whamDir, data = whamN)

    ####################### SCAN FROM TS #########################

    reverseScan = join(startDir, "TS1reverseScan1")
    
    newNode = FDynamoNode("scan.f90", reverseScan)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(15), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "seed.-15"
    
    jobGraph.add_node(reverseScan, data = newNode)
    jobGraph.add_edge( stepOptDir, reverseScan)


    for i in range(15+1):
        stepDir = join(pmfDir, "pmfRev"+str(reverseI))
        reverseI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.-"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( reverseScan, stepDir)

        jobGraph.add_edge(stepDir, whamDir)
    
    reverseScan2 = join(startDir, "TS1reverseScan2")
    
    newNode = FDynamoNode("scan.f90", reverseScan2)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(16), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "seed.-16"
    
    jobGraph.add_node(reverseScan2, data = newNode)
    jobGraph.add_edge( reverseScan, reverseScan2)

    for i in range(1,16+1):
        stepDir = join(pmfDir, "pmfRev"+str(reverseI))
        reverseI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.-"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( reverseScan2, stepDir)

        jobGraph.add_edge(stepDir, whamDir)

    reverseScan3 = join(startDir, "TS1reverseScan3")
    
    newNode = FDynamoNode("scan.f90", reverseScan3)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(11), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(reverseScan3, data = newNode)
    jobGraph.add_edge( reverseScan2, reverseScan3)

    for i in range(1,11+1):
        stepDir = join(pmfDir, "pmfRev"+str(reverseI))
        reverseI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.-"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( reverseScan3, stepDir)

        jobGraph.add_edge(stepDir, whamDir)
        
    forwardScan = join(startDir, "TS1forwardScan1")
    
    newNode = FDynamoNode("scan.f90", forwardScan)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(15), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "seed.+15"
    
    jobGraph.add_node(forwardScan, data = newNode)
    jobGraph.add_edge( stepOptDir, forwardScan)

    for i in range(1, 15+1):
        stepDir = join(pmfDir, "pmfForw"+str(forwardI))
        forwardI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.+"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( forwardScan, stepDir)

        jobGraph.add_edge(stepDir, whamDir)
    
    forwardScan2 = join(startDir, "TS1forwardScan2")
    
    newNode = FDynamoNode("scan.f90", forwardScan2)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(16), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "seed.+16"
    
    jobGraph.add_node(forwardScan2, data = newNode)
    jobGraph.add_edge( forwardScan, forwardScan2)

    for i in range(1, 16+1):
        stepDir = join(pmfDir, "pmfForw"+str(forwardI))
        forwardI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.+"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( forwardScan2, stepDir)

        jobGraph.add_edge(stepDir, whamDir)

    forwardScan3 = join(startDir, "TS1forwardScan3")
    
    newNode = FDynamoNode("scan.f90", forwardScan3)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
         "iterNo" : str(11), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(forwardScan3, data = newNode)
    jobGraph.add_edge( forwardScan2, forwardScan3)

    for i in range(1, 11+1):
        stepDir = join(pmfDir, "pmfForw"+str(forwardI))
        forwardI += 1
        
        newNode = FDynamoNode("pmfStep.f90", stepDir)
        newNode.verification = ["SP"]
        newNode.partition = "plgrid"
        newNode.time = "72:00:00"
        newNode.templateKey = "QMMM_pmf"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "pmfSteps" : 40000}
        newNode.anotherCoordsSource = "seed.+"+str(i)
        newNode.coordsIn = "seed.crd"
        
        jobGraph.add_node(stepDir, data = newNode)
        jobGraph.add_edge( forwardScan3, stepDir)

        jobGraph.add_edge(stepDir, whamDir)
    
    
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: initTSsearchDynamoPMF compileScanScript.sh ")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchDynamoPMF(compFile)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")