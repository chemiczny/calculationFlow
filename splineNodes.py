from jobNode import JobNode
from os.path import join, abspath, isfile, expanduser
from shutil import copyfile
import math

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
        
    def generateFromParents(self, graph, parents):
        copyfile( self.whamLog, join(self.path, "wham.log" ) )
        
        sortedParents = sorted( parents, key = lambda x: graph.nodes[x]["data"].reactionCoordinate  )
        offset = min( [ graph.nodes[p]["data"].diff for p in parents   ] )
        
        logF = open( join( self.path, "diff.log" ) , 'w' )
        logHL = open( join( self.path, "dft.log" ) , 'w' )
        
        x = []
        y = []
        lastX = -123124
        for p in sortedParents:
            parent = graph.nodes[p]["data"]
            if abs( parent.reactionCoordinate - lastX ) < 0.00001:
                continue
            lastX = parent.reactionCoordinate
            x.append(parent.reactionCoordinate)
            y.append(parent.diff - offset)
            logF.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.diff - offset ) )
            logHL.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.dftValue) )
        
        logF.close()
        logHL.close()

        self.smoothProfile(x, y)

        templateDir = expanduser("~/jobManagerPro/fDYNAMO")
        splineScript = join(templateDir, "spline.py")

        if isfile(splineScript):
            copyfile(splineScript, join(self.path, "spline.py"))

    def smoothProfile(self, x, y):
        x.reverse()
        y.reverse()

        logF = open(join(self.path, "diffSmooth.log"), 'w')

        # gaussian smoothing (based on grids:regular)
        g = 0.4
        n = len( x )
        for i in range( n ):
            w = .0
            r = .0
            for j in range( n ):
                d = math.fabs( ( x[i] - x[j] ) / g )
                t = math.exp( - d * d )
                r += y[j] * t
                w += t
            logF.write("%20.10lf%20.10lf%20.10lf\n"%( x[i], r / w, y[i] ) )

        logF.close()
        
    def run(self):
        self.status = "finished"
