#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 10:35:48 2019

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) !=3:
        print("Usage: graphMark2Dump node fileName")
    else:
        node = sys.argv[1]
        destinyName = sys.argv[2]
        
        sm = GraphManager()
        graph = sm.isGraphHere(node)
        
        if graph:
            nodeData = graph.nodes[node]["data"]
            nodeData.structure2dump = destinyName
            sm.saveGraphs()
        else:
            print("Invalid node!")
