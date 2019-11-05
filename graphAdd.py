#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:41:28 2019

@author: michal
"""
import sys
from graphManager import GraphManager
import pickle

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: graphAdd graphKey pickleFile")
    elif len(sys.argv) > 1:
        sm = GraphManager()
        graphKey = sys.argv[1]
        pickleFile = sys.argv[2]
        
        infile = open(pickleFile,'rb')
        graph = pickle.load(infile)
        infile.close()
        
        if graphKey in sm.graphs:
            print("Graph with this key already exists!")
            quit()
            
        sm.graphs[graphKey] = graph
        sm.saveGraphs()