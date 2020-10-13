#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:07:14 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from graphManager import GraphManager
import sys
#from crdParser import getCoords, dist, atomsFromAtomSelection

def generateTSsearchDynamoPMF(compFile, onlyPrepare):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
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
         "iterNo" : "70", "definedAtoms" : definedAtoms, "constraints" : constraints }
    
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
    
    ####################### SCAN FROM TS #########################
    
    scanSteps = 40
    
    reverseScan = join(startDir, "TS1reverseScan")
    
    newNode = FDynamoNode("scan.f90", reverseScan)
    newNode.verification = ["scan1D"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" ,
         "iterNo" : str(scanSteps), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(reverseScan, data = newNode)
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
    newNode.verification = ["scan1D"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.readInitialScanCoord = True
    newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" ,
         "iterNo" : str(scanSteps), "definedAtoms" : definedAtoms,  "constraints" : constraints}
    newNode.coordsIn = "coordsStart.crd"
    
    jobGraph.add_node(forwardScan, data = newNode)
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
        print("Usage: initTSsearchDynamoPMF compileScanScript.sh [ only prepare for PMF, default False ]")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        onlyPrepare = False
        if len(sys.argv) > 2:
            onlyPrepare = True
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchDynamoPMF(compFile, onlyPrepare)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")