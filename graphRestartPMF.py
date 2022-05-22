#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 23:27:46 2019

@author: michal
"""

from graphManager import GraphManager
from os import makedirs
from os.path import join, isdir
import sys
from shutil import move, copyfile
from copy import deepcopy

def count_lines(file_path):
    lines_no = 0
    with open(file_path, 'r') as fl:
        line = fl.readline()

        while line:
            lines_no += 1
            line = fl.readline()

    return lines_no

def restart_PMF_node(graph, node, steps2calculate):
    data = graph.nodes[node]["data"]

    newNodeData = deepcopy(data)
    newNodeData.path = newNodeData.path + "_continue" 
    newNodeData.status = "waitingForParent"
    newNodeData.id = None
    newNodeData.getCoordsFromParent = True
    newNodeData.additionalKeywords["pmfSteps"] = steps2calculate
    newNodeData.anotherCoordsSource = data.coordsIn
    newNode = newNodeData.path
    newNodeData.verification.append("PMF_restart")

    print("creating: ", newNode)
    if not isdir(newNode):
        makedirs(newNode)

    copyfile(  join(data.path, data.slurmFile), join( newNodeData.path, newNodeData.slurmFile ) )
    move( join(data.path, "pmf.dat"), join(newNodeData.path, "pmf_timeout.dat") )

    data.status = "finished"
    data.readResults = False
    
    graph.add_node(newNodeData.path, data = newNodeData)
    
    successors = list(graph.successors(node))
    for s in successors:
        graph.add_edge(newNode, s)
        graph.remove_edge(node, s)
        
    graph.add_edge(node, newNode)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: graphRestartPMF graph")
    else:
        sm = GraphManager()
        path = sys.argv[-1]
        graph = sm.isGraphHere(path)

        if not graph:
            print("There is no graph!")
            quit()

        nodes2restart = []
        for node in graph.nodes:
            nodeData = graph.nodes[node]["data"]
            if not hasattr(nodeData, "templateKey"):
                continue

            if nodeData.templateKey != "QMMM_pmf":
                continue

            if nodeData.status != "failed":
                continue

            print("Found failed PMF node to analyse:", node)
            nodes2restart.append(node)

        for node in nodes2restart:
            pmf_result_file = join(node, "pmf.dat")
            steps_executed = count_lines(pmf_result_file) - 1
            steps2calculate = 40000-steps_executed

            restart_PMF_node(graph, node, steps2calculate)




        sm.saveGraphs()

