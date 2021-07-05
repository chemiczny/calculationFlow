#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:15:22 2019

@author: michal
"""

from graphManager import GraphManager
from sremove import SremoveManager
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: graphCleanJobsDone graphKey")
    else:
        graphKey = sys.argv[1]
        sm = GraphManager()
        
        if not graphKey in sm.graphs:
            print("Invalid graph key!")
            quit()
            
        graph = sm.graphs[graphKey]
        
        id2remove = []
        
        for node in graph.nodes:
            
            status = graph.nodes[node]["data"].status
            
            if status != "examined" and status != "failed":
                continue
            
            id2remove.append(graph.nodes[node]["data"].id)

        if not id2remove:
            quit()
            
        srem = SremoveManager()
        srem.sremove(id2remove)
        
