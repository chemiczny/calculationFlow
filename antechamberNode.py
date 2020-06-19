from jobNode import JobNode
from os.path import join, isfile, isdir
from shutil import copyfile

class AntechamberNode(JobNode):
    def __init__(self, inputFile, path):
        JobNode.__init__(self,inputFile, path)
        
    def generateFromParent(self, parentData):
        if not hasattr(parentData, "gesp"):
            print("Parent does not contain gesp data!")
            
        gespSource = join( parentData.path, parentData.gesp )
        copyfile(gespSource, join(self.path, self.inputFile))
        
        self.writeSlurmScript("run.slurm")
    
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
                        
        if not slurmConfig:
            slurmFile.write("#SBATCH --time=1:00:00\n")
            if hasattr(self, "partition"):
                slurmFile.write("#SBATCH -p plgrid-short\n\n")
            else:
                slurmFile.write("#SBATCH -p plgrid\n\n")


        slurmFile.write("module add plgrid/apps/amber/18\n")
            
            
        slurmFile.write("antechamber -i keto.gesp -fi gesp -o keto.mol2 -fo mol2 -c resp\n")
        slurmFile.write("antechamber -i keto.mol2 -fi mol2 -o keto.prepi -fo prepi\n")
        slurmFile.write("parmchk2 -f prepi -i keto.prepi -o keto.frcmod\n")
        
        slurmFile.close()
        
        self.slurmFile = filename
        
    def verifyLog(self):
        if not isfile( join( self.path, "keto.mol2" ) ):
            print("Files not generated!")
            return False
        
        if not isfile( join( self.path, "keto.prepi" ) ):
            print("Files not generated!")
            return False
        
        if not isfile( join( self.path, "keto.frcmod" ) ):
            print("Files not generated!")
            return False

        return True

    def analyseLog(self):
    	pass