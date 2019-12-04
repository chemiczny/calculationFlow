#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:57:10 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from graphManager import GraphManager
import sys

def generateTSsearchDynamo(compFile):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    data = parseFDynamoCompileScript(compFile)
    
    newNode = FDynamoNode(data["inputFile"], currentDir)
    newNode.coordsIn = data["coordsIn"]
    newNode.coordsOut = data["coordsOut"]
    newNode.verification = [ "Opt" , "Freq" ]
    newNode.slurmFile = None
    newNode.autorestart = False
    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.forceField = data["forceField"]
    newNode.flexiblePart = data["flexiblePart"]
    newNode.sequence = data["sequence"]
    newNode.qmSele = data["qmSele"]
    newNode.fDynamoPath = data["fDynamoPath"]
    newNode.charge = data["charge"]
    newNode.method = data["method"]
    newNode.additionalKeywords = { "ts_search" : "true" }
    
    jobGraph.add_node( currentDir , data = newNode )
    newNode.compileInput()
    
    return buildTSsearchGraphDynamo(jobGraph, currentDir )
    
def buildTSsearchGraphDynamo( jobGraph, currentDir):
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
    
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: initTSsearchDynamo compileScript.sh")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchDynamo(compFile)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")

