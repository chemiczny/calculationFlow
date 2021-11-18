import sys
from graphManager import GraphManager
from os import getcwd, makedirs
from os.path import join, basename
import networkx as nx
from amberNode import AmberNode
from fDynamoJobNode import FDynamoNode
from parsers import parseFDynamoCompileScript
from shutil import copyfile, move
from QMMMsetupNode import QMMMsetupNode
from jobNode import JobNode

def solventInLine(line):
    if "WAT" in line:
        return True
    
    if "CL-" in line:
        return True
    
    if "NA+" in line:
        return True
    
def countNoSolventInLine(line):
    noSolvent = 0
    
    for res in line.split():
        if not res in [ "WAT" , "NA+", "CL-" ]:
            noSolvent += 1
            
    return noSolvent

def getNumberOfNotSolventRes(topologyFile):
    noSolventRes = 0
    
    topF = open(topologyFile, 'r')
    
    line = topF.readline()
    
    while line and not "%FLAG RESIDUE_LABEL" in line:
        line = topF.readline()
    
    topF.readline()
    line = topF.readline().upper()
    
    while not solventInLine(line):
        noSolventRes += countNoSolventInLine(line)
        line = topF.readline().upper()
        
    noSolventRes += countNoSolventInLine(line)
    topF.close()
    
    return noSolventRes


def generateGraph(topologyFile, forcefield, compileScript, coordinates):
    jobGraph = nx.DiGraph()
    rootDir = getcwd()
    
    notSolventNo = getNumberOfNotSolventRes(topologyFile)

    data = parseFDynamoCompileScript(compileScript)

    newNode = JobNode(None, rootDir)
    newNode.status = "finished"
    jobGraph.add_node(rootDir, data = newNode)

    for crd in coordinates:
        coolDirName = join( rootDir, basename(crd).replace(".", "_") )
        makedirs(coolDirName)

        copyfile( join( rootDir, basename(topologyFile) ), join(coolDirName, basename(topologyFile)) )
        move( join( rootDir, basename(crd) ), join(coolDirName, basename(crd)) )

        coolNode = AmberNode("amber.slurm", coolDirName, coolDirName, basename(topologyFile), basename(crd))
        coolNode.runType = "standardCooling"
        coolNode.time = "1:00:00"
        coolNode.partition = "plgrid-short"
        coolNode.processors = 8
        jobGraph.add_node( coolDirName, data = coolNode )
        jobGraph.add_edge(rootDir, coolDirName)

        optimDir = join( coolDirName, "MM_opt")
        optimNode = AmberNode("amber.slurm", optimDir, optimDir, topologyFile)
        optimNode.NoSolventResidues = notSolventNo
        optimNode.runType = "standardOptimization"
        optimNode.time = "1:00:00"
        optimNode.partition = "plgrid-short"
        jobGraph.add_node( optimDir, data = optimNode )
        jobGraph.add_edge( coolDirName, optimDir)

        qmmmSetupDirName = join( coolDirName, "QMMM_setup")
        qmmmSetupNode = QMMMsetupNode("qmmmSetup.slurm", qmmmSetupDirName, basename(topologyFile), "cooled.nc")
        jobGraph.add_node( qmmmSetupDirName, data = qmmmSetupNode )
        jobGraph.add_edge( optimDir, qmmmSetupDirName)

        qmmmOptDir = join(qmmmSetupDirName, "opt")
        makedirs(qmmmOptDir)
        copyfile( join( rootDir, basename(forcefield) ), join(qmmmOptDir, basename(forcefield)) )

        definedAtoms = data["definedAtoms"]
        constraints = data["constraints"]
        qmmmOptNode = FDynamoNode(data["inputFile"], qmmmOptDir)
        qmmmOptNode.coordsIn = "coordsIn.crd"
        qmmmOptNode.coordsOut = "coordsOut.crd"
        qmmmOptNode.verification = [ "Opt" ]
        qmmmOptNode.slurmFile = None
        qmmmOptNode.autorestart = False
        qmmmOptNode.forceField = data["forceField"]
        qmmmOptNode.flexiblePart = data["flexiblePart"]
        qmmmOptNode.sequence = data["sequence"]
        qmmmOptNode.qmSele = data["qmSele"]
        qmmmOptNode.templateKey = "QMMM_opt_mopac_no_hess"
        qmmmOptNode.fDynamoPath = data["fDynamoPath"]
        qmmmOptNode.charge = data["charge"]
        qmmmOptNode.method = data["method"]

        jobGraph.add_node( qmmmOptDir, data = qmmmOptNode )
        jobGraph.add_edge( qmmmSetupDirName, qmmmOptDir)

        qmmmScanDir = join(qmmmSetupDirName, "scan")
        qmmmScanNode = FDynamoNode("scan.f90", qmmmScanDir)
        qmmmScanNode.verification = [ "scan1D" ]
        qmmmScanNode.readInitialScanCoord = True
        qmmmScanNode.templateKey = "QMMM_scan1D_mopac"
        qmmmScanNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" ,
        	"iterNo" : "80", "definedAtoms" : definedAtoms, "constraints" : constraints }

        jobGraph.add_node( qmmmScanDir, data = qmmmScanNode )
        jobGraph.add_edge( qmmmOptDir, qmmmScanDir)

        qmmmTSoptDir = join(qmmmSetupDirName, "ts_search")
        qmmmTSoptNode = FDynamoNode("tsSearch.f90", qmmmTSoptDir)
        qmmmTSoptNode.verification = ["Opt" , "Freq"]
        qmmmTSoptNode.noOfExcpectedImaginaryFrequetions = 1
        qmmmTSoptNode.templateKey = "QMMM_opt_mopac"
        qmmmTSoptNode.additionalKeywords = { "ts_search" : "true" }
        qmmmTSoptNode.coordsIn = "coordsStart.crd"
        qmmmTSoptNode.coordsOut = "coordsDone.crd"

        jobGraph.add_node( qmmmTSoptDir, data = qmmmTSoptNode )
        jobGraph.add_edge( qmmmScanDir, qmmmTSoptDir)

    return jobGraph


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("graphMassiveQMMMsetup topology file, forcefield, compile script, amber coordinates")
    else:
        sm = GraphManager()
        currentDir = getcwd()
        graph = sm.isGraphHere(currentDir)
        
        topology = sys.argv[1]
        forcefield = sys.argv[2]
        compileScript = sys.argv[3]
        coordinates = sys.argv[4:]
        if not graph:
            newGraph = generateGraph(topology, forcefield, compileScript, coordinates)
            
            result = sm.addGraph(newGraph, currentDir)
            if result:
                sm.buildGraphDirectories(newGraph)
                sm.saveGraphs()
            print("Created new graph")
        else:
            print("Cannot create more than one graph in the same directory")