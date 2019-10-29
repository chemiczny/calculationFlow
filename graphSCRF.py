#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 10:51:40 2019

@author: michal
"""

from os.path import join, isdir
from jobNode import GaussianNode
from graphManager import GraphManager
import sys
from os import mkdir

def addSCRF(graph, node, theoryLow = "B3LYP/6-31G(d,p)", basename = "", additionalRoute = ""):
    newDir = join(node, basename+"CPCM")
    if not isdir(newDir):
        print("creating: ", newDir)
        mkdir(newDir)
    else:
        print("already exist: ", newDir)

    newNode = GaussianNode("cpcm.inp", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theoryLow+"""
# nosymm SCRF(CPCM, Solvent=Generic, Read) """+additionalRoute+"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556
"""
    newNode.verification = "SP"
    newNode.readResults = True
    newNode.time = "1:00:00"
    newNode.partition = "plgrid-short"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, basename+"SMD")
    if not isdir(newDir):
        print("creating: ", newDir)
        mkdir(newDir)
    else:
        print("already exist: ", newDir)
    newNode = GaussianNode("smd.inp", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theoryLow+"""
# nosymm SCRF(SMD, Solvent=Generic, Read) """+additionalRoute+"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556
"""
    newNode.verification = "SP"
    newNode.readResults = True
    newNode.time = "1:00:00"
    newNode.partition = "plgrid-short"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    graph.nodes[node]["data"].status = "finished"
    
    return graph

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphSCRF node")
    elif len(sys.argv) == 2:
        node = sys.argv[1]
        
        sm = GraphManager()
        graph  = sm.isGraphHere(node)
        if graph:
            addSCRF(graph, node)
            sm.saveGraphs()
        else:
            print("Invalid node key!")
        
    else:
        print( "cooooo?")