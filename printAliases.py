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
    
print("alias graphTSsearchFromGuess='python3 "+cwd+"/generateStandardPathGraph.py'")
print("alias graphTSsearchFromScan='python3 "+cwd+"/findTSfromScan.py'")
print("alias graphRun='python3 "+cwd+"/graphManager.py'")
print("alias graphRemove='python3 "+cwd+"/graphRemove.py'")
print("alias graphStatus='python3 "+cwd+"/graphStatus.py'")
print("alias graphSave='python3 "+cwd+"/graphSave.py'")
print("alias graphReplace='python3 "+cwd+"/graphReplace.py'")
print("alias graphResults='python3 "+cwd+"/graphResults.py'")
print("alias graphRestart='python3 "+cwd+"/graphRestart.py'")
print("alias graphPrintNodeAttr='python3 "+cwd+"/graphPrintNodeAttr.py'")
print("alias graphAddNode='python3 "+cwd+"/graphAddNode.py'")