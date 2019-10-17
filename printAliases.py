#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 15:08:05 2019

@author: michal
"""

from os import getcwd
from os.path import join

cwd = getcwd()
file2alias = { "sbatchPy.py" : "sbatchPy", "squeuePy.py" : "squeuePy", "sremove.py" : "sremove" }

for script in file2alias:
    path = join(cwd, script)
    print("alias "+file2alias[script]+"='python "+path+"'")
    
print("alias initTSsearchFromGuess ='python3 "+cwd+"generateStandardPathGraph.py'")
print("alias initTSsearchFromScan ='python3 "+cwd+"findTSfromScan.py'")
print("alias graphRun ='python3 "+cwd+"graphManager.py'")