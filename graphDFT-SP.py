#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 10:51:40 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
import sys
from graphManager import GraphManager

def addManySPcorrections(graph, node):
    functionals = [ "BLYP", "B3LYP", "BP86"  ] 
    functionals +=[ "M05", "M052X", "M06L", "M06", "M062X" ]
    functionals +=[ "TPSSTPSS" , "PBEPBE" ]
    
    for functional in functionals:
        newDir = join(node, functional)
        newNode = GaussianNode("sp.inp", newDir)
        newNode.routeSection = """%Chk=checkp.chk
%Nproc=6
#P """+functional+"""/6-31G(d,p)
# nosymm Population(Hirshfeld)
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
        newNode.verification = "SP"
        newNode.readResults = True
        newNode.processors = 6
        newNode.time = "72:00:00"
        graph.add_node(newDir, data = newNode)
        graph.add_edge(node, newDir)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphDFT-SP slurmFile/nodeKey")
    elif len(sys.argv) == 2:
        slurmFile = sys.argv[1]
        currentDir = getcwd()
        gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
        gaussianLog = gaussianFile.replace("inp", "log")
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            jobGraph = nx.DiGraph()
            newNode = GaussianNode(gaussianFile, currentDir)
            newNode.slurmFile = slurmFile
            newNode.status = "finished"
            jobGraph.add_node( currentDir , data = newNode )
            
            addManySPcorrections(jobGraph, currentDir)
    
            
            result = sm.addGraph(jobGraph, currentDir)
            if result:
                sm.buildGraphDirectories(jobGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            addManySPcorrections(graph, currentDir)
            sm.buildGraphDirectories(graph)
            sm.saveGraphs()
            print("Added nodes to existing graph")
            
            