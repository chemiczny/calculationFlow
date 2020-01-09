#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:41:28 2019

@author: michal
"""
import sys
from graphManager import GraphManager

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphDelNode nodeId")
    elif len(sys.argv) > 1:
        sm = GraphManager()
        nodeId = sys.argv[1]
        graph = sm.isGraphHere(nodeId)
        
        if not graph:
            print("Wrong node id")
            quit()
        
        successors = list( graph.successors(nodeId) )
        
        graph.remove_node(nodeId)
        
        while successors:
            node2test = successors.pop()
            
            predecessors = list( graph.predecessors( node2test ) )
            
            if len(predecessors) == 0:
                successors += graph.successors(node2test)
                graph.remove_node(node2test)
        
        sm.saveGraphs()