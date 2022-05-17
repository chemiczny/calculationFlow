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

    scanLen = "73"

    ########## INITIAL SCAN ###########################
    definedAtoms = data["definedAtoms"]
    constraints = data["constraints"]
    newNode = FDynamoNode(data["inputFile"], currentDir)
    newNode.coordsIn = data["coordsIn"]
    newNode.coordsOut = "seed.+"+scanLen
    newNode.verification = [ "SP" ]
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
         "iterNo" : scanLen, "definedAtoms" : definedAtoms, "constraints" : constraints }
    
    jobGraph.add_node( currentDir , data = newNode )
    newNode.generateInput()
        # newNode.compileInput()
    
    iterNo = 7
    forwardScan = currentDir

    for i in range(iterNo):
        #initial opt i
        stepOptDir = join(rootDir, "optI_restr_"+str(i))

        newNode = FDynamoNode("optStep.f90", stepOptDir)
        newNode.verification = ["Opt"]
        newNode.partition = "plgrid-short"
        newNode.time = "1:00:00"
        newNode.templateKey = "QMMM_opt_mopac_no_hess_restr"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "gradientTolerance" : "0.1" }
        newNode.coordsIn = "coordsIn.crd"
        newNode.coordsOut = "coordsOut.crd"
        
        jobGraph.add_node(stepOptDir, data = newNode)
        jobGraph.add_edge( forwardScan, stepOptDir)

        #opt i

        iOptDir = join(rootDir, "optI_"+str(i))

        newNode = FDynamoNode("optStep.f90", iOptDir)
        newNode.verification = ["Opt"]
        newNode.partition = "plgrid-short"
        newNode.time = "1:00:00"
        newNode.templateKey = "QMMM_opt_mopac_no_hess"
        newNode.coordsIn = "coordsIn.crd"
        newNode.coordsOut = "coordsOut.crd"
        newNode.additionalKeywords = { "gradientTolerance" : "0.1"}
        
        jobGraph.add_node(iOptDir, data = newNode)
        jobGraph.add_edge( stepOptDir, iOptDir)


        #scan back

        reverseScan = join(rootDir, "reverseScan_"+str(i))
        
        newNode = FDynamoNode("scan.f90", reverseScan)
        newNode.verification = ["SP"]
        newNode.templateKey = "QMMM_scan1D_mopac"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "1.0",
             "iterNo" : scanLen, "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newNode.coordsIn = "coordsStart.crd"
        newNode.coordsOut = "seed.-"+scanLen
        
        jobGraph.add_node(reverseScan, data = newNode)
        jobGraph.add_edge( iOptDir, reverseScan)

        #initial opt s
        stepOptDir = join(rootDir, "optS_restr_"+str(i))

        newNode = FDynamoNode("optStep.f90", stepOptDir)
        newNode.verification = ["Opt"]
        newNode.partition = "plgrid-short"
        newNode.time = "1:00:00"
        newNode.templateKey = "QMMM_opt_mopac_no_hess_restr"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "gradientTolerance" : "0.1" }
        newNode.coordsIn = "coordsIn.crd"
        newNode.coordsOut = "coordsOut.crd"
        
        jobGraph.add_node(stepOptDir, data = newNode)
        jobGraph.add_edge( reverseScan, stepOptDir)

        #opt s

        sOptDir = join(rootDir, "optS_"+str(i))

        newNode = FDynamoNode("optStep.f90", sOptDir)
        newNode.verification = ["Opt"]
        newNode.partition = "plgrid-short"
        newNode.time = "1:00:00"
        newNode.templateKey = "QMMM_opt_mopac_no_hess"
        newNode.coordsIn = "coordsIn.crd"
        newNode.coordsOut = "coordsOut.crd"
        newNode.additionalKeywords = { "gradientTolerance" : "0.1"}
        
        jobGraph.add_node(sOptDir, data = newNode)
        jobGraph.add_edge( stepOptDir, sOptDir)

        if i == iterNo -1:
            break
        #scan to I

        forwardScan = join(rootDir, "forwardScan_"+str(i))
        
        newNode = FDynamoNode("scan.f90", forwardScan)
        newNode.verification = ["SP"]
        newNode.templateKey = "QMMM_scan1D_mopac"
        newNode.readInitialScanCoord = True
        newNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "1.0",
             "iterNo" : scanLen, "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newNode.coordsIn = "coordsStart.crd"
        newNode.coordsOut = "seed.+"+scanLen
        
        jobGraph.add_node(forwardScan, data = newNode)
        jobGraph.add_edge( sOptDir, forwardScan)

    
    
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