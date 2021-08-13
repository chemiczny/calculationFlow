#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 10:27:35 2020

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2 :
        nodePath = sys.argv[1]
        gm = GraphManager()
        
        graph = gm.isGraphHere(nodePath)
        
        if not graph:
            print("Invalid path!")
            quit()
            
        graph.nodes[nodePath]["data"].status = "waitingForParent"
        gm.saveGraphs()
    elif len(sys.argv) == 3:
        nodePath = sys.argv[1]
        status = sys.argv[2]

        if not status in [ "waitingForParent" , "running", "finished", "examined" ]:
            print("Invalid status!")
            quit()

        gm = GraphManager()
        
        graph = gm.isGraphHere(nodePath)
        
        if not graph:
            print("Invalid path!")
            quit()

        currentStatus = graph.nodes[nodePath]["data"].status

        if currentStatus == "running":
            print("Job is running!")
            quit()
            
        graph.nodes[nodePath]["data"].status = status
        gm.saveGraphs()
    else:
        print("Usage: graphChangeNodeStatus nodePath status [default: waitingForParent]")
        print("Possible status: waitingForParent, running, finished, examined")
        