#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 23:27:46 2019

@author: michal
"""

from graphManager import GraphManager
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: graphRestart node")
    else:
        sm = GraphManager()
        path = sys.argv[-1]
        sm.restartNode(path)
        sm.saveGraphs()