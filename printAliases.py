#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 15:08:05 2019

@author: michal
"""

from os import getcwd
from os.path import join

cwd = getcwd()
file2alias = { "sbatchPy.py" : "sbatchPy", "squeuePy.py" : "squeuePy", "sremovePy.py" : "sremove" }

for script in file2alias:
    path = join(cwd, script)
    print("alias "+file2alias[script]+"='python "+path+"'")
    
print("alias graphTSsearchFromGuess='python3 "+cwd+"/generateStandardPathGraph.py'")
print("alias graphTSsearchFromGuessPCM='python3 "+cwd+"/generateStandardPathGraphPCM.py'")
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
print("alias graphAdd='python3 "+cwd+"/graphAdd.py'")
print("alias graphSCRF='python3 "+cwd+"/graphSCRF.py'")
print("alias graphMark2Dump='python3 "+cwd+"/graphMark2Dump.py'")
print("alias graphDump='python3 "+cwd+"/graphDump.py'")
print("alias graphBackup='python3 "+cwd+"/graphBackup.py'")
print("alias graphDFT-SP='python3 "+cwd+"/graphDFT-SP.py'")
print("alias graphTSsearchDynamo='python3 "+cwd+"/tsSearchDynamo.py'")
print("alias graphCleanExaminedJobs='python3 "+cwd+"/graphCleanJobsDone.py'")
print("alias graphTSsearchWHAM='python3 "+cwd+"/tsSearchFromWHAM.py'")
print("alias graphDelNode='python3 "+cwd+"/graphDelNode.py'")
print("alias graphTSsearchWHAM-G='python3 "+cwd+"/tsSearchFromWHAM-G.py'")
print("alias graphSpline='python3 "+cwd+"/splineDYNAMO.py'")
print("alias graphRunNode='python3 "+cwd+"/graphRunNode.py'")
print("alias graphChangeNodeStatus='python3 "+cwd+"/graphChangeNodeStatus.py'")
print("alias graphCancelGraph='python3 "+cwd+"/graphCancelGraph.py'")
print("alias graphKetoPrepare='python3 "+cwd+"/ketoPrepare.py'")
print("alias graphAmberDyn='python3 "+cwd+"/amberDyn.py'")
print("alias mol2fit='python3 "+cwd+"/fitNode.py'")
