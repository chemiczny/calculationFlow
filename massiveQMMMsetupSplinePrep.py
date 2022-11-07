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
        copyfile( join( rootDir, basename(crd) ), join(coolDirName, basename(crd)) )

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
        qmmmOptNode.additionalKeywords = {"gradientTolerance" : "0.1"}

        jobGraph.add_node( qmmmOptDir, data = qmmmOptNode )
        jobGraph.add_edge( qmmmSetupDirName, qmmmOptDir)

        qmmmScanDir = join(qmmmSetupDirName, "scan")
        qmmmScanNode = FDynamoNode("scan.f90", qmmmScanDir)
        qmmmScanNode.verification = [ "scan1D" ]
        qmmmScanNode.readInitialScanCoord = True
        qmmmScanNode.templateKey = "QMMM_scan1D_mopac"
        qmmmScanNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "1.0",
        	"iterNo" : "80", "definedAtoms" : definedAtoms, "constraints" : constraints }

        jobGraph.add_node( qmmmScanDir, data = qmmmScanNode )
        jobGraph.add_edge( qmmmOptDir, qmmmScanDir)

        qmmmTSoptDir = join(qmmmSetupDirName, "ts_search")
        qmmmTSoptNode = FDynamoNode("tsSearch.f90", qmmmTSoptDir)
        qmmmTSoptNode.partition = "plgrid"
        qmmmTSoptNode.time = "3:00:00"
        qmmmTSoptNode.verification = ["Opt" , "Freq"]
        qmmmTSoptNode.noOfExcpectedImaginaryFrequetions = 1
        qmmmTSoptNode.templateKey = "QMMM_opt_mopac"
        qmmmTSoptNode.coordsIn = "coordsStart.crd"
        qmmmTSoptNode.coordsOut = "coordsDone.crd"
        qmmmTSoptNode.additionalKeywords = {"gradientTolerance" : "1.0", "ts_search" : "true"}

        jobGraph.add_node( qmmmTSoptDir, data = qmmmTSoptNode )
        jobGraph.add_edge( qmmmScanDir, qmmmTSoptDir)

        stepOptDir = join(qmmmSetupDirName, "tsTightOpt")

        stepOptNode = FDynamoNode("optStep.f90", stepOptDir)
        stepOptNode.verification = ["Opt"]
        stepOptNode.partition = "plgrid-short"
        stepOptNode.time = "1:00:00"
        stepOptNode.templateKey = "QMMM_opt_mopac_no_hess_restr"
        stepOptNode.readInitialScanCoord = True
        stepOptNode.additionalKeywords = {  "coordScanStart" : "" , "definedAtoms" : definedAtoms,  "constraints" : constraints, "gradientTolerance" : "0.1"}

        jobGraph.add_node(stepOptDir, data = stepOptNode)
        jobGraph.add_edge( qmmmTSoptDir, stepOptDir)


        reverseScanDir = join(qmmmSetupDirName, "TS1reverseScan1")
    
        newScanNode = FDynamoNode("scan.f90", reverseScanDir)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(15), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        newScanNode.coordsOut = "seed.-15"
        
        jobGraph.add_node(reverseScanDir, data = newScanNode)
        jobGraph.add_edge( stepOptDir, reverseScanDir)


        reverseScanDir2 = join(qmmmSetupDirName, "TS1reverseScan2")
    
        newScanNode = FDynamoNode("scan.f90", reverseScanDir2)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(16), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        newScanNode.coordsOut = "seed.-16"
        
        jobGraph.add_node(reverseScanDir2, data = newScanNode)
        jobGraph.add_edge( reverseScanDir, reverseScanDir2)

        reverseScanDir3 = join(qmmmSetupDirName, "TS1reverseScan3")
    
        newScanNode = FDynamoNode("scan.f90", reverseScanDir3)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "-", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(11), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        
        jobGraph.add_node(reverseScanDir3, data = newScanNode)
        jobGraph.add_edge( reverseScanDir2, reverseScanDir3)


        forwardScanDir = join(qmmmSetupDirName, "TS1forwardScan1")
    
        newScanNode = FDynamoNode("scan.f90", forwardScanDir)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(15), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        newScanNode.coordsOut = "seed.+15"
        
        jobGraph.add_node(forwardScanDir, data = newScanNode)
        jobGraph.add_edge( stepOptDir, forwardScanDir)

        forwardScanDir2 = join(qmmmSetupDirName, "TS1forwardScan2")
    
        newScanNode = FDynamoNode("scan.f90", forwardScanDir2)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(16), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        newScanNode.coordsOut = "seed.+16"
        
        jobGraph.add_node(forwardScanDir2, data = newScanNode)
        jobGraph.add_edge(forwardScanDir, forwardScanDir2)

        forwardScanDir3 = join(qmmmSetupDirName, "TS1forwardScan3")
    
        newScanNode = FDynamoNode("scan.f90", forwardScanDir3)
        newScanNode.verification = ["SP"]
        newScanNode.templateKey = "QMMM_scan1D_mopac"
        newScanNode.readInitialScanCoord = True
        newScanNode.additionalKeywords = { "scanDir" : "+", "coordScanStart" : "" , "gradientTolerance" : "0.1",
             "iterNo" : str(11), "definedAtoms" : definedAtoms,  "constraints" : constraints}
        newScanNode.coordsIn = "coordsStart.crd"
        
        jobGraph.add_node(forwardScanDir3, data = newScanNode)
        jobGraph.add_edge(forwardScanDir2, forwardScanDir3)

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