#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 10:43:20 2019

@author: michal
"""
from os.path import join, dirname

def getGaussianInpFromSlurmFile(slurmFile):
    sf = open(slurmFile)
    
    line = sf.readline()
    inpName = None
    while line:
        if "g16" in line or "g09" in line:
            lineSpl = line.split()
            
            for i, word in enumerate(lineSpl):
                if word  in [ "g16" , "g09" ]:
                    inpName = lineSpl[i+1]
        
        line = sf.readline()
    
    sf.close()
    return inpName

def getCheckpointNameFromInput(inputFile):
    sf = open(inputFile)
    
    line = sf.readline()
    chkName = None
    while line:
        if "%CHK" in line.upper():
            lineSpl = line.split("=")
            chkName = lineSpl[-1].strip()
            break
        
        line = sf.readline()
    
    sf.close()
    return chkName

def getLastCoordsFromLog(logFile):
    gFile = open(logFile, 'r' )
    
    
    line = gFile.readline()
    while line:
       
        if "Coordinates" in line:
            
            for i in range(3):
                line = gFile.readline()
                
            coords = []
            atomNo = 0
            while not "-----" in line:
                lineS = line.split()
                newCoords = "\t".join(lineS[-3:])
                coords.append(newCoords.split())
                atomNo +=1
                line = gFile.readline()
                
        
        line = gFile.readline()
        
        
    gFile.close()
    return coords

def isBlankLine(line):
    return line.isspace()

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def floatInList( list2test ):
    res = []
    for i, item in enumerate(list2test):
        if isfloat(item):
            res.append(i)
    return res

def readG16Inp( oldInput ):
    oldFile = open(oldInput, 'r')
    line = oldFile.readline()
    
    #route section
    while not isBlankLine(line):
        line = oldFile.readline()
        
    line = oldFile.readline()
    #comment
    while not isBlankLine(line):
        line = oldFile.readline()
        
    line = oldFile.readline() #charges and multiplicity
    line = oldFile.readline()
    
    indexes = []
    ind = 0
    coords = []
    elements = []
    while not isBlankLine(line):
        
        lineSpl = line.split()
        if lineSpl[1] == "-1":
            indexes.append(ind)
            
        coordInd = floatInList(lineSpl)[-3:]
        newCoords = [ float(lineSpl[c]) for c in coordInd]
        coords.append(newCoords)
        elements.append(lineSpl[0])
        
        line = oldFile.readline()
        ind += 1
    
    oldFile.close()
    
    return indexes, coords, elements

def getCoordInd( lineSpl ):
    floatInd = floatInList(lineSpl)

    contInd = [ floatInd[0] ]
    lastElement = floatInd[0]

    for ind in floatInd[1:]:
        if ind-lastElement == 1:
            contInd.append(ind)
        else:
            break
        lastElement = ind

    return contInd[-3:]

def writeNewInput ( oldInput, newCoords, newInputName, routeSection = "", skipAfterCoords = False, additional = "" ):
    oldFile = open(oldInput, 'r')
    beginning = ""
    if routeSection :
        beginning = routeSection
    line = oldFile.readline()
    destiny = open(newInputName, 'w')
    
    #route section
    while not isBlankLine(line):
        if not routeSection:
            beginning += line
        line = oldFile.readline()
        
    beginning += line
    line = oldFile.readline()
    #comment
    while not isBlankLine(line):
        beginning += line
        line = oldFile.readline()
        
    beginning += line
    line = oldFile.readline()
    
    beginning += line
    destiny.write(beginning)
    for coord in newCoords:
        line = oldFile.readline()
        lineSpl = line.split()
        coordInd = getCoordInd( lineSpl )
        for ci, crd in zip(coordInd, coord):
            lineSpl[ci] = str(crd)
        destiny.write("\t".join(lineSpl)+"\n")
        
    if not skipAfterCoords:
        line = oldFile.readline()
        while line:
            destiny.write(line)
            line = oldFile.readline()
            
    if additional:
        destiny.write("\n")
        destiny.write(additional.strip("\n"))
        destiny.write("\n\n")
    elif skipAfterCoords:
        destiny.write("\n\n")
    
    destiny.close()
    oldFile.close()
    
def getModredundantSection(gaussianInput):
    gf = open(gaussianInput, 'r')
    
    #route section
    line = gf.readline()
    while not isBlankLine(line):
        line = gf.readline()
        
    line = gf.readline()
    #comment
    while not isBlankLine(line):
        line = gf.readline()
        
    line = gf.readline()
    #spin, multiplicity and coordinates
    while not isBlankLine(line):
        line = gf.readline()
        
    modredundantSection = ""
    
    line = gf.readline()
    while not isBlankLine(line):
        modredundantSection += line
        line = gf.readline()
        
    gf.close()
    
    return modredundantSection


def go2Freqs(logF):
    line = logF.readline()
    
    while line and not "and normal coordinates:" in line:
        line = logF.readline()
        
    logF.readline()
        
def readNewFreqs(logF):
    line = logF.readline()
    freqsNo = len(line.split())
    if freqsNo > 3:
        return
        
    newFreqs = []
    for i in range(freqsNo):
        newFreqs.append({})
        
    line = logF.readline()
    
    if not "Frequencies" in line:
        return
    
    for i, freq in enumerate(line.split()[-3:]):
        newFreqs[i]["Frequency"] = freq
    
    while not "IR Inten" in line:
        line = logF.readline()
        
    for i, irInt in enumerate(line.split()[-3:]):
        newFreqs[i]["IRintensity"] = irInt
        
    while not "Atom" in line:
        line = logF.readline()
        
    columnsNo = len(line.split())
    
    for i in range(freqsNo):
        newFreqs[i]["vector"] = []
    
    lineS = logF.readline().split()
    
    while len(lineS) == columnsNo:
        for i in range(freqsNo):
            firstIndex = 2+i*3
            lastIndex = firstIndex+3
            newCoords = lineS[firstIndex:lastIndex]
            newCoords = [ float(c) for c in newCoords ]
            
            [ x, y, z] = newCoords
            if x == 0.0 and y == 0.0 and z == 0.0:
                continue
            
            atomNo = int(lineS[0])-1
            newFreqs[i]["vector"].append( { "coords" : [ x, y, z ], "atomInd" : atomNo } )
            
        lineS = logF.readline().split()
        
    return newFreqs

def getFreqs(logFile):
    logF = open(logFile, 'r')
    freqs = []
    
    go2Freqs(logF)
    newFreqs = readNewFreqs(logF)
    while newFreqs:
        freqs += newFreqs
        newFreqs = readNewFreqs(logF)
    
    
    logF.close()
    
    return freqs

def parseFDynamoCompileScript(compileScript):
    compDir = dirname(compileScript)
    cs = open(compileScript, 'r')
    infoLine = cs.readline()
    cs.close()
    
    data = {}
    data["fDynamoPath"] = infoLine.split()[2]
    inputFile = infoLine.split("=")[-1].strip()
    
    data["inputFile"] = inputFile
    
    fortFile = open( join(compDir, inputFile), 'r')
    
    data["qmSele"] = ""
    data["definedAtoms"] = ""
    data["constraints"] = ""
    
    line = fortFile.readline()
    while line:
        if "mm_file_process" in line:
            data["forceField"] = line.split('"')[3]
        elif "mm_system_construct" in line:
            data["sequence"] = line.split('"')[3]
        elif "coordinates_read" in line and not "coordsIn" in data:
            data["coordsIn"] = line.split('"')[1]
        elif "atom_selection" in line and "acs" in line:
                   
            while "&" in line:
                data["qmSele"] += line
                line = fortFile.readline()
                
            data["qmSele"] += line
                
        elif "mopac_setup" in line :
            
            while "&" in line:
                if "method" in line:
                    data["method"] = line.split("'")[1]
                elif "charge" in line:
                    data["charge"] = line.split("=")[1].split(",")[0]
                
                line = fortFile.readline()
            
        elif "coordinates_write" in line:
            data["coordsOut"] = line.split('"')[1]
        
        elif "atom_number(" in line:
            data["definedAtoms"] += line

        elif "constraint_point_define" in line:
            data["constraints"] += line
            
        line = fortFile.readline()
    
    fortFile.close()

    data["flexiblePart"] = "in20.f90"
    data["qmSele"] = data["qmSele"].strip()+"\n"
    
    if data["definedAtoms"]:
        data["definedAtoms"] = data["definedAtoms"].strip()+"\n"
    
    return data    
    
    
    
