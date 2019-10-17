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
        print("Usage: graphRemove graphKeys")
    elif len(sys.argv) > 1:
        sm = GraphManager()
        graphKeys = sys.argv[1:]
        for g in graphKeys:
            sm.deleteGraph(g)
        sm.saveGraphs()
    else:
        print( "cooooo?")