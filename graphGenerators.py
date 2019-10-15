#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 12:55:34 2019

@author: michal
"""
from os.path import join
from jobNode import GaussianNode

def addSPcorrections(graph, node):
    newDir = join(node, "TZ")
    newNode = GaussianNode("tz.log", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.verification = "SP"
    newNode.readResults = True
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "PCM")
    newNode = GaussianNode("pcm.log", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# nosymm SCRF(Solvent=Generic, Read)
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556
"""
    newNode.verification = "SP"
    newNode.readResults = True
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "TZ_PCM")
    newNode = GaussianNode("tz_pcm.log", newDir)
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556
"""
    newNode.verification = "SP"
    newNode.readResults = True
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
def addZPE(graph, node, expectedImaginaryFreqs = 0):
    newDir = join(node, "freq")
    newNode = GaussianNode("freq.inp", newDir)
    newNode.verification = "Freq"
    newNode.readResults = True
    newNode.routeSection = """%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# Freq nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)
"""
    newNode.noOfExcpectedImaginaryFrequetions = expectedImaginaryFreqs
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)