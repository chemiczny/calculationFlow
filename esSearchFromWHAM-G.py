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
from os.path import dirname, join, abspath, basename, isdir, isfile
from os import getcwd, makedirs
from graphManager import GraphManager
import heapq
import ecmb

class FrameData:
    def __init__(self, crdFilename, dcdFilename, frameNo, reactionCoord):
        self.crd = crdFilename
        self.dcd = dcdFilename
        self.frame = frameNo
        self.rcDiff = reactionCoord

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
    dcdNo = len(dcdFiles)
    for i, dcd in enumerate(dcdFiles, 1):
        dcdDirname = dirname(dcd)
        crdFiles = list(glob( join( dcdDirname, "pmfDone.crd" ) ))
        if not crdFiles:
            continue 
            
        print("Analysing ...", dcd , i , "/", dcdNo)

        if len(crdFiles) != 1:
            print("WTF?! to many crd files")
            quit()
            
        crd = crdFiles[0]
        
        closestFrames += findNstrClose2rcDCD( rc, n, crd, dcd, selectedAtoms )
        
    return heapq.nsmallest( n, closestFrames, key = lambda x : x.rcDiff )
            
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
        dist1 = ecmb.Dist( mol.crd[a1] , mol.crd[a2] )
        dist2 = ecmb.Dist( mol.crd[a2] , mol.crd[a3] )
        
        strList.append( FrameData(crdFile, dcdFile, index, abs( dist1 - dist2 - rc )) )
        
        index += 1
        
    mol.dcd_close()
    return heapq.nsmallest( n, strList, key = lambda x : x.rcDiff )

def rewriteFlexibleSeleFile( original ):
    inF = open(original, 'r')
    line = inF.readline().upper()
    
    corrected = ""
    
    if "MY_SELE_QMNB" in line:
        corrected = original
    else:
        corrected = original.replace(".f90", "_qmnb.f90")
        
        cF = open(corrected, 'w')
        cF.write( line.replace("MY_SELE(" , "MY_SELE_QMNB(") )
        
        line = inF.readline()
        while line:
            cF.write(line)
            line = inF.readline()
    
    inF.close()
    
    return corrected
    
def buildGraph( rc, definedAtoms, dir2start, dynamoData, dynamoFilesDir, tsNo, method, basis ):
    jobGraph = nx.DiGraph()
    
    dynamoData["filesDir"] = dynamoFilesDir
    # dynamoData["fDynamoPath"] = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
    gaussianFlexibleSele = rewriteFlexibleSeleFile(  join(dynamoFilesDir, dynamoData["flexiblePart"]) )
    
    newNode = JobNode(None, dir2start)
    newNode.status = "finished"
    jobGraph.add_node(dir2start, data = newNode)
    
    bestStr = findNstrClosest2rc( rc, tsNo, definedAtoms )
    
    for i, structure in enumerate( bestStr ):
        print("Structure for TS search ", structure.dcd, structure.frame)
        newDir = join( dir2start,  "TS_"+str(i) )
        
        addTSsearch(jobGraph, dir2start, newDir, dynamoData, structure, i, method, basis , gaussianFlexibleSele )

    return jobGraph
        
def saveCrdFromDCD( destiny, dcdFrame ):
    mol=ecmb.Molec()
    mol.load_crd( dcdFrame.crd )
    
    boxl = getSymmetryData( dcdFrame.crd )
    mol.dcd_read( dcdFrame.dcd )
    
    for i in range( dcdFrame.frame ):
        mol.dcd_next()
        
    mol.save_crd(destiny, boxl)
    mol.dcd_close()
        
def addTSsearch (jobGraph, rootDir, currentDir, baseData, initialGeom, index, method, basis, gaussianFelxSele):
    if not isdir(currentDir):
        makedirs(currentDir)
    saveCrdFromDCD( join(currentDir, "coordsIn.crd"), initialGeom )

    #pre opt

    stepOptDir = currentDir

    newNode = FDynamoNode("optStep.f90", stepOptDir)
    newNode.verification = ["Opt"]
    newNode.partition = "plgrid-short"
    newNode.time = "1:00:00"
    newNode.templateKey = "QMMM_opt_mopac_no_hess"
    newNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : baseData["definedAtoms"] , "constraints" : baseData["constraints"], "gradientTolerance" : "0.3"}
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
    newNode.coordsOut = "coordsDone.crd"
    newNode.getCoordsFromParent = False
    newNode.coordsIn = "coordsIn.crd" 


    jobGraph.add_node(stepOptDir, data = newNode)
    jobGraph.add_edge( rootDir, stepOptDir)


    ########################################################
    currentDir = join(currentDir, "opt_gaussian")
    if not isdir(currentDir):
        makedirs(currentDir)
    
    gaussianTime = "72:00:00"

    newNode = FDynamoNode("opt", currentDir)
        
    newNode.verification = ["Opt" , "Freq"]
    newNode.noOfExcpectedImaginaryFrequetions = 0
    newNode.templateKey = "QMMM_opt_gaussian"
    newNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
    newNode.additionalKeywords =  { "ts_search" : "false", "definedAtoms" : baseData["definedAtoms"] , "method" : method, "basis" : basis , "multiplicity" : 1, "otherOptions" : "" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    newNode.flexiblePart = basename(gaussianFelxSele)
    copyfile( gaussianFelxSele, join(currentDir, newNode.flexiblePart) )
    newNode.processors = 24
    newNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"
    newNode.partition = "plgrid"
    newNode.time = gaussianTime
    

    jobGraph.add_node(currentDir, data = newNode)
    jobGraph.add_edge(stepOptDir, currentDir)

    

if __name__ == "__main__":
    if not len(sys.argv) in [ 6, 7]:
        print("Usage: graphTSsearchWHAM_fast_IRC wham.log/RC ,compileScanScript.sh ,numberOfTS2find ,method ,basis , name")
    else:
        whamLog = sys.argv[1]
        compileScript = sys.argv[2]
        TSno = int(sys.argv[3])
        method = sys.argv[4]
        basis = sys.argv[5]

        additionalName = ""
        if len(sys.argv) == 7:
            additionalName = sys.argv[6]

        if isfile(whamLog):
            tsReactionCoord = getTScoords(whamLog)
        else:
            tsReactionCoord = float(whamLog)
        print("Found reaction coordinate: ", tsReactionCoord)
        data = parseFDynamoCompileScript(compileScript)
        definedAtoms = data["definedAtoms"]
        atoms = atomsFromAtomSelection( definedAtoms)

        currentDir = abspath(dirname(compileScript))

        graphDir = join( getcwd(), "multiOpt-"+method + additionalName )

        sm = GraphManager()
        graph = sm.isGraphHere(graphDir)
        if not graph:
            newGraph = jobGraph = buildGraph(tsReactionCoord, atoms, graphDir, data, currentDir, TSno, method, basis)
    
            
            result = sm.addGraph(newGraph, graphDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")
        
        