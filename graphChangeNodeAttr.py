#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 14:22:30 2019

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphChangeNodeAttry nodePath atribute newValue")
    elif len(sys.argv) == 4:
        node = sys.argv[1]
        atribute = sys.argv[2]
        value = sys.argv[3]

        sm = GraphManager()
        graph = sm.isGraphHere(node)
        
        if not graph:
            print("There is no graph here!")
            quit()
        
        data = graph.nodes[node]["data"]
        dataDict = vars(data)
        
        if not atribute in dataDict:
            print("Ivalid argument!")
            quit()


        setattr( data, atribute, value )
        sm.saveGraphs()

    else :
        print("Cooo?")