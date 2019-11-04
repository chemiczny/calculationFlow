#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 10:36:10 2019

@author: michal
"""

from graphManager import GraphManager
import sys
from shutil import copyfile
from os.path import join, isfile
import pickle

if __name__ == "__main__":
    if len(sys.argv) !=2:
        print("Usage: graphDump graphKey")
    else:
        graphKey = sys.argv[1]
        
        sm = GraphManager()
        graph = None
        if graphKey in sm.graphs:
            graph = sm.graphs[graphKey]
            print("Read graph from graph manager")
        elif isfile(graphKey):
            infile = open(graphKey,'rb')
            graph = pickle.load(infile)
            infile.close()
            print("Read graph from file")
        else:
            print("Invalid graphKey!")
            quit()
            
        for node in graph.nodes:
            nodeData = graph.nodes[node]["data"]
            if not hasattr( nodeData, "structure2dump" ):
                continue
            
            if not nodeData.structure2dump:
                continue
            
            if nodeData.status != "examined":
                continue
            
            logFilePath = join( nodeData.path, nodeData.logFile )
            copyfile(logFilePath, nodeData.structure2dump)
            
