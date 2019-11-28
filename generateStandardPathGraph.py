#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:57:02 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join, dirname
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile, getModredundantSection
from graphGenerators import addSPcorrections, addZPE
from graphManager import GraphManager
import sys

def frozenDistancesFromModredundantSection(modredundantSection):
    frozenDists = []
    
    for line in modredundantSection.split("\n"):
        if not line:
            continue
        
        lineS = line.split()
        
        if lineS[0] != "B":
            continue
        
        if lineS[-1] != "F":
            continue
        
        frozenDists.append( [ int(lineS[1])-1, int(lineS[2])-1 ] )
        
    return frozenDists

def generateTSsearchFromGuess(slurmFile, functional = "B3LYP"):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
    modredundantSection = getModredundantSection( join( dirname(slurmFile ) , gaussianFile ) )
    frozenDists = frozenDistancesFromModredundantSection(modredundantSection)
    
    newNode = GaussianNode(gaussianFile, currentDir)
    newNode.verification = "Opt"
    newNode.slurmFile = slurmFile
    jobGraph.add_node( currentDir , data = newNode )
    
    return buildTSsearchGraph(jobGraph, currentDir, functional, frozenDists )
    
def buildTSsearchGraph( jobGraph, currentDir, functional = "B3LYP", frozenDists = [] ):
    newDir = join(currentDir, "freq")
    newNode = GaussianNode("freq.inp", newDir)
    newNode.verification = "SP"
    
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
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
#P """+functional+"""/6-31G(d,p)
# Opt(TS,ReadFC,noeigentest) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    lastDir, newDir = newDir, join(currentDir, "freq_verify")
    newNode = GaussianNode("freq_verify.inp", newDir)
    newNode.verification = "Freq"
    newNode.distances2measure = frozenDists
    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.readResults = True
    newNode.structure2dump = "TS.inp"
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
# Freq nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir, theoryLow = functional+"/6-31G(d,p)", theoryHigh = functional+ "/6-311+G(2d,2p)")
    
    optimizedTs = newDir
    
    newDir = join(currentDir, "irc_reverse")
    newNode = GaussianNode("irc_reverse.inp", newDir)
    newNode.verification = "SP"
    newNode.copyChk = True
    newNode.distances2measure = frozenDists
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
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
    newNode.distances2measure = frozenDists
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
# Opt nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir, theoryLow = functional+"/6-31G(d,p)", theoryHigh = functional+ "/6-311+G(2d,2p)")
    addZPE(jobGraph, newDir, structure2dump= "irc_reverse_opt.inp", theory = functional+"/6-31G(d,p)")
    
    newDir = join(currentDir, "irc_forward")
    newNode = GaussianNode("irc_forward.inp", newDir)
    newNode.verification = "SP"
    newNode.copyChk = True
    newNode.distances2measure = frozenDists
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
# IRC(RCFC, Forward) nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(optimizedTs, newDir)
    
    lastDir , newDir = newDir,  join(newDir, "opt")
    newNode = GaussianNode("opt.inp", newDir)
    newNode.verification = "Opt"
    newNode.distances2measure = frozenDists
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+functional+"""/6-31G(d,p)
# Opt nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(lastDir, newDir)
    
    addSPcorrections(jobGraph, newDir, theoryLow = functional+"/6-31G(d,p)", theoryHigh = functional+ "/6-311+G(2d,2p)")
    addZPE(jobGraph, newDir, structure2dump= "irc_forward_opt.inp", theory = functional+"/6-31G(d,p)")
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: initTSsearchFromGuess slurmFile functional [default: B3LYP]")
    else:
        slurmFile = sys.argv[1]
        currentDir = getcwd()
        
        functional = "B3LYP"
        if len(sys.argv) >= 3:
            functional = sys.argv[2]
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchFromGuess(slurmFile, functional)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")

