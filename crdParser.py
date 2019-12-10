#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 12:09:01 2019

@author: michal
"""

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
    atoms = []
    
    for line in atomSelection.split("\n"):
        if not "=" in line:
            continue
        
        lineS = line.split("=")
        subsystem = lineS[2].split("'")[1]
        residueNumber = int(lineS[3].split(",")[0])
        atomName = lineS[4].split("'")[1]

        atoms.append( atomID(subsystem, residueNumber, atomName) )
        
    return atoms