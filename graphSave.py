#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 17:29:27 2019

@author: michal
"""

import sys
from graphManager import GraphManager

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: graphSave graphKey pickleFile")
    else :
        sm = GraphManager()
        graphKey = sys.argv[1]
        pickleFile = sys.argv[2]
        sm.saveGraph(graphKey, pickleFile)