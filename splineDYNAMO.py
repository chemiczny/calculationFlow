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

class SplineDiffNode(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
        
        self.dftValue = None
        self.semiEmpiricalValue = None
        self.reactionCoordinate = None
        self.diff = None
        
    def generateFromParents(self, graph, parents):
        for p in parents:
            parentData = graph.nodes[p]["data"]
            
            if "gaussian" in parentData.templateKey:
                parentData.analyseLog()
                self.dftValue = parentData.QMenergy
                inputCoords = join(parentData.path, parentData.coordsIn)
                self.reactionCoordinate = parentData.measureRC(inputCoords)
                
            else:
                parentData.analyseLog()
                self.semiEmpiricalValue = parentData.PotentialEnergy
                
        self.diff = self.dftValue - self.semiEmpiricalValue
        
    def run(self):
        self.status = "finished"
        
class SplineNode(JobNode):
    def __init__(self, inputFile, path, whamLog):
        JobNode.__init__(self,inputFile, path)
        self.whamLog = whamLog
        
    def generateFromParents(self, graph, parents):
        copyfile( self.whamLog, join(self.pathm, "wham.log" ) )
        
        sortedParents = sorted( parents, key = lambda x: graph.nodes[x]["data"].reactionCoordinate  )
        offset = min( [ graph.nodes[p]["data"].diff for p in parents   ] )
        
        logF = open( join( self.path, "diff.log" ) , 'w' )
        
        for p in sortedParents:
            parent = graph.nodes[p]["data"]
            logF.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.diff - offset ) )
        
        logF.close()
        
    def run(self):
        self.status = "finished"
        

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
    rootNode = JobNode(None, graphDir)
    rootNode.status = "finished"
    
    rootNode.fDynamoPath = data["fDynamoPath"]
    rootNode.charge = data["charge"]
    rootNode.method = data["method"]
    rootNode.forceField = data["forceField"]
    copyfile( join(data["filesDir"], data["forceField"]), join(graphDir, rootNode.forceField) )
    rootNode.flexiblePart = data["flexiblePart"]
    copyfile( join(data["filesDir"], data["flexiblePart"]), join(graphDir, rootNode.flexiblePart) )
    rootNode.sequence = data["sequence"]
    copyfile( join(data["filesDir"], data["sequence"]), join(graphDir, rootNode.sequence) )
    rootNode.qmSele = data["qmSele"]
    
    jobGraph.add_node(graphDir, data = rootNode)
    
    ########### SPLINE NODE ####################
    splineDir = join( graphDir, "spline" )
    splineNode = SplineNode(None, splineDir )
    jobGraph.add_node( splineDir, data= splineNode )
    
    
    ################## SP DFT + SP SEMIEMPIRICAL #####################################
    
    for struct in structures:
        dirNo = struct.split(".")[-1]
        dirname = join( graphDir,  dirNo )
        
        dftDir = join(dirname, method)
        semiEmpDir = join(dirname, data["method"])
        
        if not isdir(dftDir):
            makedirs(dftDir)
        
        dftNode = FDynamoNode("DFT-SP-"+dirNo, dftDir)
        dftNode.verification = ["SP"]
        dftNode.templateKey = "QMMM_sp_gaussian"
        dftNode.fDynamoPath = "/net/people/plgglanow/fortranPackages/AMBER-g09/AMBER-dynamo/makefile"
        dftNode.additionalKeywords =  {  "method" : method, "basis" : basis , "multiplicity" : 1 , "definedAtoms" : data["definedAtoms"] }
        dftNode.coordsIn = "coordsStart.crd"
        dftNode.coordsOut = "coordsDone.crd"
        dftNode.flexiblePart = basename(gaussianFlexibleSele)
        copyfile( gaussianFlexibleSele, join(dftDir, dftNode.flexiblePart) )
        dftNode.processors = 24
        dftNode.moduleAddLines = "module add plgrid/apps/gaussian/g16.B.01"
        dftNode.partition = "plgrid-short"
        dftNode.time = "1:00:00"
        jobGraph.add_node(dftDir, data = dftNode)
        jobGraph.add_edge(graphDir, dftDir)
        
        semiNode = FDynamoNode("SemiEmp-SP-"+dirNo, semiEmpDir)
        semiNode.verification = ["SP"]
        semiNode.templateKey = "QMMM_sp"
        semiNode.coordsIn = "coordsStart.crd"
        semiNode.coordsOut = "coordsDone.crd"
        semiNode.partition = "plgrid-short"
        semiNode.time = "0:10:00"
        jobGraph.add_node(semiEmpDir, data = semiNode)
        jobGraph.add_edge( graphDir, semiEmpDir )
        
        splineDiff = SplineDiffNode("diff", dirname)
        jobGraph.add_node(dirname, data = splineDiff)
        jobGraph.add_edge(graphDir, dirname)
        
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
        
        graphDir = join( getcwd(), "spline-"+method )
        sm = GraphManager()
        graph = sm.isGraphHere(graphDir)
        if not graph:
            newGraph = buildGraph(whamLog, compileScript, method, basis, structures, currentDir, graphDir)
    
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")