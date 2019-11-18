#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:31:34 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import  basename, dirname, abspath, join
from jobNode import GaussianNode, JobNode
from parsers import getGaussianInpFromSlurmFile, getModredundantSection
from graphManager import GraphManager
from generateStandardPathGraph import buildTSsearchGraph
import sys

def generateTSsearchFromScan(slurmFiles):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()

    newNode = JobNode(None, currentDir)
    newNode.status = "finished"
    jobGraph.add_node(currentDir, data = newNode)
    
    roots = []
    gaussianInput = getGaussianInpFromSlurmFile(slurmFiles[0])
    modredundantSection = getModredundantSection(  join( dirname(slurmFiles[0]), gaussianInput))
    print("Modredundant section will be added: ")
    print(modredundantSection)
    for slurmF in slurmFiles:
        newPath = dirname(abspath(slurmF))
        
        gaussianFile = getGaussianInpFromSlurmFile(slurmF)
    
        newNode = GaussianNode(gaussianFile, newPath)
        newNode.verification = "Opt"
        newNode.getCoordsFromParent = False
        newNode.slurmFile = basename(slurmF)
        newNode.autorestart = True
        jobGraph.add_node( newPath , data = newNode )
        jobGraph.add_edge(currentDir, newPath)
        roots.append(newPath)
        
    newDir = join(currentDir, "ts_search")
    newNode = GaussianNode("ts.inp", newDir)
    newNode.verification = "Opt"
    
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P AM1
# Opt(TS, CalcAll, noeigentest) nosymm
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
            print("Creating new graph")
            newGraph = generateTSsearchFromScan(slurmFiles)
    
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")
            
        