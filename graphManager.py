#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 13:25:14 2019

@author: michal
"""
from os.path import join, isfile, isdir
from jobManager import JobManager
from squeuePy import SqueueManager
import pickle
import sys
from os import mkdir
import networkx as nx

class GraphManager(JobManager):
    def __init__(self):
        JobManager.__init__(self)
        pickledGraphs = "graphs.pickle"
        self.pickledGraphs = join(self.jobManagerDir, pickledGraphs)
        
        if not isfile(self.pickledGraphs):
            self.initGraphs()
            
        self.graphs = {}
        self.loadGraphs()
        
        
    def initGraphs(self):
        file2dump = open(self.pickledGraphs, 'wb')
        pickle.dump({}, file2dump)
        file2dump.close()
        
    def loadGraphs(self):
        infile = open(self.pickledGraphs,'rb')
        self.graphs = pickle.load(infile)
        infile.close()
        
    def saveGraphs(self):
        file2dump = open(self.pickledGraphs, 'wb')
        pickle.dump(self.graphs, file2dump)
        file2dump.close()
        
    def isGraphHere(self, path):
        for graphKey in self.graphs:
            graph = self.graphs[graphKey]
            
            if path in graph.nodes:
                return graph
        else:
            return False
        
    def addGraph(self, graph, path):
        self.graphs[path] = graph
        return True
    
    def deleteGraph(self, path):
        del self.graphs[path]
        
        
    def nextIteration(self):
        sm = SqueueManager()
        results = sm.squeuePy(json = True, printResult = False)
        
        for graphKey in self.graphs:
            graph = self.graphs[graphKey]
            finishedNodes = []
            for node in graph.nodes:
                data = graph.nodes[node]["data"]
                
                if data.status == "running"  :
                    if self.jobIsFinished(data, results):
                        slurmOk, comment = data.verifySlurm()
                        if not slurmOk:
                            print("Slurm error ", node, comment)
                            continue
                        
                        logOk = data.verifyLog()
                        if not logOk:
                            print("Error in logfile ", node)
                            continue
                        
                        print("Find finished node: ")
                        print(node)
                        finishedNodes.append(node)
                        graph.nodes[node]["data"].analyseLog()
                        graph.nodes[node]["data"].status = "examined"
                elif data.status == "finished":
                    finishedNodes.append(node)
                    graph.nodes[node]["data"].analyseLog()
                    graph.nodes[node]["data"].status = "examined"
               
            children2run =set([])
            for node in finishedNodes:
                children2run |= set( graph.successors(node ))
                
            for children in children2run:
                if graph.nodes[children]["data"].status != "waitingForParent":
                    continue

                parents = list(graph.predecessors(children))
                
                allParentsFinished = True
                for p in parents:
                    if not graph.nodes[p]["data"].status == "examined":
                        allParentsFinished = False
                        
                if not allParentsFinished:
                    continue
                
                if parents:
                    self.runNode(graph, children, parents[0])
                else:
                    print("running new node: ")
                    print(node)
                    print("from existing files")
                    graph.nodes[children]["data"].run()
                
        self.saveGraphs()
                
    def jobIsFinished(self, nodeData, results):
        nodeId = nodeData.id
        nodeStatus = None
        for status in results["RunningOrWaiting"]:
            if status["jobID"] == nodeId:
                return False
                
        if not nodeStatus:
            for status in results["Finished"]:
                if status["jobID"] == nodeId:
                    return True
                
        return True
#        raise Exception("Job is lost!")
                    
        
    def runNode(self, graph, node, parent):
        print("generating new node: ")
        print(node)
        print(" from parent: ")
        print(graph.nodes[parent]["data"].logFile )
        
        graph.nodes[node]["data"].generateFromParent(graph.nodes[parent]["data"])
        graph.nodes[node]["data"].run()
        
    def buildGraphDirectories(self, graph):
        for node in nx.topological_sort(graph):
            if not isdir(node):
                print("creating: ", node)
                mkdir(node)
            else:
                print("already exist: ", node)
        
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphs run")
    elif len(sys.argv) == 2:
        sm = GraphManager()
        sm.nextIteration()
    else:
        print( "cooooo?")