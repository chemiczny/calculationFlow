#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:57:02 2019

@author: michal
"""

import networkx as nx
from os import getcwd, mkdir
from os.path import join, isdir
from jobNode import GaussianNode
from parsers import getGaussianInpFromSlurmFile

def addSPcorrections(graph, node):
    newDir = join(node, "TZ")
    newNode = GaussianNode("tz.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "PCM")
    newNode = GaussianNode("pcm.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-31G(d,p)
# nosymm SCRF(Solvent=Generic, Read)
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
    
    newDir = join(node, "TZ_PCM")
    newNode = GaussianNode("tz_pcm.inp", newDir)
    newNode.routeSection = """
%Chk=checkp.chk
%Mem=100GB
#P B3LYP/6-311+G(2d,2p)
# nosymm
# Gfinput IOP(6/7=3)  Pop=full  Density  Test 
# Units(Ang,Deg)"""
    newNode.additionalSection = """
stoichiometry=H2O1
solventname=Water2
eps=4
epsinf=1.77556"""
    newNode.verification = "SP"
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)

def addZPE(graph, node):
    newDir = join(node, "freq")
    newNode = GaussianNode("freq.inp", newDir)
    graph.add_node(newDir, data = newNode)
    graph.add_edge(node, newDir)
            

jobGraph = nx.DiGraph()
slurmFile = "test.slurm"
currentDir = getcwd()
gaussianFile = getGaussianInpFromSlurmFile(slurmFile)


newNode = GaussianNode(gaussianFile, currentDir)
jobGraph.add_node( currentDir , data = newNode )

newDir = join(currentDir, "freq")
newNode = GaussianNode("freq.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(currentDir, newDir)

lastDir, newDir = newDir, join(newDir, "ts_opt")
newNode = GaussianNode("ts_opt.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(lastDir, newDir)

lastDir, newDir = newDir, join(currentDir, "freq_verify")
newNode = GaussianNode("freq_verify.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(lastDir, newDir)

addSPcorrections(jobGraph, newDir)

optimizedTs = newDir

newDir = join(currentDir, "irc_reverse")
newNode = GaussianNode("irc_reverse.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(optimizedTs, newDir)

lastDir , newDir = newDir,  join(newDir, "opt")
newNode = GaussianNode("opt.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(lastDir, newDir)

addSPcorrections(jobGraph, newDir)
addZPE(jobGraph, newDir)

newDir = join(currentDir, "irc_forward")
newNode = GaussianNode("irc_forward.inp", newDir)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(optimizedTs, newDir)

lastDir , newDir = newDir,  join(newDir, "opt")
newNode = GaussianNode("opt.inp", None)
jobGraph.add_node(newDir, data = newNode)
jobGraph.add_edge(lastDir, newDir)

addSPcorrections(jobGraph, newDir)
addZPE(jobGraph, newDir)

#buildGraphDirectories(jobGraph)
