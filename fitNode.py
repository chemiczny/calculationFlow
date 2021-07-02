from networkx.algorithms.isomorphism import GraphMatcher
import numpy as np
import math
from jobNode import JobNode
from os.path import join, isfile, abspath, basename, dirname
from os import getcwd
import networkx as nx
from shutil import copyfile
import sys

class moleculeMatcher(GraphMatcher):
    def semantic_feasibility(self, G1_node, G2_node):
        return self.G1.node[G1_node]["element"] == self.G2.node[G2_node]["element"]
    
class Atom:
    def __init__(self, coords, element, atomId = "unk", atomType = "unk", charge = 0):
        self.coords = coords
        self.element = element
        self.atomId = atomId
        self.atomType = atomType
        self.charge = charge
        
def readXYZ(xyzFilename):
    xyz = open(xyzFilename, 'r')
    atomsNo  = int(xyz.readline())
    
    atoms = []
    line = xyz.readline()
    
    for i in range(atomsNo):
        line = xyz.readline()
        
        line = line.split()
        element = line[0]
        
        coords = [ float(c) for c in line[-3:]]
        atoms.append(Atom(np.array(coords), element))
    
    xyz.close()
    return atoms
        
def readMol2( mol2File ):
    mol2 = open(mol2File, 'r')
    
    line = mol2.readline()
    
    while not "ATOM" in line:
        line = mol2.readline()
        
    line = mol2.readline()
    atoms = []
    while not "BOND" in line:
        lineSpl = line.split()
        coords = [ float( coord ) for coord in lineSpl[2:5] ]
        atomId = lineSpl[1]
        element = atomId[0:1]
        atomType = lineSpl[5]
        charge = lineSpl[-1]
        atoms.append(Atom(coords, element, atomId, atomType, charge))
        
        line = mol2.readline()
        
    mol2.close()
    return atoms

def rewriteXyz( molecule, mapping, filename ):
    xyzF = open(filename, "w")
    
    xyzF.write( str(len(molecule))+"\n\n" )
    
    sortedKeys = sorted(list(mapping.keys()))
    
    for key in sortedKeys:
        atomIndex = mapping[key]
        atom = molecule[atomIndex]
        
        xyzF.write(atom.element+" ")
        coordsStr = [ str(crd) for crd in atom.coords ]
        xyzF.write(" ".join(coordsStr)+"\n")
    
    xyzF.close()

def molecule2graph(atoms):   
    thresholds = { "C" : 2, "O" : 1.65, "N" : 1.7, "S" : 2.2,
                  "F" : 1.6, "CL" : 2.0, "BR" : 2.1, "I" : 2.2 }
                  
    G = nx.Graph()

    for atom1Ind, atom1 in enumerate(atoms):
        threshold1 = 1.8
        
        element1 = atom1.element
        
        if element1 in thresholds.keys():
            threshold1 = thresholds[element1]
        
        
        for atom2Ind, atom2 in enumerate(atoms[atom1Ind+1:], atom1Ind+1):
            threshold2 = 1.8      
            element2 = atom2.element
            
            if element2 in thresholds.keys():
                threshold2 = thresholds[element2]
                
            if element1 == "H" and element2 == "H":
                continue
        
            
            distance = 0
            dist_vec = np.array(atom1.coords) - np.array(atom2.coords)
            for element in dist_vec:
                distance += element*element
                
            dist = math.sqrt(distance)
            
            threshold = max( threshold1, threshold2 )
            if dist < threshold :
                G.add_edge(atom1Ind, atom2Ind)
                G.node[atom1Ind]["element"] = element1
                G.node[atom2Ind]["element"] = element2
        
    return G

class FitNode(JobNode):
    def __init__(self, inputFile, path, templateXyz):
        JobNode.__init__(self,inputFile, path)
        self.templateAbs = abspath(templateXyz)
        self.templateBase = join(self.path, "reindexed_" + basename(self.templateAbs) )
        self.time = "0:10:00"
        
    def generateFromParent(self, parentData, mol2file = "keto.mol2"):
        gespSource = join( parentData.path, mol2file )
        
        fullMolecule = readMol2(gespSource)
        moleculeFragment = readXYZ(self.templateAbs)
        
        fullMoleculeGraph = molecule2graph(fullMolecule)
        moleculeFragmentGraph = molecule2graph(moleculeFragment)
        
        copyfile(gespSource, join(self.path, self.inputFile))
        
        gMatcher = moleculeMatcher( fullMoleculeGraph, moleculeFragmentGraph )
        
        if not gMatcher.subgraph_is_isomorphic():
            print("Error! Fragment of molecule is not isomorphic to template!!!")
            
        mapping = gMatcher.mapping
        
        rewriteXyz(moleculeFragment, mapping, self.templateBase)
        
        
#        copyfile( self.templateAbs,  self.templateBase )
        
        self.generateTclSrcipt(mapping)
        self.writeSlurmScript("run.slurm")
    
    def generateTclSrcipt(self, mapping):
        scriptTemplate = """
set mol2id [ mol new "{mol2source}" type "mol2" first 0 last -1 step 1 waitfor 1 ]
set templateId [ mol new "{template}" type "xyz" first 0 last -1 step 1 waitfor 1 ]


set templateSel [ atomselect $templateId "all" ]
set indexes "{indexes}"
set mol2sel [ atomselect $mol2id "index $indexes" ]

set transformation_matrix [measure fit $mol2sel $templateSel]
set mol2fullSel [ atomselect $mol2id "all" ]
$mol2fullSel move $transformation_matrix

animate write mol2 "{mol2out}" beg 0 end 0 skip 1 $mol2id
exit     
"""
        indexes = [ str(ind) for ind in mapping.keys() ]
        replaceDict = { "mol2source" : self.inputFile, "template" : self.templateBase, "mol2out" : "keto_fitted.mol2",
                       "indexes" : " ".join(indexes)}
        
        script = scriptTemplate.format( **replaceDict )
        scriptF = open( join(self.path, "fit.tcl"), 'w')
        scriptF.write(script)
        scriptF.close()
    
    
    def writeSlurmScript( self, filename):
        fullPath = join(self.path, filename)
        slurmFile = open(fullPath, 'w')
        
        slurmConfig = self.readSlurmConfig()
        
        if not "firstLine" in slurmConfig:
            slurmFile.write("#!/bin/env bash\n")
        else:
            slurmFile.write(slurmConfig["firstLine"]+"\n")
            
        slurmFile.write("#SBATCH --nodes=1\n")
        slurmFile.write("#SBATCH --cpus-per-task=1\n")
        time = self.time

        timeRestrictions = True

        if timeRestrictions in slurmConfig:
            timeRestrictions = slurmConfig["timeRestrictions"]

        if timeRestrictions:
            slurmFile.write("#SBATCH --time="+str(time)+"\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p "+self.partition+"\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid-testing\n\n")


        slurmFile.write("module add plgrid/tools/vmd/1.9.3\n")
            
            
        slurmFile.write("vmd -dispdev text -e fit.tcl\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        if not isfile( join( self.path, "keto_fitted.mol2" ) ):
            print("Files not generated!")
            return False

        return True

    def analyseLog(self):
    	pass
        
class FakeParent(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("mol2fit mol2 , xyz")
        quit()
        
    mol2file = sys.argv[1]
    xyzFile = sys.argv[2]
    
    actualDir = getcwd()
    mol2Dir = dirname(abspath(mol2file))
    
    fakeParent = FakeParent( mol2file,mol2Dir)
    fitNode = FitNode("lol", actualDir, xyzFile)
    
    fitNode.generateFromParent(fakeParent, basename(mol2file))
    
    