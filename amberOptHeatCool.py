#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 19:38:35 2020

@author: michal
"""
import sys
from graphManager import GraphManager
from os import getcwd
from os.path import join, basename
import networkx as nx
from amberNode import AmberNode
from cppTrajNode import CppTrajNode

def solventInLine(line):
    if "WAT" in line:
        return True
    
    if "CL-" in line:
        return True
    
    if "NA+" in line:
        return True
    
def countNoSolventInLine(line):
    noSolvent = 0
    
    for res in line.split():
        if not res in [ "WAT" , "NA+", "CL-" ]:
            noSolvent += 1
            
    return noSolvent

def getNumberOfNotSolventRes(topologyFile):
    noSolventRes = 0
    
    topF = open(topologyFile, 'r')
    
    line = topF.readline()
    
    while line and not "%FLAG RESIDUE_LABEL" in line:
        line = topF.readline()
    
    topF.readline()
    line = topF.readline().upper()
    
    while not solventInLine(line):
        noSolventRes += countNoSolventInLine(line)
        line = topF.readline().upper()
        
    noSolventRes += countNoSolventInLine(line)
    topF.close()
    
    return noSolventRes

def generateGraph(topologyFile, coordinates):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    
    notSolventNo = getNumberOfNotSolventRes(topologyFile)
    
    optimNode = AmberNode("amber.slurm", currentDir, currentDir, topologyFile, coordinates)
    optimNode.NoSolventResidues = notSolventNo
    optimNode.runType = "standardOptimization"
    optimNode.time = "1:00:00"
    optimNode.partition = "plgrid-short"
    jobGraph.add_node( currentDir, data = optimNode )
    optimNode.writeSlurmScript("amber.slurm")
    
    heatingDir = join( currentDir, "heating" )
    heatingNode = AmberNode("amber.in", heatingDir, heatingDir, topologyFile)
    heatingNode.NoSolventResidues = notSolventNo
    heatingNode.time = "1:00:00"
    heatingNode.partition = "plgrid-short"
    heatingNode.runType = "standardHeating"
    jobGraph.add_node(heatingDir, data = heatingNode )
    jobGraph.add_edge(currentDir, heatingDir)
    

    coolDirName = join(currentDir, "cool")
    coolNode = AmberNode("amber.slurm", coolDirName, coolDirName, basename(topologyFile), "md_rst_0.nc")
    coolNode.runType = "standardCooling"
    coolNode.time = "1:00:00"
    coolNode.partition = "plgrid-short"
    coolNode.processors = 8
    jobGraph.add_node( coolDirName, data = coolNode )
    jobGraph.add_edge(heatingDir, coolDirName)
    
    return jobGraph


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("graphAmberDyn topology file, coordinates")
    else:
        sm = GraphManager()
        currentDir = getcwd()
        graph = sm.isGraphHere(currentDir)
        
        topology = sys.argv[1]
        coordinates = sys.argv[2]
        if not graph:
            newGraph = generateGraph(topology, coordinates)
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")