#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:57:02 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
from graphGenerators import addSPcorrections, addZPE
from graphManager import GraphManager
import sys

def generateTSsearchFromGuess(slurmFile):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
    
    newNode = GaussianNode(gaussianFile, currentDir)
    newNode.verification = "Opt"
    newNode.slurmFile = slurmFile
    jobGraph.add_node( currentDir , data = newNode )
    
    newDir = join(currentDir, "freq")
    newNode = GaussianNode("freq.inp", newDir)
    newNode.verification = "SP"
    
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Freq nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(currentDir, newDir)
    
    lastDir, newDir = newDir, join(newDir, "ts_opt")
    newNode = GaussianNode("ts_opt.inp", newDir)
    newNode.verification = "Opt"
    newNode.copyChk = True
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Opt(TS,ReadFC,noeigentest) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    lastDir, newDir = newDir, join(currentDir, "freq_verify")
    newNode = GaussianNode("freq_verify.inp", newDir)
    newNode.verification = "Freq"
    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Freq nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir)
    
    optimizedTs = newDir
    
    newDir = join(currentDir, "irc_reverse")
    newNode = GaussianNode("irc_reverse.inp", newDir)
    newNode.verification = "SP"
    newNode.copyChk = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# IRC(RCFC, Reverse) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(optimizedTs, newDir)
    
    lastDir , newDir = newDir,  join(newDir, "opt")
    newNode = GaussianNode("opt.inp", newDir)
    newNode.verification = "Opt"
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Opt nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir)
    addZPE(jobGraph, newDir)
    
    newDir = join(currentDir, "irc_forward")
    newNode = GaussianNode("irc_forward.inp", newDir)
    newNode.verification = "SP"
    newNode.copyChk = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# IRC(RCFC, Forward) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(optimizedTs, newDir)
    
    lastDir , newDir = newDir,  join(newDir, "opt")
    newNode = GaussianNode("opt.inp", None)
    newNode.verification = "Opt"
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Opt nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir)
    addZPE(jobGraph, newDir)
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: initTSsearchFromGuess slurmFile")
    elif len(sys.argv) == 2:
        slurmFile = sys.argv[1]
        currentDir = getcwd()
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchFromGuess(slurmFile)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")
            
        
    else:
        print( "cooooo?")
