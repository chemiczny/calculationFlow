#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:31:34 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import  basename, dirname, abspath, join
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile, getModredundantSection
from graphManager import GraphManager
from generateStandardPathGraph import buildTSsearchGraph
import sys

def generateTSsearchFromScan(slurmFiles):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    
    roots = []
    modredundantSection = getModredundantSection(slurmFiles[0])
    for slurmF in slurmFiles:
        newPath = dirname(abspath(slurmF))
        
        gaussianFile = getGaussianInpFromSlurmFile(slurmF)
    
        newNode = GaussianNode(gaussianFile, newPath)
        newNode.verification = "Opt"
        newNode.slurmFile = basename(slurmF)
        jobGraph.add_node( newPath , data = newNode )
        
        roots.append(newPath)
        
    newDir = join(currentDir, "ts_search")
    newNode = GaussianNode("ts.inp", newDir)
    newNode.verification = "Opt"
    
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P AM1
# Opt(TS, CalcAll) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    for r in roots:
        jobGraph.add_edge(r, newDir)
        
    lastDir, newDir = newDir, join(newDir, "dft_ts_search")
        
    newNode = GaussianNode("opt.inp", newDir)
    newNode.verification = "Opt"
    newNode.additionalSection = modredundantSection
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Opt(Modredundant) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)    
    
    return buildTSsearchGraph(jobGraph, newDir)

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
            
        