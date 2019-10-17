#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:31:34 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join, basename, dirname
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
from graphGenerators import addSPcorrections, addZPE
from graphManager import GraphManager
import sys

def generateTSsearchFromScan(slurmFiles):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    
    for slurmF in slurmFiles:
        path = dirname(slurmF)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: initTSsearchFromScan slurmFiles")
    elif len(sys.argv) >= 2:
        slurmFiles = sys.argv[1:]
        currentDir = getcwd()
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchFromScan(slurmFiles)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")
            
        