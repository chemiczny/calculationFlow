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
        print("Usage: graphPrintNodeAttry nodePath")
    elif len(sys.argv) == 2:
        node = sys.argv[1]
        sm = GraphManager()
        sm.printNodeAttributes(node)
    else :
        print("Cooo?")