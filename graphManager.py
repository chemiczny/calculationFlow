#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 13:25:14 2019

@author: michal
"""
from os.path import join, isfile, isdir
from jobManager import JobManager
#from jobNode import
from gaussianNode import GaussianNode
from squeuePy import SqueueManager
from copy import deepcopy
from shutil import copyfile
import pickle
import sys
from os import makedirs
import networkx as nx
from collections import defaultdict

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
        
#    def setCurrentNodeAsFinished
        
    def restartNode(self, path):
        graph = self.isGraphHere(path)
        
        if not graph:
            print("There is no graph here!")
            return
        
        data = graph.nodes[path]["data"]
        
        newNodeData = deepcopy(data)
        newNodeData.path = join( newNodeData.path, "restart" )
        newNodeData.skipParentAdditionalSection = False
        newNodeData.additionalSection = "" 
        newNodeData.status = "waitingForParent"
        newNodeData.id = None
        newNodeData.getCoordsFromParent = True
        newNode = newNodeData.path

        if not isdir(newNode):
            print("creating: ", newNode)
            makedirs(newNode)

        copyfile(  join(data.path, data.slurmFile), join( newNodeData.path, newNodeData.slurmFile ) )
        
        data.status = "finished"
        data.readResults = False
        
        graph.add_node(newNodeData.path, data = newNodeData)
        
        successors = list(graph.successors(path))
        for s in successors:
            graph.add_edge(newNode, s)
            graph.remove_edge(path, s)
            
        graph.add_edge(path, newNode)
        
        print("Graph has been modified")
        
    def printNodeAttributes(self, path):
        graph = self.isGraphHere(path)
        
        if not graph:
            print("There is no graph here!")
            return
        
        data = graph.nodes[path]["data"]
        dataDict = vars(data)
        
        for key in dataDict:
            print(key," : ", dataDict[key])

        print("Node successors:")
        successors = list(graph.successors(path))
        for s in successors:
            print(s)

        print("Node predecessors")
        predecessors = list( graph.predecessors(path) )
        for p in predecessors:
            print(p)
        
        
    def addGraph(self, graph, path):
        self.graphs[path] = graph
        return True
    
    def addNewNode(self, parentPath, newNodePath, slurmFile, inputFile, status = "waitingForParent"):
        graph = self.isGraphHere(parentPath)
        if not graph:
            print("Invalid graph key:")
            print(parentPath)
            return
        
        if not status in [ "waitingForParent" , "running" , "finished" , "examined" ]:
            print("Invalid status!")
            return
        
        if status == "waitingForParent":
            graph.nodes[parentPath]["data"].status = "finished"
            
        newNode = GaussianNode(inputFile, newNodePath)
        newNode.verification = "SP"
        newNode.readResults = True
        newNode.slurmFile = slurmFile
        newNode.getCoordsFromParent = False
        newNode.status = status
        graph.add_node( newNodePath , data = newNode )
        graph.add_edge(parentPath, newNodePath)
    
    def insertPath2node(self, oldPath, newPath, slurmFile, inputFile, status = "waitingForParent"):
        graph = self.isGraphHere(oldPath)
        if not graph:
            print("Invalid graph key:")
            print(oldPath)
            return
        
        if not status in [ "waitingForParent" , "running" , "finished" , "examined" ]:
            print("Invalid status!")
            return
        
        data = graph.nodes[oldPath]["data"]
        data.rebuild(inputFile, newPath, slurmFile)
        data.getCoordsFromParent = False
        
        nx.relabel_nodes(graph, { oldPath : newPath }, False)
        
        # test = data.verifyLog()
        # if not test:
        #     print("something wrong with this node:")
        #     print(newPath)
            
        data.status = status
        
        if status == "waitingForParent":
            for p in graph.predecessors(newPath):
                graph.nodes[p]["data"].status = "finished"
        
    def getGraphStatus(self, graphKey):
        status = defaultdict(int)
        
        for node in self.graphs[graphKey].nodes:
            graph = self.graphs[graphKey]
            status[graph.nodes[node]["data"].status] += 1
            
        return status
    
    def printStatus(self, long = False, graphKey = None):
        if not graphKey:
            print(70*"#")
            print("Actual graphs status:")
            print("No of graphs: ", len(self.graphs))
            for graphKey in self.graphs:
                print("Graph key: ", graphKey)
                if long:
                    print("nodes state:")
                    graph = self.graphs[graphKey]
                    for node in graph.nodes:
                        print(node, graph.nodes[node]["data"].status)
                else:
                    status = self.getGraphStatus(graphKey)
                    for key in sorted(list(status.keys())):
                        print( key, " : ", status[key] )
                    
                    
                print(70*"#")
        else:
            graph = None
            if graphKey in self.graphs:
                graph = self.graphs[graphKey]
                print("Read graph from graph manager")
            elif isfile(graphKey):
                infile = open(graphKey,'rb')
                graph = pickle.load(infile)
                infile.close()
                print("Read graph from file")
            else:
                print("Invalid graphKey!")
                return
            
            print(70*"#")
            print("Actual graph status:")
            print("Graph key: ", graphKey)
            print("nodes state:")
            for node in graph.nodes:
                print(node, graph.nodes[node]["data"].status)
            print(70*"#")
    
    def printResults(self, path, force = False):
        print(70*"#")
              
        graph = None
        if path in self.graphs:
            graph = self.graphs[path]
            print("Read graph from graph manager")
        elif isfile(path):
            infile = open(path,'rb')
            graph = pickle.load(infile)
            infile.close()
            print("Read graph from file")
        else:
            print("Invalid graphKey!")
            return
        
        for node in graph.nodes:
            data = graph.nodes[node]["data"]
            
            if hasattr(data, "measuredDistances"):
                if data.measuredDistances:
                    print("Distances: ")
                    print(node)
                    
                for key in data.measuredDistances:
                    print(key, data.measuredDistances[key])
                
            
            if not hasattr(data, "readResults"):
                continue
            
            if not data.readResults:
                continue
            
            if data.status != "examined":
                print(node)
                print("Result not available, node status: ", data.status)
                continue
            
            if not data.results or force:
                data.results = []
                data.analyseLog()
                
            print(node)
            for res in data.results:
                print(res)
                
                
        print(70*"#")
    
    def deleteGraph(self, path):
        if path in self.graphs:
            del self.graphs[path]
        else:
            print("Invalid graphKey: ", path)
            
    def saveGraph(self, path, destiny):
        if not path in self.graphs:
            print("Invalid graphKey: ", path)
            return
        
        file2dump = open(destiny, 'wb')
        pickle.dump(self.graphs[path], file2dump)
        file2dump.close()
        
    def graphIteration(self, graphKey, results):
        print("Analysing graph: ")
        print(graphKey)
        graph = self.graphs[graphKey]
        finishedNodes = []
        nodes2restart = []
        for node in graph.nodes:
            data = graph.nodes[node]["data"]
            
            if data.status == "running"  :
                jobFailed = False
                
                if self.jobIsFinished(data, results):
                    try:
                        slurmOk, comment = data.verifySlurm()
                        if not slurmOk:
                            print("Slurm error ", node, comment)
                            jobFailed = True
                    except:
                        print("Cannot verify slurm file")
                    
                    try:
                        logOk = data.verifyLog()
                        if not logOk:
                            print("Error in logfile ", node)
                            jobFailed = True
                    except:
                        print("Cannot verify log file: "+node)
                        
                    if jobFailed:
                        if hasattr(data, "autorestart"):
                            if data.autorestart:
                                restartJob = data.shouldBeRestarted()
                                if restartJob:
                                    nodes2restart.append(node)
                            else:
                                continue
                        else:
                            continue
                    
                    print("Find finished node: ")
                    print("\t",node)
                    finishedNodes.append(node)
                    graph.nodes[node]["data"].analyseLog()
                    graph.nodes[node]["data"].status = "examined"
            elif data.status == "finished":
                print("Find finished node: ")
                print("\t",node)
                finishedNodes.append(node)
                # graph.nodes[node]["data"].analyseLog()
                graph.nodes[node]["data"].status = "examined"
                print("Node has been examined")
           
        if nodes2restart:
            print("Restarting nodes...")
            
        for node in nodes2restart:
            self.restartNode(node)
            finishedNodes.append(node)
            graph.nodes[node]["data"].status = "examined"
            
        children2run =set([])
        for node in finishedNodes:
            children2run |= set( graph.successors(node ))
            
            
        if not children2run:
            if graph.nodes[graphKey]["data"].status == "waitingForParent":
                   children2run.add(graphKey)

            
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
                if len(parents) == 1:
                    self.runNode(graph, children, parents[0])
                else:                            
                    self.runNodeFromParents(graph, children, parents)
            else:
                print("running new node: ")
                print("\t",children)
                print("from existing files")
                graph.nodes[children]["data"].run()
        
    def nextIteration(self, selectedGraph = ""):
        sm = SqueueManager()
        results = sm.squeuePy(json = True, printResult = False)
        
        if not selectedGraph:
            for graphKey in self.graphs:
                self.graphIteration(graphKey, results)
                print("")
        else:
            if not selectedGraph in self.graphs:
                print("Wrong graph key!")
                return
            
            self.graphIteration(selectedGraph, results)
                
        self.saveGraphs()
                
    def jobIsFinished(self, nodeData, results):
        nodeId = nodeData.id
#        nodeStatus = None
        for status in results["RunningOrWaiting"]:
            if status["jobID"] == nodeId:
                return False
                
#        if not nodeStatus:
#            for status in results["Finished"]:
#                if status["jobID"] == nodeId:
#                    return True
                
        return True
#        raise Exception("Job is lost!")
                    
        
    def runNode(self, graph, node, parent):
        print("generating new node: ")
        print("\t",node)
        print(" from parent: ")
        print("\t",parent, graph.nodes[parent]["data"].logFile )
        
        graph.nodes[node]["data"].generateFromParent(graph.nodes[parent]["data"])
        graph.nodes[node]["data"].run()
        
    def runNodeFromParents(self, graph, node, parents):
        print("generating new node: ")
        print("\t",node)
        print(" from parents")
        
        graph.nodes[node]["data"].generateFromParents(graph, parents)
        graph.nodes[node]["data"].run()
        
    def buildGraphDirectories(self, graph):
        for node in nx.topological_sort(graph):
            if not isdir(node):
                print("creating: ", node)
                makedirs(node)
            else:
                print("already exist: ", node)
        
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: graphRun next graphKey [optional]")
    elif len(sys.argv) == 2:
        sm = GraphManager()
        sm.nextIteration()
    elif len(sys.argv) == 3:
        sm = GraphManager()
        path = sys.argv[-1]
        sm.nextIteration(path)
#        sm.restartNode(path)
        sm.saveGraphs()
    else:
        print( "cooooo?")