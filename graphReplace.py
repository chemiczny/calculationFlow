#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 18:30:01 2019

@author: michal
"""

from graphManager import GraphManager
import sys
from os.path import basename, dirname, abspath
from parsers import getGaussianInpFromSlurmFile

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphReplace node slurmFile status [default: waitingForParent]")
        print("Possible status: waitingForParent, running, finished, examined")
    elif len(sys.argv) == 3:
        slurmFile = sys.argv[2]
        inputFile = getGaussianInpFromSlurmFile(slurmFile)
        newNode = dirname(abspath(slurmFile))
        
        slurmFile = basename(slurmFile)
        oldNode = sys.argv[1]
        
        sm = GraphManager()
        sm.insertPath2node(oldNode, newNode, slurmFile, inputFile)
        sm.saveGraphs()
    elif len(sys.argv) == 4:
        slurmFile = sys.argv[2]
        inputFile = getGaussianInpFromSlurmFile(slurmFile)
        newNode = dirname(abspath(slurmFile))
        
        slurmFile = basename(slurmFile)
        oldNode = sys.argv[1]
        status = sys.argv[3]

        sm = GraphManager()
        sm.insertPath2node(oldNode, newNode, slurmFile, inputFile, status)
        sm.saveGraphs()
        
    else:
        print( "cooooo?")