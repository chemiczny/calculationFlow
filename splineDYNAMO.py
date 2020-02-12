#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:07:14 2019

@author: michal
"""

import networkx as nx
from os import getcwd, makedirs
from os.path import join, abspath, dirname, basename, isdir
from shutil import copyfile
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from graphManager import GraphManager
from jobNode import JobNode
import sys
from splineNodes import SplineDiffNode, SplineNode
        

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

def buildGraph(whamLog, compileScript, method, basis, structures, sourceDir, graphDir):
    jobGraph = nx.DiGraph()
#    currentDir = getcwd()
    data = parseFDynamoCompileScript(compileScript)
    
    gaussianFlexibleSele = rewriteFlexibleSeleFile(  join(sourceDir, data["flexiblePart"]) )

    ########## ROOT NODE ###########################
    rootNode = FDynamoNode(None, graphDir)
    rootNode.status = "finished"

    if not isdir(graphDir):
        makedirs(graphDir)
    
    rootNode.fDynamoPath = data["fDynamoPath"]
    rootNode.charge = data["charge"]
    rootNode.method = data["method"]
    rootNode.forceField = data["forceField"]
    copyfile( join(sourceDir, data["forceField"]), join(graphDir, rootNode.forceField) )
    rootNode.flexiblePart = data["flexiblePart"]
    copyfile( join(sourceDir, data["flexiblePart"]), join(graphDir, rootNode.flexiblePart) )
    rootNode.sequence = data["sequence"]
    copyfile( join(sourceDir, data["sequence"]), join(graphDir, rootNode.sequence) )
    rootNode.qmSele = data["qmSele"]
    
    jobGraph.add_node(graphDir, data = rootNode)
    
    ########### SPLINE NODE ####################
    splineDir = join( graphDir, "spline" )
    splineNode = SplineNode(None, splineDir, whamLog )
    jobGraph.add_node( splineDir, data= splineNode )
    
    
    ################## SP DFT + SP SEMIEMPIRICAL #####################################
    
    for struct in structures:
        dirNo = struct.split(".")[-1]
        dirname = join( graphDir,  dirNo )
        
        dftDir = join(dirname, method)
        semiEmpDir = join(dirname, data["method"])
        
        if not isdir(dftDir):
            makedirs(dftDir)

        if not isdir(semiEmpDir):
            makedirs(semiEmpDir)
        
        dftNode = FDynamoNode("DFT-SP-"+dirNo, dftDir)
        dftNode.verification = ["SP"]
        dftNode.templateKey = "QMMM_sp_gaussian"
        dftNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
        dftNode.additionalKeywords =  {  "method" : method, "basis" : basis , "multiplicity" : 1 , "definedAtoms" : data["definedAtoms"] }
        dftNode.coordsIn = "coordsStart.crd"
        copyfile(struct, join( dftNode.path, dftNode.coordsIn ))
        dftNode.coordsOut = "coordsDone.crd"
        dftNode.flexiblePart = basename(gaussianFlexibleSele)
        copyfile( gaussianFlexibleSele, join(dftDir, dftNode.flexiblePart) )
        dftNode.processors = 24
        dftNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"
        dftNode.partition = "plgrid-short"
        dftNode.time = "1:00:00"
        dftNode.getCoordsFromParent = False
        jobGraph.add_node(dftDir, data = dftNode)
        jobGraph.add_edge(graphDir, dftDir)
        
        semiNode = FDynamoNode("SemiEmp-SP-"+dirNo, semiEmpDir)
        semiNode.verification = ["SP"]
        semiNode.templateKey = "QMMM_sp"
        semiNode.coordsIn = "coordsStart.crd"
        semiNode.coordsOut = "coordsDone.crd"
        copyfile(struct, join( semiNode.path, semiNode.coordsIn ))
        semiNode.partition = "plgrid-short"
        semiNode.time = "0:10:00"
        semiNode.getCoordsFromParent = False
        jobGraph.add_node(semiEmpDir, data = semiNode)
        jobGraph.add_edge( graphDir, semiEmpDir )
        
        splineDiff = SplineDiffNode("diff", dirname)
        jobGraph.add_node(dirname, data = splineDiff)
        
        jobGraph.add_edge( dftDir, dirname )
        jobGraph.add_edge( semiEmpDir, dirname )

        jobGraph.add_edge( dirname, splineDir )
    
    return jobGraph

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: graphSplineDYNAMO wham.log compileScanScript.sh method basis structures")
    else:
        whamLog = sys.argv[1]
        compileScript = sys.argv[2]
        method = sys.argv[3]
        basis = sys.argv[4]
        structures = sys.argv[5:]
        
        currentDir = abspath(dirname(compileScript))
        
        basisDir = basis.replace("(", "_")
        basisDir = basisDir.replace(")", "_")
        basisDir = basisDir.replace(",", "_")

        graphDir = join( getcwd(), "spline-"+method+"-"+basisDir )
        sm = GraphManager()
        graph = sm.isGraphHere(graphDir)
        if not graph:
            newGraph = buildGraph(whamLog, compileScript, method, basis, structures, currentDir, graphDir)
    
            
            result = sm.addGraph(newGraph, graphDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")