#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 15:01:57 2019

@author: michal
"""

import networkx as nx
from os import getcwd, mkdir
from os.path import join, isdir
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
import sys
from graphManager import GraphManager

def addSPcorrections(graph, node):
    newDir = join(node, "TZ")
    newNode = GaussianNode("tz.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "PCM")
    newNode = GaussianNode("pcm.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# nosymm SCRF(Solvent=Generic, Read)
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "TZ_PCM")
    newNode = GaussianNode("tz_pcm.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphs slurmFile")
    elif len(sys.argv) == 2:
        jobGraph = nx.DiGraph()
        slurmFile = sys.argv[1]
        currentDir = getcwd()
        gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
        gaussianLog = gaussianFile.replace("inp", "log")
        
        newNode = GaussianNode(gaussianFile, currentDir)
        newNode.status = "finished"
        jobGraph.add_node( currentDir , data = newNode )
        
        sm = GraphManager()
        sm.buildGraphDirectories(jobGraph)
        sm.graphs.append(jobGraph)
        sm.saveGraphs()
    else:
        print( "cooooo?")