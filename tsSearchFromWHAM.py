#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:10:16 2020

@author: michal
"""
import sys
from shutil import copyfile
from parsers import parseFDynamoCompileScript
from crdParser import atomsFromAtomSelection, getSymmetryData
import networkx as nx
from fDynamoJobNode import FDynamoNode
from jobNode import JobNode
from glob import glob
from os.path import dirname, join, abspath
import heapq
import ecmb

class FrameData:
    def __init__(self, crdFilename, dcdFilename, frameNo, reactionCoord):
        self.crd = crdFilename
        self.dcd = dcdFilename
        self.frame = frameNo
        self.rc = reactionCoord

def getTScoords( whamLog ):
    wl = open(whamLog, 'r')
    
    line = wl.readline()
    while "#" in line or "*" in line:
        line = wl.readline()
    
    line = wl.readline()
    
    reactionCoord = None
    while line:
        lineSpl = line.split()
        PMF = lineSpl[-1]
        
        if PMF == "0.0000000000":
            reactionCoord = float(lineSpl[1])
            break
        
        line = wl.readline()
    else:
        print("WTF?! No zero PMF!")
        quit()
    
    wl.close()

    return reactionCoord    

def findNstrClosest2rc( rc, n , selectedAtoms ):
    dcdFiles = glob("pmf*/pmf.trj")
    
    closestFrames = []
    for dcd in dcdFiles:
        dcdDirname = dirname(dcd)
        crdFiles = glob( join( dcdDirname, "*crd*" ) )
        
        if len(crdFiles) != 1:
            print("WTF?! to many crd files")
            quit()
            
        crd = crdFiles[0]
        
        closestFrames += findNstrClose2rcDCD( rc, n, crd, dcd, selectedAtoms )
        
    return heapq.nsmallest( n, closestFrames, key = lambda x : x.rc )
            
def findNstrClose2rcDCD( rc, n, crdFile, dcdFile, selectedAtoms ):
    mol=ecmb.Molec()
    mol.load_crd( crdFile )
    
    a1 = mol.atom_number( selectedAtoms[0].subsystem, selectedAtoms[0].residue, selectedAtoms[0].atom )
    a2 = mol.atom_number( selectedAtoms[1].subsystem, selectedAtoms[1].residue, selectedAtoms[1].atom )
    a3 = mol.atom_number( selectedAtoms[2].subsystem, selectedAtoms[2].residue, selectedAtoms[2].atom )

    mol.dcd_read( dcdFile )
    index = 0
    strList = []
    
    while mol.dcd_next():
        dist1 = ecmb.Dist( mol.crd(a1) , mol.crd(a2) )
        dist2 = ecmb.Dist( mol.crd(a2) , mol.crd(a3) )
        
        strList.append( FrameData(crdFile, dcdFile, index, dist1 - dist2 ) )
        
        index += 1
        
    mol.dcd_close()
    return heapq.nsmallest( n, strList, key = lambda x : x.rc )
    
def buildGraph( rc, definedAtoms, dir2start, dynamoData, dynamoFilesDir ):
    jobGraph = nx.DiGraph()
    
    dynamoData["filesDir"] = dynamoFilesDir
    
    newNode = JobNode(None, dir2start)
    newNode.status = "finished"
    jobGraph.add_node(dir2start, data = newNode)
    
    bestStr = findNstrClosest2rc( rc, 15, definedAtoms )
    
    for i, structure in enumerate( bestStr ):
        newDir = join( dir2start,  "TS_"+str(i) )
        
        addTSsearch(jobGraph, dir2start, newDir, dynamoData, structure, i )
        
def saveCrdFromDCD( destiny, dcdFrame ):
    mol=ecmb.Molec()
    mol.load_crd( dcdFrame.crd )
    
    boxl = getSymmetryData( dcdFrame.crd )
    mol.dcd_read( dcdFrame.dcd )
    
    for i in range( dcdFrame.frame ):
        mol.dcd_next()
        
    mol.save_crd(destiny, boxl)
    mol.dcd_close()
        
def addTSsearch (jobGraph, rootDir, currentDir, baseData, initialGeom, index):
    newNode = FDynamoNode("tsSearch.f90", currentDir)
    newNode.verification = ["Opt" , "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "true" }
    newNode.coordsIn = "coordsIn.crd"
    
    saveCrdFromDCD( join(currentDir, "coordsIn.crd"), initialGeom )
    
    newNode.coordsOut = "coordsDone.crd"
    newNode.getCoordsFromParent = False
    
    newNode.fDynamoPath = baseData["fDynamoPath"]
    newNode.charge = baseData["charge"]
    newNode.method = baseData["method"]
    newNode.forceField = data["forceField"]
    copyfile( join(baseData["filesDir"], baseData["forceField"]), join(currentDir, newNode.forceField) )
    newNode.flexiblePart = data["flexiblePart"]
    copyfile( join(baseData["filesDir"], baseData["flexiblePart"]), join(currentDir, newNode.flexiblePart) )
    newNode.sequence = data["sequence"]
    copyfile( join(baseData["filesDir"], baseData["sequence"]), join(currentDir, newNode.sequence) )
    newNode.qmSele = data["qmSele"]
    
    jobGraph.add_node(currentDir, data = newNode)
    jobGraph.add_edge(rootDir, currentDir)
    
    newDir = join(currentDir, "irc_reverse")
    newNode = FDynamoNode("irc_reverse.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "-1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    

    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(currentDir, newDir)
    
    optDir = join(newDir, "opt")
    
    newNode = FDynamoNode("opt.f90", optDir)
    newNode.verification = ["Opt", "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 0
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "false" , "definedAtoms" : baseData["definedAtoms"]}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone"+str(index)+".crd"
    newNode.measureRCinOutput = True
    

    jobGraph.add_node(optDir, data = newNode)
    jobGraph.add_edge( newDir, optDir)
    
    newDir = join(currentDir, "irc_forward")
    newNode = FDynamoNode("irc_forward.f90", newDir)
    newNode.verification = ["SP"]
    newNode.templateKey = "QMMM_irc_mopac"
    newNode.additionalKeywords = { "IRC_dir" : "1" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    jobGraph.add_node(newDir, data = newNode)
    jobGraph.add_edge(currentDir, newDir)
    
    optDir = join(newDir, "opt")
    
    newNode = FDynamoNode("opt.f90", optDir)
    newNode.verification = ["Opt", "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 0
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "false" , "definedAtoms" : baseData["definedAtoms"]}
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone"+str(index)+".crd"
    newNode.measureRCinOutput = True
    
    jobGraph.add_node(optDir, data = newNode)
    jobGraph.add_edge( newDir, optDir)
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: graphTSsearchWHAM wham.log compileScanScript.sh numberOfTS2find")
    else:
        whamLog = sys.argv[1]
        compileScript = sys.argv[2]
        
        tsReactionCoord = getTScoords(whamLog)
        data = parseFDynamoCompileScript(compileScript)
        definedAtoms = data["definedAtoms"]
        atoms = atomsFromAtomSelection( definedAtoms)
        
        buildGraph(tsReactionCoord, atoms, "multiTSsearch", data, abspath(dirname(compileScript)))
        
        