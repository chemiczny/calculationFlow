from jobNode import JobNode
from os.path import join, abspath
from shutil import copyfile

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
        
        for p in sortedParents:
            parent = graph.nodes[p]["data"]
            logF.write( "%8.3lf%20.10lf\n"%( parent.reactionCoordinate, parent.diff - offset ) )
        
        logF.close()
        
    def run(self):
        self.status = "finished"
