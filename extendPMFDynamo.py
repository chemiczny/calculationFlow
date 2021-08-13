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

def extendDynamoPMF(compFile, jobGraph, currentDir):
    startDir = currentDir
    data = parseFDynamoCompileScript(compFile)

    definedAtoms = data["definedAtoms"]
    constraints = data["constraints"]
    
    ####################### SCAN FROM TS #########################
    
    scanSteps = 40

    reverseScan = join(startDir, "TS1reverseScan")
    forwardScan = join(startDir, "TS1forwardScan")

    pmfDir = join( startDir, "PMF" )

    if not reverseScan in jobGraph.nodes:
        print("Cannot find directory:")
        print(reverseScan)
        return jobGraph

    if not forwardScan in jobGraph.nodes:
        print("Cannot find directory:")
        print(forwardScan)
        return jobGraph


    for crd in glob( join( reverseScan, "seed.-*" ) ):
        if "pdb" in crd:
            continue

        i = int( basename(crd).replace( "seed.-", "" ) )
        stepDir = join(pmfDir, "pmfRev"+str(i))

        if stepDir in jobGraph.nodes:
            continue
        else:
            print("New PMF step: ", stepDir)
        
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
        
    
    for crd in glob( join( forwardScan, "seed.+*" ) ):
        if "pdb" in crd:
            continue

        i = int( basename(crd).replace( "seed.+", "" ) )
        if i == 0:
            continue

        stepDir = join(pmfDir, "pmfForw"+str(i))

        if stepDir in jobGraph.nodes:
            continue
        else:
            print("New PMF step: ", stepDir)
        
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
        print("Usage: expandDynamoPMF compileScanScript.sh")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if graph:
            newGraph = extendDynamoPMF(compFile, graph, currentDir)
    
            
            sm.buildGraphDirectories(newGraph)
            sm.saveGraphs()
            print("Created new graph")
        else:
            print("No graph found in this directory directory")