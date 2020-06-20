#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 16:03:56 2020

@author: michal
"""

from graphManager import GraphManager
from antechamberNode import AntechamberNode
import networkx as nx
from os import getcwd
from os.path import join
import sys
from gaussianNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile
from fitNode import FitNode

def generateGraph(slurmFile, template):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    gaussianFile = getGaussianInpFromSlurmFile(slurmFile)
    
    newNode = GaussianNode(gaussianFile, currentDir)
    newNode.verification = "Opt"
    newNode.slurmFile = slurmFile
    newNode.autorestart = True
    jobGraph.add_node( currentDir , data = newNode )
    
    newDir = join(currentDir, "gesp")
    newNode = GaussianNode("auto_gesp.inp", newDir)
    newNode.verification = "SP"
    
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Gfinput  Pop=full  Density  Test iop(6/50=1)
# Units(Ang,Deg) Pop=MK iop(6/33=2) iop(6/42=6)
"""
    newNode.additionalSection = "keto.gesp\n\nketo.gesp\n\n"
    newNode.gesp = "keto.gesp"
    newNode.time = "1:00:00"
    newNode.partition = "plgrid-short"
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(currentDir, newDir)
    
    
    anteDir = join(newDir, "antechamber")
    newNode = AntechamberNode("keto.gesp", anteDir)
    newNode.partition = "plgrid-short"
    jobGraph.add_node(anteDir, data = newNode)
    jobGraph.add_edge(newDir, anteDir)
    
    fitDir = join(anteDir, "fit")
    newNode = FitNode("keto.mol2", fitDir, template)
    newNode.partition = "plgrid-short"
    jobGraph.add_node(fitDir, data = newNode)
    jobGraph.add_edge(anteDir, fitDir)

    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ketoPrepare slurmFile, template")
    else:
        sm = GraphManager()
        currentDir = getcwd()
        graph = sm.isGraphHere(currentDir)
        
        slurmFile = sys.argv[1]
        template = sys.argv[2]
        if not graph:
            newGraph = generateGraph(slurmFile, template)
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")