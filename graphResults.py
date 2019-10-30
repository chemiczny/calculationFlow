#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 23:24:04 2019

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: graphResults graphKey force[optional]")
    elif len(sys.argv) == 2:
        graphKey = sys.argv[1]
        sm = GraphManager()
        sm.printResults(graphKey)
        sm.saveGraphs()
    else:
        graphKey = sys.argv[1]
        sm = GraphManager()
        sm.printResults(graphKey, True)
        sm.saveGraphs()