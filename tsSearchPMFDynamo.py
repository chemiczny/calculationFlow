#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:07:14 2019

@author: michal
"""

import networkx as nx
from os import getcwd
from os.path import join
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from graphManager import GraphManager
import sys
from math import sqrt

class atomID:
    def __init__(self, subsystem, residue_number, atom_name):
        self.subsystem = subsystem
        self.residue = residue_number
        self.atom = atom_name
        self.coords = []
        
def dist(atom1, atom2):
    dist = 0
    for c1, c2 in zip(atom1.coords, atom2.coords):
        dist += ( c1 - c2)**2
        
    return sqrt(dist)
        
def getCoords(structure, atoms):
    atomDict = {}
    
    for a in atoms:
        if not a.subsystem in atomDict:
            atomDict[a.subsystem] = {}
        
        if not a.residue in atomDict[a.subsystem]:
            atomDict[a.subsystem][a.residue]={}
            
        atomDict[a.subsystem][a.residue][a.atom] = a
    
    source = open(structure)
    
    line = source.readline()
    
    while line:
        if "Subsystem" in line:
            lineSpl = line.split()
            currentSubsystemName = lineSpl[-1]
#            currentSubsystemId = int(lineSpl[-2])
            
            if currentSubsystemName in atomDict:
                residues2find = atomDict[currentSubsystemName]
            else:
                residues2find = {}
                
            if currentSubsystemName == "WAT":
                break
            
        if "Residue" in line:
            
            lineSpl = line.split()
#            currentResidueName = lineSpl[-1]
            currentResidueId = int(lineSpl[-2])
            
            if currentResidueId in residues2find:
                atoms2find = residues2find[currentResidueId]
            else:
                atoms2find = {}
            
            line = source.readline()
            atomsNo = int(line.split()[0])
            
            for i in range(atomsNo):
                line = source.readline()
                lineSpl = line.split()
#                atomInd = int(lineSpl[0])
                atomName = lineSpl[1]
                
                if atomName in atoms2find:
                    atom = atoms2find[atomName]
                    atom.coords = [ float(c) for c in lineSpl[-3:] ]
                
                
        line = source.readline()
    
    source.close()

def atomsFromAtomSelection( atomSelection ):
    atoms = {}
    
    for line in atomSelection.split("\n"):
        if not line.strip():
            continue
        
        lineS = line.split("=")
        subsystem = lineS[1].split("'")[1]
        residueNumber = int(lineS[2].split(",")[0])
        atomName = int(lineS[3].split(")")[0]) 
    
        atoms.append( atomID(subsystem, residueNumber, atomName) )
        
    return atoms

def generateTSsearchDynamoPMF(compFile):
    jobGraph = nx.DiGraph()
    currentDir = getcwd()
    data = parseFDynamoCompileScript(compFile)
    
    definedAtoms = data["definedAtoms"]
    atoms = atomsFromAtomSelection(definedAtoms)
    getCoords( data["coordsIn"], atoms)
    
    initialCoord = dist(atoms[0], atoms[1]) - dist(atoms[1], atoms[2])
    
    newNode = FDynamoNode(data["inputFile"], currentDir)
    newNode.coordsIn = data["coordsIn"]
    newNode.verification = [ "scan1D" ]
    newNode.slurmFile = None
    newNode.autorestart = False
#    newNode.noOfExcpectedImaginaryFrequetions = 1
    newNode.forceField = data["forceField"]
    newNode.flexiblePart = data["flexiblePart"]
    newNode.sequence = data["sequence"]
    newNode.qmSele = data["qmSele"]
    newNode.templateKey = "QMMM_scan1D_mopac"
    newNode.fDynamoPath = data["fDynamoPath"]
    newNode.charge = data["charge"]
    newNode.method = data["method"]
    newNode.additionalKeywords = { "scanDir" : "", "coordScanStart" : str(initialCoord) , "iterNo" : "70"}
    
    jobGraph.add_node( currentDir , data = newNode )
    newNode.generateInput()
    newNode.compileInput()
    
    
    currentDir = join(currentDir, "ts_search")
    newNode = FDynamoNode("tsSearch.f90", currentDir)
    newNode.verification = ["Opt"]
    newNode.templateKey = "QMMM_opt_mopac"
    newNode.additionalKeywords = { "ts_search" : "true" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    
    
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
    newNode.additionalKeywords = { "ts_search" : "false" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    

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
    newNode.additionalKeywords = { "ts_search" : "false" }
    newNode.coordsIn = "coordsStart.crd"
    newNode.coordsOut = "coordsDone.crd"
    

    jobGraph.add_node(optDir, data = newNode)
    jobGraph.add_edge( newDir, optDir)
    
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: initTSsearchDynamoPMF compileScanScript.sh")
    else:
        compFile = sys.argv[1]
        currentDir = getcwd()
        
        sm = GraphManager()
        graph = sm.isGraphHere(currentDir)
        if not graph:
            newGraph = generateTSsearchDynamoPMF(compFile)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")