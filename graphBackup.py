#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 10:49:57 2019

@author: michal
"""

from graphManager import GraphManager
import sys
from shutil import copyfile
from os.path import join, isdir
import networkx as nx
from os import makedirs
import pickle

if __name__ == "__main__":
    if len(sys.argv) !=3:
        print("Usage: graphBackup graphKey destiny")
    else:
        graphKey = sys.argv[1]
        graphDestiny = sys.argv[2]
        sm = GraphManager()
        
        
        if graphKey in sm.graphs:
            graph = sm.graphs[graphKey]
            
            relabelDict = {}
            for node in graph.nodes:
                nodeData = graph.nodes[node]["data"]
                
                newPath = nodeData.path.replace( graphKey, graphDestiny )
                
                if not isdir(newPath):
                    makedirs(newPath)
                
                relabelDict[ node ] = newPath
                
                if nodeData.logFile:
                    logFilePath = join( nodeData.path, nodeData.logFile )
                    newPath = logFilePath.replace( graphKey, graphDestiny )
                    print("Copy ", logFilePath , " to ", newPath)
                    copyfile(logFilePath, newPath)
                    
                if nodeData.inputFile:
                    inputFilePath = join( nodeData.path, nodeData.inputFile )
                    newPath = inputFilePath.replace( graphKey, graphDestiny )
                    print("Copy ", inputFilePath , " to ", newPath)
                    copyfile(inputFilePath, newPath)
                    
                if nodeData.slurmFile:
                    slurmFilePath = join( nodeData.path, nodeData.slurmFile )
                    newPath = slurmFilePath.replace( graphKey, graphDestiny )
                    print("Copy ", slurmFilePath , " to ", newPath)
                    copyfile(slurmFilePath, newPath)
                    
            nx.relabel_nodes(graph, relabelDict, False)
            
            graphPickleName = join(graphDestiny, "graph.pickle")
            
            file2dump = open(graphPickleName, 'wb')
            pickle.dump(graph, file2dump)
            file2dump.close()
            
        else:
            print("Invalid graphKey!")