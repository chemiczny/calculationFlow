from jobNode import JobNode
from os.path import join, abspath, isfile, expanduser
from shutil import copyfile
import math
from os import remove
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
                self.semiEmpiricalValue = parentData.QMenergy
                
        self.diff = self.dftValue - self.semiEmpiricalValue
        
    def run(self):
        self.status = "finished"
        
class SplineNode(JobNode):
    def __init__(self, inputFile, path, whamLog):
        JobNode.__init__(self,inputFile, path)
        self.whamLog = abspath(whamLog)
        self.scanOk = True
        
    def generateFromParents(self, graph, parents):
        self.scanOk = True
        copyfile( self.whamLog, join(self.path, "wham.log" ) )
        

        sortedParents = sorted( parents, key = lambda x: graph.nodes[x]["data"].reactionCoordinate  )
        offset = min( [ graph.nodes[p]["data"].diff for p in parents   ] )
        
        logF = open( join( self.path, "diff.log" ) , 'w' )
        logHL = open( join( self.path, "dft.log" ) , 'w' )
        
        x = []
        y = []
        lastX = -123124


        allowRestart = False
        
        for p in sortedParents:
            parent = graph.nodes[p]["data"]
            if abs( parent.reactionCoordinate - lastX ) < 0.00001:
                continue
            lastX = parent.reactionCoordinate
            x.append(parent.reactionCoordinate)
            y.append(parent.diff - offset)

            logF.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.diff - offset ) )
            logHL.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.dftValue) )

            if parent.diff - offset > 230 and allowRestart:
                print("Big difference: ",parent.diff - offset  , " for " )

                dftPath = ""

                for node in graph.predecessors(parent.path):
                    if "gaussian" in graph.nodes[node]["data"].templateKey:
                        dftPath = node
                        break

                print(dftPath)
                print("Restarting DFT node with option SCF=QC")

                dftNodeData = graph.nodes[dftPath]["data"]
                dftNodeData.additionalKeywords["otherOptions"] = "SCF=(QC,direct)" 
                if isfile( join(dftPath, "with_gaussian.f90") ):
                    remove( join(dftPath, "with_gaussian.f90") )

                dftNodeData.status = "waitingForParent"
                parent.status = "waitingForParent"

                self.scanOk = False

        
        logF.close()
        logHL.close()

        templateDir = join(sys.path[0],"fDYNAMO")
        splineScript = join(templateDir, "spline.py")
        fixSplineScript = join(templateDir, "fixSpline.py")

        if isfile(splineScript):
            copyfile(splineScript, join(self.path, "spline.py"))

        if isfile(fixSplineScript):
            copyfile(fixSplineScript, join(self.path, "fixSpline.py"))

        self.generateEnergyLogs(graph, parents)

    def generateEnergyLogs(self, graph, diffNodes):
        rc = []
        semiEmpiricalPotEn = []
        semiEmpiricalQMEn = []
        dftPotEn = []
        dftQMEn = []


        sortedDiffNodes = sorted( diffNodes, key = lambda x: graph.nodes[x]["data"].reactionCoordinate  )
        for node in sortedDiffNodes:
            pred = list(graph.predecessors(node))
            diffData = graph.nodes[node]["data"]

            rc.append(diffData.reactionCoordinate)
            for spNode in pred:
                spNodeData = graph.nodes[spNode]["data"]
            
                if "gaussian" in spNodeData.templateKey:
                    dftQMEn.append( spNodeData.QMenergy)
                    dftPotEn.append( spNodeData.PotentialEnergy )
                    
                else:
                    semiEmpiricalQMEn.append( spNodeData.QMenergy)
                    semiEmpiricalPotEn.append( spNodeData.PotentialEnergy )


        self.writeXY2log(  rc, semiEmpiricalPotEn, join(self.path, "semiEmpPotEn.log") )
        self.writeXY2log(  rc, semiEmpiricalQMEn, join(self.path, "semiEmpQMEn.log") )
        self.writeXY2log(  rc, dftPotEn, join(self.path, "dftPotEn.log") )
        self.writeXY2log(  rc, dftQMEn, join(self.path, "dftQMEn.log") )


    def writeXY2log(self, x, y, log):
        logF = open(log, 'w')

        for xEl, yEl in zip(x, y):
            logF.write( "%8.3lf%20.10lf\n"%( xEl, yEl ) )

        logF.close()

    def verifyLog(self):
        return scanOk
        
    def run(self):
        if self.scanOk:
            self.status = "finished"
        else:
            self.status = "waitingForParent"
