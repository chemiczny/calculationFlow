#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 12:55:34 2019

@author: michal
"""
from os.path import join
from gaussianNode import GaussianNode

def addSPcorrections(graph, node, theoryLow = "B3LYP/6-31G(d,p)", theoryHigh = "B3LYP/6-311+G(2d,2p)", basename = "", additionalRoute = ""):
    newDir = join(node, basename+"TZ")
    newNode = GaussianNode("tz.inp", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theoryHigh+"""
# nosymm """+additionalRoute+"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.verification = "SP"
    newNode.readResults = True
    newNode.time = "72:00:00"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, basename+"PCM")
    newNode = GaussianNode("pcm.inp", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theoryLow+"""
# nosymm SCRF(Solvent=Water, Read) """+additionalRoute+"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
eps=4
"""
    newNode.verification = "SP"
    newNode.readResults = True
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, basename+"TZ_PCM")
    newNode = GaussianNode("tz_pcm.inp", newDir)
    newNode.time = "24:00:00"
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theoryHigh+"""
# nosymm SCRF(Solvent=Water, Read) """+additionalRoute+"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
eps=4
"""
    newNode.verification = "SP"
    newNode.readResults = True
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    
def addZPE(graph, node, expectedImaginaryFreqs = 0, theory = "B3LYP/6-31G(d,p)", basename = "", structure2dump = "",
           additionalSection = "", additionalRouteSection = ""):
    newDir = join(node, basename + "freq")
    newNode = GaussianNode("freq.inp", newDir)
    newNode.verification = "Freq"
    newNode.readResults = True
    newNode.structure2dump = structure2dump
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P """+theory+"""
# Freq nosymm """+ additionalRouteSection +"""
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.noOfExcpectedImaginaryFrequetions = expectedImaginaryFreqs
    newNode.additionalSection = additionalSection
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)