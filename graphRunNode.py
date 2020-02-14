#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 10:27:35 2020

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: graphRunNode nodePath")
    else:
        nodePath = sys.argv[1]
        gm = GraphManager()
        
        graph = gm.isGraphHere(nodePath)
        
        if not graph:
            print("Invalid path!")
            quit()
            
        graph.nodes[nodePath]["data"].run()
        gm.saveGraphs()
        