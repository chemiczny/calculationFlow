#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 15:01:57 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
import sys
from graphManager import GraphManager
from graphGenerators import addSPcorrections

    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphs slurmFile")
    elif len(sys.argv) == 2:
        slurmFile = sys.argv[1]
        currentDir = getcwd()
        gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
        gaussianLog = gaussianFile.replace("inp", "log")
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            jobGraph = nx.DiGraph()
            newNode = GaussianNode(gaussianLog, currentDir)
            newNode.status = "finished"
            jobGraph.add_node( currentDir , data = newNode )
            
            addSPcorrections(jobGraph, currentDir)
    
            
            result = sm.addGraph(jobGraph, currentDir)
            if result:
                sm.buildGraphDirectories(jobGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            addSPcorrections(graph, currentDir)
            sm.buildGraphDirectories(graph)
            sm.saveGraphs()
            print("Added nodes to existing graph")
            
        
    else:
        print( "cooooo?")