#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:15:22 2019

@author: michal
"""

from graphManager import GraphManager
from sremove import SremoveManager
import sys
from os import system

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: graphCancelGraph graphKey")
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
            
            if status != "running":
                continue
            
            if graph.nodes[node]["data"].id != None:
                id2remove.append(graph.nodes[node]["data"].id)

        if not id2remove:
            quit()
            

        srem = SremoveManager()
        system("scancel "+" ".join(id2remove))
        srem.sremove(id2remove)

        
