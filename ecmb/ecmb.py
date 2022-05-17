# -*- coding: iso-8859-1 -*-

"""
  Copyright (C) Sergio Marti (smarti@nuvol.uji.es)

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

#######################################################################
#                                                                     #
#  Dependences & some Constants...                                    #
#                                                                     #
#######################################################################
import    os
import    sys
import    time
import    math
import    string
import    struct
import    stat

# Compressed files...
import    gzip
import    bz2

#
# http://physics.nist.gov/cuu/Constants/index.html
#
_c       = 299792458.       # m·s-1
_NA      = 6.0221415e23        # mol-1
_h       = 6.6260693e-34    # J·s
_kb      = 1.3806505e-23    # J·K-1
_R       = 8.314472         # J·mol-1·K-1
_eV      = 1.60217653e-19   # eV -> J
_me      = 9.1093826e-31    # kg
_a0      = 0.5291772108     # 1e-10·m
_Ha      = 4.35974417e-18   # J (2625.49962955 kJ·mol-1)
_K2J     = 4.184
_J2K     = 0.239005736138
_H2K     = 627.509471695    # Ha >> kcal·mol-1
_R2D     = 180./math.pi
_VERSION = "Mon Jan 23 20:40:44 CET 2006"


#######################################################################
#                                                                     #
#  Periodic Table                                                     #
#                                                                     #
#######################################################################
PTable_mass = [ 1.00794, 1.00794, 4.002602, 6.941, 9.012182, 10.811, \
    12.0107, 14.00674, 15.9994, 18.9984032, 20.1797, 22.989770, 24.3050, \
    26.981538, 28.0855, 30.973761, 32.066, 35.4527, 39.948, 39.0983, \
    40.078, 44.955910, 47.867, 50.9415, 51.9961, 54.938049, 55.845, \
    58.933200, 58.6934, 63.546, 65.39, 69.723, 72.61, 74.92160, \
    78.96, 79.904, 83.80, 85.4678, 87.62, 88.90585, 91.224, \
    92.90638, 95.94, 98.0, 101.07, 102.90550, 106.42, 107.8682, \
    112.411, 114.818, 118.710, 121.760, 127.60, 126.90447, 131.29, \
    132.90545, 137.327, 138.9055, 140.116, 140.90765, 144.24, 145.0, \
    150.36, 151.964, 157.25, 158.92534, 162.50, 164.93032, 167.26, \
    168.93421, 173.04, 174.967, 178.49, 180.9479, 183.84, 186.207, \
    190.23, 192.217, 195.078, 196.96655, 200.59, 204.3833, 207.2, \
    208.98038, 209.0, 210.0, 222.0, 223.0, 226.0, 227.0, \
    232.0381, 231.03588, 238.0289, 237.0, 244.0, 243.0, 247.0, \
    247.0, 251.0, 252.0, 257.0, 258.0, 259.0, 262.0, \
    261.0, 262.0, 263.0, 262.0, 265.0, 266.0 ]
    
PTable_smb  = [ "X", "H", "He", "Li", "Be", "B", \
    "C", "N", "O", "F", "Ne", "Na", "Mg", \
    "Al", "Si", "P", "S", "Cl", "Ar", "K", \
    "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", \
    "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", \
    "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", \
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", \
    "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", \
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", \
    "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", \
    "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", \
    "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", \
    "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", \
    "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", \
    "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", \
    "Rf", "Db", "Sg", "Bh", "Hs", "Mt" ]

PTable_dic = { 'ge': 32, 'gd': 64, 'ga': 31, 'la': 57, 'li': 3, 'tl': 81, \
	'tm': 69, 'lr': 103, 'th': 90, 'ti': 22, 'te': 52, 'tb': 65, 'tc': 43, \
	'ta': 73, 'yb': 70, 'db': 105, 'dy': 66, 'xe': 54, 'h': 1, 'p': 15, \
	'x': 0, 'zn': 30, 'eu': 63, 'zr': 40, 'er': 68, 'ru': 44, 're': 75, \
	'rf': 104, 'ra': 88, 'rb': 37, 'rn': 86, 'rh': 45, 'be': 4, 'ba': 56, \
	'bh': 107, 'bi': 83, 'bk': 97, 'br': 35, 'c': 6, 'k': 19, 'o': 8, \
	's': 16, 'w': 74, 'os': 76, 'co': 27, 'cm': 96, 'cl': 17, 'ca': 20, \
	'pa': 91, 'cf': 98, 'ce': 58, 'cd': 48, 'cs': 55, 'cr': 24, 'cu': 29, \
	'pr': 59, 'pt': 78, 'pu': 94, 'pb': 82, 'lu': 71, 'pd': 46, 'po': 84, \
	'pm': 61, 'hs': 108, 'ho': 67, 'hf': 72, 'hg': 80, 'he': 2, 'md': 101, \
	'mg': 12, 'b': 5, 'f': 9, 'mo': 42, 'mn': 25, 'n': 7, 'mt': 109, 'v': 23, \
	'ac': 89, 'ag': 47, 'ir': 77, 'am': 95, 'al': 13, 'as': 33, 'ar': 18, \
	'au': 79, 'at': 85, 'in': 49, 'ni': 28, 'no': 102, 'na': 11, 'nb': 41, \
	'nd': 60, 'ne': 10, 'es': 99, 'np': 93, 'fr': 87, 'sc': 21, 'fe': 26, \
	'fm': 100, 'i': 53, 'sr': 38, 'kr': 36, 'si': 14, 'u': 92, 'sn': 50, \
	'sm': 62, 'y': 39, 'sb': 51, 'sg': 106, 'se': 34 }

PTable_size = len( PTable_mass )


#######################################################################
#                                                                     #
#  3D Coordinate Operations (Some taken from Babel)                   #
#                                                                     #
#######################################################################
def Module( v ):
    return( math.sqrt( v[0] * v[0] + v[1] * v[1] + v[2] * v[2] ) )


def Dotvec( a, b ):
    return( ( a[0] * b[0] ) + ( a[1] * b[1] ) + ( a[2] * b[2] ) )


def Crossvec( a, b ):
    out=[ .0, .0, .0 ]
    out[0]=a[1] * b[2] - a[2] * b[1]
    out[1]=a[2] * b[0] - a[0] * b[2]
    out[2]=a[0] * b[1] - a[1] * b[0]
    return( out )


def Normalize( vec ):
    mod_vec=Module( vec )
    if( mod_vec == 0.0 ):
        return( [ .0, .0, .0 ] )
    vec[0]/=mod_vec
    vec[1]/=mod_vec
    vec[2]/=mod_vec
    return( vec )
    

def Det3( m ):
    det= m[0] * ( m[4] * m[8] - m[5] * m[7] )
    det-=m[1] * ( m[3] * m[8] - m[5] * m[6] )
    det+=m[2] * ( m[3] * m[7] - m[4] * m[6] )
    return( det )


def Matvec3( vec, mat ):
    out=[ .0, .0, .0 ]
    out[0]=vec[0] * mat[0] + vec[1] * mat[1] + vec[2] * mat[2]
    out[1]=vec[0] * mat[3] + vec[1] * mat[4] + vec[2] * mat[5]
    out[2]=vec[0] * mat[6] + vec[1] * mat[7] + vec[2] * mat[8]
    return( out )
    

def Invmat3( m ):
    det=Det3( m )
    mi=[ .0, .0, .0, .0, .0, .0, .0, .0, .0 ]
    if( det != 0.0 ):
        mi[0]=+( m[4] * m[8] - m[5] * m[7] ) / det
        mi[1]=-( m[1] * m[8] - m[2] * m[7] ) / det
        mi[2]=+( m[1] * m[5] - m[2] * m[4] ) / det
        mi[3]=-( m[3] * m[8] - m[5] * m[6] ) / det
        mi[4]=+( m[0] * m[8] - m[2] * m[6] ) / det
        mi[5]=-( m[0] * m[5] - m[2] * m[3] ) / det
        mi[6]=+( m[3] * m[7] - m[4] * m[6] ) / det
        mi[7]=-( m[0] * m[7] - m[1] * m[6] ) / det
        mi[8]=+( m[0] * m[4] - m[1] * m[3] ) / det
    return( mi )


def Matmat3( ma, mb ):
    mo=[ .0, .0, .0, .0, .0, .0, .0, .0, .0 ]
    mo[0]=ma[0] * mb[0] + ma[1] * mb[3] + ma[2] * mb[6]
    mo[1]=ma[0] * mb[1] + ma[1] * mb[4] + ma[2] * mb[7]
    mo[2]=ma[0] * mb[2] + ma[1] * mb[5] + ma[2] * mb[8]
    mo[3]=ma[3] * mb[0] + ma[4] * mb[3] + ma[5] * mb[6]
    mo[4]=ma[3] * mb[1] + ma[4] * mb[4] + ma[5] * mb[7]
    mo[5]=ma[3] * mb[2] + ma[4] * mb[5] + ma[5] * mb[8]
    mo[6]=ma[6] * mb[0] + ma[7] * mb[3] + ma[8] * mb[6]
    mo[7]=ma[6] * mb[1] + ma[7] * mb[4] + ma[8] * mb[7]
    mo[8]=ma[6] * mb[2] + ma[7] * mb[5] + ma[8] * mb[8]
    return( mo )


def Jacobi3( mat_symm_upp ):
    msu=mat_symm_upp[:]
    tmsu=[ .0, .0, .0, .0, .0, .0 ]
    evec=[ 1., .0, .0, .0, 1., .0, .0, .0, 1. ]
    tmpe=[ .0, .0, .0, .0, .0, .0, .0, .0, .0 ]
    flg=0
    nit=0
    while( nit < 100 and flg == 0 ):
        tet=.0
        faij=[ math.fabs( msu[1] ), math.fabs( msu[2] ), math.fabs( msu[4] ) ]
        # M(1,2)
        if( faij[0] > faij[1] and faij[0] > faij[2] ):
#            elemento="a12"
            if( math.fabs( msu[3] - msu[0] ) > 1e-12 ):
                tet=0.5 * math.atan( -2. * msu[1] / ( msu[3] - msu[0] ) )
                sen=math.sin( tet ); SEN=sen*sen
                cos=math.cos( tet ); COS=cos*cos
            else:
                sen=math.sqrt( 2. ) * 0.5; SEN=0.5
                cos=sen;                   COS=0.5
            cossen=cos * sen
            tmsu[0]=msu[0] * COS + 2. * msu[1] * cossen + msu[3] * SEN
            tmsu[1]=( msu[3] - msu[0] ) * cossen + msu[1] * ( COS - SEN )
            tmsu[2]=msu[2] * cos + msu[4] * sen
            tmsu[3]=msu[3] * COS - 2. * msu[1] * cossen + msu[0] * SEN
            tmsu[4]=msu[4] * cos - msu[2] * sen
            tmsu[5]=msu[5]
            msu=tmsu[:]
            tmpe[0]=evec[0] * cos + evec[1] * sen
            tmpe[1]=evec[1] * cos - evec[0] * sen
            tmpe[2]=evec[2]
            tmpe[3]=evec[3] * cos + evec[4] * sen
            tmpe[4]=evec[4] * cos - evec[3] * sen
            tmpe[5]=evec[5]
            tmpe[6]=evec[6] * cos + evec[7] * sen
            tmpe[7]=evec[7] * cos - evec[6] * sen
            tmpe[8]=evec[8]
            evec=tmpe[:]
#            evec=Matmat3( evec, [ cos, -sen, .0, sen, cos, .0, .0, .0, 1. ] )
        # M(1,3)
        elif( faij[1] > faij[0] and faij[1] > faij[2] ):
#            elemento="a13"
            if( math.fabs( msu[5] - msu[0] ) > 1e-12 ):
                tet=0.5 * math.atan( -2. * msu[2] / ( msu[5] - msu[0] ) )
                sen=math.sin( tet ); SEN=sen*sen
                cos=math.cos( tet ); COS=cos*cos
            else:
                sen=math.sqrt( 2. ) * 0.5; SEN=0.5
                cos=sen;                   COS=0.5
            cossen=cos * sen
            tmsu[0]=msu[0] * COS + 2. * msu[2] * cossen + msu[5] * SEN
            tmsu[1]=msu[1] * cos + msu[4] * sen
            tmsu[2]=( msu[5] - msu[0] ) * cossen + msu[2] * ( COS - SEN )
            tmsu[3]=msu[3]
            tmsu[4]=msu[4] * cos - msu[1] * sen
            tmsu[5]=msu[5] * COS - 2. * msu[2] * cossen + msu[0] * SEN
            msu=tmsu[:]
            tmpe[0]=evec[0] * cos + evec[2] * sen
            tmpe[1]=evec[1]
            tmpe[2]=evec[2] * cos - evec[0] * sen
            tmpe[3]=evec[3] * cos + evec[5] * sen
            tmpe[4]=evec[4]
            tmpe[5]=evec[5] * cos - evec[3] * sen
            tmpe[6]=evec[6] * cos + evec[8] * sen
            tmpe[7]=evec[7]
            tmpe[8]=evec[8] * cos - evec[6] * sen
            evec=tmpe[:]
#            evec=Matmat3( evec, [ cos, .0, -sen, .0, 1., .0, sen, .0, cos ] )
        # M(2,3)
        else:
#            elemento="a23"
            if( math.fabs( msu[5] - msu[3] ) > 1e-12 ):
                tet=0.5 * math.atan( -2. * msu[4] / ( msu[5] - msu[3] ) )
                sen=math.sin( tet ); SEN=sen*sen
                cos=math.cos( tet ); COS=cos*cos
            else:
                sen=math.sqrt( 2. ) * 0.5; SEN=0.5
                cos=sen;                   COS=0.5
            cossen=cos * sen
            tmsu[0]=msu[0]
            tmsu[1]=msu[1] * cos + msu[2] * sen
            tmsu[2]=msu[2] * cos - msu[1] * sen
            tmsu[3]=msu[3] * COS + 2. * msu[4] * cossen + msu[5] * SEN
            tmsu[4]=( msu[5] - msu[3] ) * cossen + msu[4] * ( COS - SEN )
            tmsu[5]=msu[5] * COS - 2. * msu[4] * cossen + msu[3] * SEN
            msu=tmsu[:]
            tmpe[0]=evec[0]
            tmpe[1]=evec[1] * cos + evec[2] * sen
            tmpe[2]=evec[2] * cos - evec[1] * sen
            tmpe[3]=evec[3]
            tmpe[4]=evec[4] * cos + evec[5] * sen
            tmpe[5]=evec[5] * cos - evec[4] * sen
            tmpe[6]=evec[6]
            tmpe[7]=evec[7] * cos + evec[8] * sen
            tmpe[8]=evec[8] * cos - evec[7] * sen
            evec=tmpe[:]
#            evec=Matmat3( evec, [ 1., .0, .0, .0, cos, -sen, .0, sen, cos ] )
#        print "%d [%s] (%lf)"%(nit,elemento,tet)
#        print "%20.10lf%20.10lf%20.10lf"%(msu[0],msu[3],msu[5])
#        print "%20.10lf%20.10lf%20.10lf"%(evec[0],evec[1],evec[2])
#        print "%20.10lf%20.10lf%20.10lf"%(evec[3],evec[4],evec[5])
#        print "%20.10lf%20.10lf%20.10lf\n"%(evec[6],evec[7],evec[8])
        nit+=1
        flg=( math.fabs( msu[1] ) < 1e-6 and
            math.fabs( msu[2] ) < 1e-6 and
            math.fabs( msu[4] ) < 1e-6 )
    if( flg == 0 ):
        return( None, None )
    else:
        return( [ msu[0], msu[3], msu[5] ], evec )


def Dist( crd1, crd2 ):
    return( Module( [ crd2[0] - crd1[0], crd2[1] - crd1[1], crd2[2] - crd1[2] ] ) )


def Angl( crd1, crd2, crd3 ):
    v21=[ .0, .0, .0 ]
    v21[0]=crd1[0] - crd2[0]
    v21[1]=crd1[1] - crd2[1]
    v21[2]=crd1[2] - crd2[2]
    v23=[ .0, .0, .0 ]
    v23[0]=crd3[0] - crd2[0]
    v23[1]=crd3[1] - crd2[1]
    v23[2]=crd3[2] - crd2[2]
    return( math.acos( Dotvec( v21, v23 ) / ( Module( v21 ) * Module( v23 ) ) ) * _R2D )


def Dihe( crd1, crd2, crd3, crd4 ):
    v21=[ .0, .0, .0 ]
    v21[0]=crd1[0] - crd2[0]
    v21[1]=crd1[1] - crd2[1]
    v21[2]=crd1[2] - crd2[2]
    v23=[ .0, .0, .0 ]
    v23[0]=crd3[0] - crd2[0]
    v23[1]=crd3[1] - crd2[1]
    v23[2]=crd3[2] - crd2[2]
    v24=[ .0, .0, .0 ]
    v24[0]=crd4[0] - crd2[0]
    v24[1]=crd4[1] - crd2[1]
    v24[2]=crd4[2] - crd2[2]
    p1=Crossvec( v21, v23 )
    p2=Crossvec( v24, v23 )
    t1=Dotvec( p1, p2 )
    t2=Module( p1 )
    t3=Module( p2 )
    if( t2 == .0 or t3 == .0 ):
        angle=.0
    else:
        angle= t1 / ( t2 * t3 )
        if( math.fabs( angle ) > 1. ): 
            angle=math.fabs( angle ) / angle
        angle=math.acos( angle ) * _R2D
        sign=Dotvec( v21, p2 )
        if( sign < .0 ): 
            angle=-angle
    return( angle )


#######################################################################
#                                                                     #
#  Main Class Definition                                              #
#                                                                     #
#######################################################################
class Molec:
#
# Init all the variables...
#
    def __init__( self, size=0 ):
        self.size=size
        self.segn=[]
        self.seg_lim=[]
        self.seg_lim_size=0
        self.resn=[]
        self.res_lim=[]
        self.res_lim_size=0
        self.resid=[]
        self.atom=[]
        self.crd=[]
        self.chrg=[]
        self.z=[]
        # Define an empty structure, may be useless...
        n=0
        while( n < size ):
            self.segn.append( "SEGN" )
            self.resn.append( "RESN" )
            self.resid.append( 0 )
            self.atom.append( "X" )
            self.crd.append( [.0, .0, .0 ] )
            self.chrg.append( .0 )
            self.z.append( 0 )
            n+=1
        if( size > 0 ):
            self.seg_lim.append( size - 1 )
            self.seg_lim_size+=1
            self.res_lim.append( size - 1 )
            self.res_lim_size+=1


    def __clean( self ):
        del self.size
        del self.segn
        del self.seg_lim
        del self.seg_lim_size
        del self.resn
        del self.res_lim
        del self.res_lim_size
        del self.resid
        del self.atom
        del self.crd
        del self.chrg
        del self.z

    def __del__( self ):
        self.__clean()


#
# Physical / Logical separation...
#
    def get_segn( self, n ):
        return( self.segn[n] )

    def get_resn( self, n ):
        return( self.resn[n] )

    def get_resid( self, n ):
        return( self.resid[n] )

    def get_atom( self, n ):
        return( self.atom[n] )

    def get_crd( self, n):
        # Avoid possible pointer mislead...
        return( self.crd[n][:] )

    def get_chrg( self, n ):
        return( self.chrg[n] )

    def get_z( self, n ):
        return( self.z[n] )

    def set_segn( self, n, segn ):
        self.segn[n]=segn

    def set_resn( self, n, resn ):
        self.resn[n]=resn

    def set_resid( self, n, resid ):
        self.resid[n]=resid

    def set_atom( self, n, atom ):
        self.atom[n]=atom

    def set_crd( self, n, crd):
        # Avoid possible pointer mislead...
        self.crd[n][:]=crd[:]

    def set_chrg( self, n, chrg ):
        self.chrg[n]=chrg

    def set_z( self, n, z ):
        self.z[n]=z


#
# Basic Geometrical Operations: Translate, Rotate and Dock...
#
    def translate( self, vec, beta=1., sele=None ):
        if( sele == None ):
            n=0
            while( n < self.size ):
                pos=self.get_crd( n )
                pos[0]+=beta * vec[0]
                pos[1]+=beta * vec[1]
                pos[2]+=beta * vec[2]
                self.set_crd( n, pos )
                n+=1
        else:
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    pos=self.get_crd( n )
                    pos[0]+=beta * vec[0]
                    pos[1]+=beta * vec[1]
                    pos[2]+=beta * vec[2]
                    self.set_crd( n, pos )
                n+=1

        
    def translate_to_center( self ):
        com=[ .0, .0, .0 ]
        t=.0
        n=0
        while( n < self.size ):
            p=self.get_crd( n )
            m=PTable_mass[ self.get_z( n ) ]
            t+=m
            for i in [ 0, 1, 2 ]: com[i]+=p[i] * m
            n+=1
        for i in [ 0, 1, 2 ]: com[i]/=t
        n=0
        while( n<self.size ):
            p=self.get_crd( n )
            for i in [ 0, 1, 2 ]: p[i]-=com[i]
            self.set_crd( n, p )
            n+=1


    def to_principal_axes( self ):
        self.translate_to_center()
        xx=.0; xy=.0; xz=.0
        yy=.0; yz=.0;
        zz=.0
        n=0
        while( n < self.size ):
            p=self.get_crd( n )
            m=PTable_mass[ self.get_z( n ) ]
            xx+=m * p[0] * p[0]
            xy+=m * p[0] * p[1]
            xz+=m * p[0] * p[2]
            yy+=m * p[1] * p[1]
            yz+=m * p[1] * p[2]
            zz+=m * p[2] * p[2]
            n+=1
# Symmetric Upper por columnas (Dynamo, F90)
#        mti=[ yy + zz, -xy, xx + zz, -xz, -yz, xx + yy ]
# Symmetric Upper por filas
        mti=[ yy + zz, -xy, -xz, xx + zz, -yz, xx + yy ]
        eval,evec=Jacobi3( mti )
        #Transpose
        for mij in [ [1, 3], [2, 6], [5, 7] ]:
            swp=evec[mij[0]]
            evec[mij[0]]=evec[mij[1]]
            evec[mij[1]]=swp
        n=0
        while( n<self.size ):
            pos=self.get_crd( n )
            self.set_crd( n, Matvec3( pos, evec ) )
            n+=1


    def rotate( self, crd1, crd2, theta, sele=None ):
        theta/=_R2D
        cos=math.cos( theta )
        sen=math.sin( theta )
        # R (counterclockwise direction) rotation vector
        vr=[.0,.0,.0]
        vr[0]=crd1[0] - crd2[0]
        vr[1]=crd1[1] - crd2[1]
        vr[2]=crd1[2] - crd2[2]
        vr=Normalize( vr )
        # CRD2 is the rotation center
        cr=[ .0, .0, .0 ]
        cr[:]=crd2[:]
        # Define a normalized perpendicular vector: avoid to feed the kernel
        vp=[ .0, .0, .0 ]
        if( vr[2] != .0 ):
            vp[0]=1.
            vp[1]=1.
            vp[2]=-( vr[0] + vr[1] ) / vr[2]
        else:
            vp[2]=.0
            if( vr[1] != 0.0 ):
                vp[0]=1.
                vp[1]=-vr[0] / vr[1]
            else:
                vp[0]=.0
                vp[1]=1.
        vp=Normalize( vp )
        # Obtain the normalized vectorial product
        vu=Normalize( Crossvec( vr, vp ) )
        # Build Basis-Change Matrices
        mcb=[ vp[0], vp[1], vp[2], vu[0], vu[1], vu[2], vr[0], vr[1], vr[2] ]
        micb=Invmat3( mcb )
#        print mcb
#        print micb
        # Rotation:    micb * R * mcb * P
        #
        #    P      atom/point
        #    mcb    Basis Change Matrix
        #    R      Rotation Matrix
        #          |  cos(theta)  sin(theta)  0  |
        #          | -sin(theta)  cos(theta)  0  |
        #          |  0           0           1  |
        #
        vrcb=[ .0, .0, .0 ]
        if( sele == None ):
            n=0
            while( n < self.size ):
                pos=self.get_crd( n )
                # Center to cr
                pos[0]-=cr[0]
                pos[1]-=cr[1]
                pos[2]-=cr[2]
                # Change the axis
                vcb=Matvec3( pos, mcb )
                vrcb[0]=cos * vcb[0] + sen * vcb[1]
                vrcb[1]=cos * vcb[1] - sen * vcb[0]
                vrcb[2]=vcb[2]
                # Restore original axis
                pos=Matvec3( vrcb, micb )
                pos[0]+=cr[0]
                pos[1]+=cr[1]
                pos[2]+=cr[2]
                self.set_crd( n, pos )
                n+=1
        else:
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    pos=self.get_crd( n )
                    # Center to cr
                    pos[0]-=cr[0]
                    pos[1]-=cr[1]
                    pos[2]-=cr[2]
                    # Change the axis
                    vcb=Matvec3( pos, mcb )
                    vrcb[0]=cos * vcb[0] + sen * vcb[1]
                    vrcb[1]=cos * vcb[1] - sen * vcb[0]
                    vrcb[2]=vcb[2]
                    # Restore original axis
                    pos=Matvec3( vrcb, micb )
                    pos[0]+=cr[0]
                    pos[1]+=cr[1]
                    pos[2]+=cr[2]
                    self.set_crd( n, pos )
                n+=1


    # a? (atom numbers) refer first to *zero* !!!
    def dock( self, a1, a2, a3, crd1, crd2, crd3, sele=None ):
        # a1 -> p1
        #
        pos=self.get_crd( a1 )
        orig=[ .0, .0, .0 ]
        orig[0]=crd1[0] - pos[0]
        orig[1]=crd1[1] - pos[1]
        orig[2]=crd1[2] - pos[2]
        self.translate( orig, sele=sele )
        #
        # a2 -> p2
        #
        # p1=a1 .----------. a2  (vpa=a2-p1)
        #        \ ) theta
        #         \
        #          \                        vp = vpa x vpp
        #           \
        #            . p2 (vpp=p2-p1)
        #
        pos=self.get_crd( a2 )
        theta=Angl( pos, crd1, crd2 )
        vpa=[ .0, .0, .0 ]
        vpa[0]=pos[0] - crd1[0]
        vpa[1]=pos[1] - crd1[1]
        vpa[2]=pos[2] - crd1[2]
        vpa=Normalize( vpa )
        vpp=[ .0, .0, .0 ]
        vpp[0]=crd2[0] - crd1[0]
        vpp[1]=crd2[1] - crd1[1]
        vpp[2]=crd2[2] - crd1[2]
        vpp=Normalize( vpp )
        vp=Normalize( Crossvec( vpa, vpp ) )
        vp[0]+=crd1[0]
        vp[1]+=crd1[1]
        vp[2]+=crd1[2]
        self.rotate( crd1, vp, theta, sele )
        #
        # a3 -> p3
        #
        #                    .a3
        #                   /
        #                  /
        #           a2=p2 /
        #  a1=p1 .-------.---. cr
        #                 \  |
        #                  \ |
        #                   \|
        #                    . p3
        #  
        #  To obtain theta, now we must find the point where p3 intersects
        #  with the line (p1,p2): cr
        #
        pos=self.get_crd( a3 )
        vpa=[ .0, .0, .0 ]
        vpa[0]=crd3[0] - crd2[0]
        vpa[1]=crd3[1] - crd2[1]
        vpa[2]=crd3[2] - crd2[2]
        beta=Dotvec( vpp, vpa )
        cr=[ .0, .0, .0 ]
        cr[0]=crd2[0] + beta * vpp[0]
        cr[1]=crd2[1] + beta * vpp[1]
        cr[2]=crd2[2] + beta * vpp[2]
        theta=Angl( pos, cr, crd3 )
        vp[0]=vpp[0] + cr[0]
        vp[1]=vpp[1] + cr[1]
        vp[2]=vpp[2] + cr[2]
        self.rotate( cr, vp, theta, sele )
        # Fix Complementary angle: Too much optimistic??
        if( Dist( crd3, self.get_crd( a3 ) ) > .1 ):
            self.rotate( cr, vp, 360. - 2 * theta, sele )

#   SUPERIMPOSE_QUATERNION (Dynamo)
#   Gerald Kneller, Mol. Sim. 7, 113--119, 1991.
#    def superimpose( self, molec ):
#        if( molec.size != self.size ): return
#        mc=molec.mass_center()
#        crd=[]
#        n=0
#        while( n < molec.size ):
#            p=molec.get_crd( n )
#            for i in [ 0, 1, 2 ]: p[i]-=mc[i]
#            crd.append( p[:] )
#            n+=1
#        self.translate_to_center()
#        m=[ .0, .0, .0, .0, .0, .0, .0, .0, .0, .0 ]
#        n=0
#        while( n < self.size ):
#            mas=PTable_mass[ self.get_z( m ) ]
#            p=self.get_crd( n )
#            c=Crossvec( crd[n], p )
#            for i in [ 0, 1, 2 ]: c[i]*=2.
#            f=.0
#            for i in [ 0, 1, 2 ]: 
#                f+=(crd[n][i] + p[i]) * (crd[n][i] + p[i])
#            for i in [ 0, 1, 2 ]: 
#                m[0]+=mas * (crd[n][i] - p[i]) * (crd[n][i] - p[i])
#            m[1]+=mas * c[0]
#            m[2]+=mas * (f - 4. * crd[n][0] * p[0])
#            m[3]+=mas * c[1]
#            m[4]-=mas * 2. * ( crd[n][0] * p[1] + crd[n][1] * p[0] )
#            m[5]+=mas * (f - 4. * crd[n][1] * p[1])
#            m[6]+=mas * c[2]
#            m[7]-=mas * 2. * ( crd[n][0] * p[2] + crd[n][2] * p[0] )
#            m[8]-=mas * 2. * ( crd[n][1] * p[2] + crd[n][2] * p[1] )
#            m[9]+=mas * (f - 4. * crd[n][2] * p[2])
#            n+=1
#        # columnas > filas
#        ei,ev=Jacobi4( [ m[0], m[1], m[3], m[6], m[2], m[4], m[7], m[5], m[8], m[9] ] )


    def define_limits( self ):
        del self.seg_lim
        self.seg_lim=[ 0 ]
        self.seg_lim_size=1
        del self.res_lim
        self.res_lim=[ 0 ]
        self.res_lim_size=1
        lcad=self.get_segn( 0 )
        lres=self.get_resn( 0 )
        lnrs=self.get_resid( 0 )
        n=1
        while( n < self.size ):
            if( lnrs != self.get_resid( n ) or \
            lres != self.get_resn( n ) or \
            lcad != self.get_segn( n ) ):
                if( lcad != self.get_segn( n ) ):
                    self.seg_lim.append( n )
                    self.seg_lim_size+=1
                    lcad=self.get_segn( n )
                self.res_lim.append( n )
                self.res_lim_size+=1
                lnrs=self.get_resid( n )
                lres=self.get_resn( n )
            n+=1
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1


    def atom_number( self, segn, resid, atom ):
        # Segname
        seg_idx=-1
        n=0
        n_max=self.seg_lim_size - 1
        while( n < n_max and seg_idx == -1 ):
            if( segn == self.get_segn( self.seg_lim[n] ) ):
                seg_idx=n
            n+=1
        if( seg_idx == -1 ): return(-1)
        # Resid
        res_idx=-1
        n=self.res_lim.index( self.seg_lim[seg_idx] )
        n_max=self.res_lim.index( self.seg_lim[seg_idx + 1] )
        while( n < n_max and res_idx == -1 ):
            if( resid == self.get_resid( self.res_lim[n] ) ):
                res_idx=n
            n+=1
        if( res_idx == -1 ): return(-1)
        # Atom
        atm_idx=-1
        n=self.res_lim[res_idx]
        n_max=self.res_lim[res_idx + 1]
        while( n < n_max and atm_idx == -1 ):
            if( atom == self.get_atom( n ) ):
                atm_idx=n
            n+=1
        return( atm_idx )


    # dirty, since no logical separation...
    def append( self, molec ):
        self.size+=molec.size
        n=0
        while( n < molec.size ):
            self.segn.append(  molec.segn[n]   )
            self.resn.append(  molec.resn[n]   )
            self.resid.append( molec.resid[n]  )
            self.atom.append(  molec.atom[n]   )
            self.crd.append(   molec.crd[n][:] )
            self.chrg.append(  molec.chrg[n]   )
            self.z.append(     molec.z[n]      )
            n+=1
        self.define_limits()
        self.hard_norm()
    def remove( self, sele ):
        n=self.size-1
        while( n > -1 ):
            if( sele.issel(n) ):
                del self.segn[n]
                del self.resn[n]
                del self.resid[n]
                del self.atom[n]
                del self.crd[n]
                del self.chrg[n]
                del self.z[n]
            n-=1
        self.size-=sele.count()
        self.define_limits()
        self.hard_norm()


#
# DCD IO (Yes!, quick and dirty...)
#
    def dcd_read( self, name ):
        if( name[-4:] == ".bz2" ):
            self.dcd_fd=bz2.BZ2File( name, "rb" )
        elif( name[-3:] == ".gz" ):
            self.dcd_fd=gzip.GzipFile( name, "rb" )
        else:
            self.dcd_fd=open( name, "rb" )
        if( struct.unpack( "<i", self.dcd_fd.read( 4 ) )[0] == 84 ):
            self.dcd_end="<"
        else:
            self.dcd_end=">"
        self.dcd_fd.read( 4 )
        self.dcd_nframe=struct.unpack( self.dcd_end + "i", self.dcd_fd.read( 4 ) )[0] 
        self.dcd_fd.read( 28 )
        self.dcd_nfixed=struct.unpack( self.dcd_end + "i", self.dcd_fd.read( 4 ) )[0]
        self.dcd_fd.read( 4 )
        self.dcd_qcrys=struct.unpack( self.dcd_end + "i", self.dcd_fd.read( 4 ) )[0]
# faster for dynamo, but charmm uses variable titles...
#        self.dcd_fd.read( 136 )
# charmm friendly code
        self.dcd_fd.read( 40 )
        self.dcd_fd.read( struct.unpack( self.dcd_end + "i", self.dcd_fd.read( 4 ) )[0] + 8 )
# -----------------------------------------------------------------------------------
        self.dcd_natoms=struct.unpack( self.dcd_end + "i", self.dcd_fd.read( 4 ) )[0]
        self.dcd_fd.read( 4 )
        self.dcd_nfree=self.dcd_natoms - self.dcd_nfixed
        self.dcd_sele=[]
        if( self.dcd_nfixed > 0 ):
            self.dcd_fd.read( 4 )
            for atm in struct.unpack( self.dcd_end + "%di"%( self.dcd_nfree ), \
                self.dcd_fd.read( 4 * self.dcd_nfree ) ):
                self.dcd_sele.append( atm - 1 )
            self.dcd_fd.read( 4 )
        self.dcd_cframe=0
        if( self.size != self.dcd_natoms ):
            sys.stderr.write( "* Molec [Natoms=%d] /= DCD [Natoms=%d]\n"%( \
                self.size, self.dcd_natoms ) )
            self.dcd_close()

    def dcd_save( self, name, nframes, sele = None, crys = None, big = False ):
        self.dcd_end    = "<"
        if( big ):
            self.dcd_end    = ">"
        self.dcd_cframe = 0
        self.dcd_fd=open( name, "wb" )
        b = struct.pack( self.dcd_end + "i", 84 )
        self.dcd_fd.write( b + "CORD" )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", nframes ) )
        self.dcd_nframe = nframes
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 1 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 1 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", nframes ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        if( sele ):
            n = sele.count()
            f = self.size - n
        else:
            n = self.size
            f = 0
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 3*n ) )
        self.dcd_nfree  = n
        self.dcd_nfixed = f
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", f ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        t = 0
        self.dcd_qcrys  = None
        if( crys ):
            if( len( crys ) == 3 ):
                t = 1
                self.dcd_qcrys  = crys
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", t ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 0 ) )
        self.dcd_fd.write( b )
# -----------------------------------------------------------------------------------
        b = struct.pack( self.dcd_end + "i", 4 + 80 )
        self.dcd_fd.write( b )
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 1 ) )
        self.dcd_fd.write( '* ECMB                                                                          ' )
        self.dcd_fd.write( b )
# -----------------------------------------------------------------------------------
        self.dcd_fd.write( struct.pack( self.dcd_end + "i", 4 ) + struct.pack( self.dcd_end + "i", self.size ) + struct.pack( self.dcd_end + "i", 4 ) )
        self.dcd_natoms = self.size
        self.dcd_sele = []
        if( sele ):
            b = struct.pack( self.dcd_end + "i", sele.count()*4 )
            self.dcd_fd.write( b )
            for i in xrange( self.size ):
                if( sele.issel( i ) ):
                    self.dcd_fd.write( struct.pack( self.dcd_end + "i", i+1 ) )
                    self.dcd_sele.append( i )
            self.dcd_fd.write( b )
                
    def dcd_close( self ):
        try:
            self.dcd_fd.close()
        except AttributeError:
            sys.stderr.write( "* No DCD open...\n" )
        else:
            del self.dcd_fd, self.dcd_nframe, self.dcd_nfixed, self.dcd_qcrys, \
                self.dcd_natoms, self.dcd_nfree, self.dcd_sele, self.dcd_end

    def dcd_next( self ):
        try:
            # 1st skipped fotran control word
            self.dcd_fd.read( 4 )
        except AttributeError:
            sys.stderr.write( "* No DCD open...\n" )
            return( 0 )
        else:
            if( self.dcd_cframe < self.dcd_nframe ):
                if( self.dcd_qcrys ):
                    self.dcd_fd.read( 56 )
                if( self.dcd_nfixed > 0 and self.dcd_cframe > 0 ):
                    xcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), \
                        self.dcd_fd.read( 4 * self.dcd_nfree ) )
                    self.dcd_fd.read( 8 )
                    ycrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), \
                        self.dcd_fd.read( 4 * self.dcd_nfree ) )
                    self.dcd_fd.read( 8 )
                    zcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), \
                        self.dcd_fd.read( 4 * self.dcd_nfree ) )
                    self.dcd_fd.read( 4 )
                    n=0
                    while( n < self.dcd_nfree ):
                        self.crd[self.dcd_sele[n]][0]=xcrd[n]
                        self.crd[self.dcd_sele[n]][1]=ycrd[n]
                        self.crd[self.dcd_sele[n]][2]=zcrd[n]
                        n+=1
                    del xcrd, ycrd, zcrd
                else:
                    xcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), \
                        self.dcd_fd.read( 4 * self.dcd_natoms ) )
                    self.dcd_fd.read( 8 )
                    ycrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), \
                        self.dcd_fd.read( 4 * self.dcd_natoms ) )
                    self.dcd_fd.read( 8 )
                    zcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), \
                        self.dcd_fd.read( 4 * self.dcd_natoms ) )
                    self.dcd_fd.read( 4 )
                    n=0
                    while( n < self.dcd_natoms ):
                        self.crd[n][0]=xcrd[n]
                        self.crd[n][1]=ycrd[n]
                        self.crd[n][2]=zcrd[n]
                        n+=1
                    del xcrd, ycrd, zcrd
                self.dcd_cframe+=1
                return( 1 )
            else:
                return( 0 )

    def dcd_append( self ):
        try:
            self.dcd_fd.tell()
        except AttributeError:
            sys.stderr.write( "* No DCD open...\n" )
            return( 0 )
        else:
            if( self.dcd_qcrys ):
                b = struct.pack( self.dcd_end + "i", 48 )
                t = struct.pack( self.dcd_end + "d", .0 )
                self.dcd_fd.write( b )
                self.dcd_fd.write( struct.pack( self.dcd_end + "d", self.dcd_qcrys[0] ) )
                self.dcd_fd.write( t )
                self.dcd_fd.write( struct.pack( self.dcd_end + "d", self.dcd_qcrys[1] ) )
                self.dcd_fd.write( t )
                self.dcd_fd.write( t )
                self.dcd_fd.write( struct.pack( self.dcd_end + "d", self.dcd_qcrys[2] ) )
                self.dcd_fd.write( b )
            if( self.dcd_nfixed > 0 and self.dcd_cframe > 0 ):
                t = struct.pack( self.dcd_end + "i", self.dcd_nfree * 4 )
                for j in [0, 1, 2]:
                    b = ''
                    for i in xrange( self.dcd_nfree ):
                        b += struct.pack( self.dcd_end + "f", self.crd[self.dcd_sele[i]][j] )
                    self.dcd_fd.write( t + b + t )
            else:
                t = struct.pack( self.dcd_end + "i", self.size * 4 )
                for j in [0, 1, 2]:
                    b = ''
                    for i in xrange( self.size ):
                        b += struct.pack( self.dcd_end + "f", self.crd[i][j] )
                    self.dcd_fd.write( t + b + t )
            self.dcd_cframe+=1
            return( 1 )

    def dcd_next_buf( self ):
        try:
            # 1st skipped fotran control word
            self.dcd_fd.read( 4 )
        except AttributeError:
            sys.stderr.write( "* No DCD open...\n" )
            return( 0 )
        else:
            if( self.dcd_cframe < self.dcd_nframe ):
                if( self.dcd_qcrys ):
                    if( len( self.dcd_fd.read( 56 ) ) != 56 ):
                        return( 0 )
                if( self.dcd_nfixed > 0 and self.dcd_cframe > 0 ):
                    ii=4*self.dcd_nfree
                    jj=20+3*ii
                    buff=self.dcd_fd.read( jj )
                    if( len( buff ) != jj ):
                        return( 0 )
                    kk=0
                    xcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), buff[kk:kk+ii] )
                    kk+=(8+ii)
                    ycrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), buff[kk:kk+ii] )
                    kk+=(8+ii)
                    zcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_nfree ), buff[kk:kk+ii] )
                    n=0
                    while( n < self.dcd_nfree ):
                        self.crd[self.dcd_sele[n]][0]=xcrd[n]
                        self.crd[self.dcd_sele[n]][1]=ycrd[n]
                        self.crd[self.dcd_sele[n]][2]=zcrd[n]
                        n+=1
                    del xcrd, ycrd, zcrd
                else:
                    ii=4*self.dcd_natoms
                    jj=20+3*ii
                    buff=self.dcd_fd.read( jj )
                    if( len( buff ) != jj ):
                        return( 0 )
                    kk=0
                    xcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), buff[kk:kk+ii] )
                    kk+=(8+ii)
                    ycrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), buff[kk:kk+ii] )
                    kk+=(8+ii)
                    zcrd=struct.unpack( self.dcd_end + "%df"%( self.dcd_natoms ), buff[kk:kk+ii] )
                    n=0
                    while( n < self.dcd_natoms ):
                        self.crd[n][0]=xcrd[n]
                        self.crd[n][1]=ycrd[n]
                        self.crd[n][2]=zcrd[n]
                        n+=1
                    del xcrd, ycrd, zcrd
                self.dcd_cframe+=1
                return( 1 )
            else:
                return( 0 )


#
# PDB IO (Almost all IO funcs break the logical/physical independence)
#
    def load_ent( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        lseg=None
        lres=None
        lrid=None
        line=fd.readline()
        n=-1
        while( line != "" ):
            if( len( line ) > 5 ):
                if( line[0:4] == "ATOM" or line[0:6] == "HETATM" ):
                    n+=1
                    self.size=self.size+1
                    self.atom.append( string.strip( line[12:16] ) )
                    self.resn.append( string.strip( line[17:20] ) )
                    tmp=""
                    for c in string.strip( line[23:30] ):
                        if( c in "0123456789" ):
                            tmp+=c
                    self.resid.append( string.atoi( tmp ) )
                    self.crd.append( [\
                        string.atof( line[30:38] ),\
                        string.atof( line[38:46] ),\
                        string.atof( line[46:54] ) ] )
                    if( line[21] != " " ):
                        self.segn.append( line[21] )
                    else:
                        self.segn.append( "SEGN" )
                    # Check .*_lim
                    if( lrid != self.get_resid( n ) or \
                    lres != self.get_resn( n ) or \
                    lseg != self.get_segn( n ) ):
                        if( lseg != self.get_segn( n ) ):
                            self.seg_lim.append( n )
                            self.seg_lim_size+=1
                        lseg=self.get_segn( n )
                        self.res_lim.append( n )
                        self.res_lim_size+=1
                        lrid=self.get_resid( n )
                        lres=self.get_resn( n )
                    # Null charge and atomic number...
                    self.chrg.append( .0 )
                    self.z.append( 0 )
            line=fd.readline()
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()


    def load_fpdb( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        lseg=None
        lres=None
        lrid=None
        line=fd.readline()
        n=-1
        while( line != "" and ( line[0:3] != "END" or line[0:3] != "TER" ) ):
            if( line[0:4] == "ATOM" or line[0:6] == "HETATM" ):
                #0123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789.
                #HETATM      >  < >  <>    <   >      <>      <>      <               >          |
                #ATOM  48166  H2  TIP314833     -31.826 -31.838 -28.924  0.00  0.00      BOX
                #ATOM      9 HG22 ILE    29      -6.997  -7.625 -14.272  0.00  0.00      PRL
                #ATOM   1231  C2  HOP     1       0.271  -3.307   0.596  0.00  0.00      ACS
                #ATOM   1229  O   GLY   111       2.581   2.164   8.255  0.00  0.00      PRH
                n+=1
                self.size+=1
                self.atom.append( string.strip( line[12:17] ) )
                self.resn.append( string.strip( line[17:21] ) )
                self.resid.append( string.atoi( line[21:27] ) )
                self.crd.append( [\
                    string.atof( line[30:38] ),\
                    string.atof( line[38:46] ),\
                    string.atof( line[46:54] ) ] )
                self.segn.append( string.strip( line[69:] ) )
                if( lrid != self.get_resid( n ) or \
                lres != self.get_resn( n ) or \
                lseg != self.get_segn( n ) ):
                    if( lseg != self.get_segn( n ) ):
                        self.seg_lim.append( n )
                        self.seg_lim_size+=1
                        lseg=self.get_segn( n )
                    self.res_lim.append( n )
                    self.res_lim_size+=1
                    lrid=self.get_resid( n )
                    lres=self.get_resn( n )
                self.chrg.append( .0 )
                self.z.append( 0 )
            line=fd.readline()
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()


    def load_pdb( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        lseg=None
        lres=None
        lrid=None
        line=fd.readline()
        n=-1
        while( line != "" and ( line != "END\n" or line != "TER\n" ) ):
            splt=string.split( line )
            # This only will run with a few cases... check more!!!
            if( splt[0] == "ATOM" or splt[0] == "HETATM" ):
                # Append data...
                n+=1
                self.size+=1
                self.atom.append( splt[2] )
                self.resn.append( splt[3] )
                r=4
                if( splt[4].isalpha() ): r+=1
                # fix for alphanumerical residue numbers (mostly antibodies)
                try:
                    ri = string.atoi( splt[r] )
                except ValueError:
                    ri = -1
                self.resid.append( ri )
                self.crd.append( [\
                    string.atof( splt[r + 1] ),\
                    string.atof( splt[r + 2] ),\
                    string.atof( splt[r + 3] ) ] )
                if( len( splt ) > 10 ):
                    self.segn.append( splt[10] )
                else:
                    self.segn.append( "SEGN" )
                # Check .*_lim
                if( lrid != self.get_resid( n ) or \
                lres != self.get_resn( n ) or \
                lseg != self.get_segn( n ) ):
                    if( lseg != self.get_segn( n ) ):
                        self.seg_lim.append( n )
                        self.seg_lim_size+=1
                        lseg=self.get_segn( n )
                    self.res_lim.append( n )
                    self.res_lim_size+=1
                    lrid=self.get_resid( n )
                    lres=self.get_resn( n )
                # Null charge and atomic number...
                self.chrg.append( .0 )
                self.z.append( 0 )
            line=fd.readline()
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()


    def save_pdb( self, name=None, sele=None, big=0 ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __format_pdb_line( self, fd, n, big ):
            atom=self.get_atom( n )
            if( len( atom ) == 1 ):
                fd.write( "  %s  "%( atom ) )
            elif( len(atom) == 2 ):
                fd.write( "  %s "%( atom ) )
            elif( len(atom) == 3 ):
                fd.write( "  %s"%( atom ) )
            elif( len(atom) == 4 ):
                fd.write( " %s"%( atom ) )
            if( big == 1 ):
                fd.write( " %-4s%6d   "%( self.get_resn( n ), self.get_resid( n ) ) )
            else:
                fd.write( " %-4s%5d    "%( self.get_resn( n ), self.get_resid( n ) ) )
            pos=self.get_crd( n )
            fd.write( "%8.3lf%8.3lf%8.3lf"%( pos[0], pos[1], pos[2] ) )
            fd.write( "  0.00  0.00      %s\n"%( self.get_segn( n ) ) )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( name ==None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        cnt=0
        if( sele == None ):
            while( cnt < self.size ):
                fd.write( "ATOM  %5d"%( cnt + 1) )
                __format_pdb_line( self, fd, cnt, big )
                cnt+=1
        else:
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    cnt+=1
                    fd.write( "ATOM  %5d"%( cnt ) )
                    __format_pdb_line( self, fd, n, big )
                n+=1
        fd.write( "END\n" )
        if( fd != sys.stdout ): fd.close()


#
# Coordinates IO
#
    def load_crd( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        lseg=None
        lres=None
        lrid=None
        line=fd.readline()
        n=0
        while( line != "" ):
            splt=string.split( line )
            keyw=string.upper( splt[0] )
            # Take care... if the string is not long enough, [0:__] will
            # not raise any kind of error... but could !!!
            if( keyw[0:6] == "SUBSYS" ):
                curr_segn=splt[2]
            if( keyw[0:4] == "RESI" ):
                curr_resid=string.atoi( splt[1] )
                curr_resn=splt[2]
                splt=string.split( fd.readline() )
                while( splt[0][0] == "!" ):
                    splt=string.split( fd.readline() )
                cnt_res=string.atoi( splt[0] )
                # Check .*_lim
                if( lrid != curr_resid or \
                lres != curr_resn or \
                lseg != curr_segn ):
                    if( lseg != curr_segn ):
                        self.seg_lim.append( n )
                        self.seg_lim_size+=1
                        lseg=curr_segn
                    self.res_lim.append( n )
                    self.res_lim_size+=1
                    lrid=curr_resid
                    lres=curr_resn
                # Load residue !
                m=0
                while( m < cnt_res ):
                    splt=string.split( fd.readline() )
                    while( splt[0][0] == "!" ):
                        splt=string.split( fd.readline() )
                    m+=1
                    n+=1
                    self.size=self.size + 1
                    self.segn.append( curr_segn )
                    self.resn.append( curr_resn )
                    self.resid.append( curr_resid )
                    self.atom.append( splt[1] )
                    self.crd.append( [\
                        string.atof( splt[3] ),\
                        string.atof( splt[4] ),\
                        string.atof( splt[5] ) ] )
                    self.chrg.append( .0 )
                    self.z.append( string.atoi( splt[2] ) )
            line=fd.readline()
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()


    def save_crd( self, name=None, boxl = None ):
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        seg_len=self.seg_lim_size - 1
        res_len=self.res_lim_size - 1
        fd.write( "!===============================================================================\n" )
        fd.write( "%d\t%d\t%d\n"%( self.size, res_len,seg_len ) )
        fd.write( "!===============================================================================\n" )
        if( boxl ):
        	fd.write("Symmetry\t1\nORTHORHOMBIC         93.5000000000     76.5000000000     72.0000000000\n")
            # fd.write( "Symmetry\t1\nCUBIC\t\t%lf\n"%( boxl ) )
        else:
            fd.write( "!Symmetry\t1\n!CUBIC\t\tLattice_(Angstroms)\n" )
        fd.write( "!===============================================================================\n" )
        seg_idx=0
        atom=0
        while( seg_idx < seg_len ):
            res_idxa=self.res_lim.index( self.seg_lim[seg_idx] )
            res_idxb=self.res_lim.index( self.seg_lim[seg_idx + 1] )
            fd.write( "Subsystem %5d  %s\n"%( seg_idx + 1, self.get_segn( self.seg_lim[ seg_idx ] ) ) )
            fd.write( "%7d\n"%( res_idxb - res_idxa ) )
            cnt=0
            while( res_idxa < res_idxb ):
                cnt+=1
                n=self.res_lim[res_idxa]
                n_max=self.res_lim[res_idxa + 1]
                fd.write( "Residue %5d  %s\n"%( self.get_resid( n ), self.get_resn( n ) ) )
                fd.write( "%7d\n"%( n_max - n ) )
                while( n < n_max ):
                    atom+=1
                    fd.write( "%7d %-4s %10d "%( atom, self.get_atom( n ), self.get_z( n ) ) )
                    pos=self.get_crd( n )
                    fd.write( "%18.10lf%18.10lf%18.10lf\n"%( pos[0], pos[1], pos[2] ) )
                    n+=1
                res_idxa+=1
            seg_idx+=1
        if( fd != sys.stdout ): fd.close()


#
# Charmm IO
#
    def load_card( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        lseg=None
        lres=None
        lrid=None
        line=fd.readline()
        f=0
        while( line != "" and f == 0 ):
            f=( line[0] != "*" )
            if( f == 0 ): line=fd.readline()
        self.size=string.atoi( line )
        line=fd.readline()
        n=0
        while( line != "" ):
            # As usual, non exception control...
            # 2073
            #    1    1 MEN  C1  1234.000001234.000001234.00000 ACS  1      0.00000
            # (...)
            # 2073  689 TIP3 H2  1234.000001234.000001234.00000 SOLV 688    0.00000
            #13416 2999 TIP3 H2   -16.23092  21.27275  -0.90305 W    2636   0.00000
            #0123456789.123456789.123456789.123456789.123456789.123456789.123456789.
            #          1         2         3         4         5         6
            curr_resn=string.strip( line[11:16] )
            curr_resid=string.atoi( line[55:60] )
#            curr_tresi=string.atoi( line[5:10] )
            curr_segn=string.strip( line[51:56] )
            # ---
            self.atom.append( string.strip( line[16:20] ) )
            self.resid.append( curr_resid )
            self.resn.append( curr_resn )
            self.segn.append( curr_segn )
            self.crd.append( [\
                string.atof( line[20:30] ),\
                string.atof( line[30:40] ),\
                string.atof( line[40:50] ) ] )
            # Check .*_lim
            if( lrid != curr_resid or lres != curr_resn or lseg != curr_segn ):
                if( lseg != curr_segn ):
                    self.seg_lim.append( n )
                    self.seg_lim_size+=1
                    lseg=curr_segn
                self.res_lim.append( n )
                self.res_lim_size+=1
                lrid=curr_resid
                lres=curr_resn
            # Null charge and atomic number...
            self.chrg.append( .0 )
            self.z.append( 0 )
            n+=1
            line=fd.readline()
        self.seg_lim.append( self.size )
        self.seg_lim_size+=1
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()


    def save_card( self, name=None ):
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        fd.write( "* Easy Computational Molecular Biology\n*\n%d\n"%( self.size ) )
        n=0
        t=0
        while( n < self.size ):
            if( n in self.res_lim ):
                t+=1
            pos=self.get_crd( n )
            fd.write( "%5d%5d %-4s %-4s%10.5lf%10.5lf%10.5lf %4s %-4d%10.5lf\n"%(
                n+1, t, self.get_resn( n ), self.get_atom( n ), pos[0], pos[1], pos[2],
                self.get_segn( n ), self.get_resid( n ), .0 ) )
            n+=1
        if( fd != sys.stdout ): fd.close()


#
# XYZ IO (and cartesian derivates...)
#
    def load_xyz( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        self.size=string.atoi( fd.readline() )
        self.seg_lim=[ 0, self.size ]
        self.seg_lim_size=2
        self.res_lim=[ 0, self.size ]
        self.res_lim_size=2
        fd.readline()
        m=0
        while( m < self.size ):
            splt=string.split( fd.readline() )
            self.atom.append( splt[0] )
            self.crd.append( [ string.atof( splt[1] ), \
                string.atof( splt[2] ), \
                string.atof( splt[3] ) ] )
            if( len( splt ) == 5 ):
                self.chrg.append( string.atof( splt[4] ) )
            else:
                self.chrg.append( .0 )
            self.z.append( 0 )
            self.segn.append( "SEGN" )
            self.resn.append( "RESN" )
            self.resid.append( 0 )
            m+=1
        if( fd != sys.stdin ): fd.close()


    def load_CCx( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            if( name[-4:] == ".bz2" ):
                fd=bz2.BZ2File( name, "rb" )
            elif( name[-3:] == ".gz" ):
                fd=gzip.GzipFile( name, "rb" )
            else:
                fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        self.size=stirng.atoi( fd.readline() )
        self.seg_lim=[ 0, self.size ]
        self.seg_lim_size=2
        self.res_lim=[ 0, self.size ]
        self.res_lim_size=2
        m=0
        while( m < self.size ):
            splt=string.split( fd.readline() )
            self.atom.append( splt[0] )
            self.crd.append( [ string.atof( splt[2] ), \
                string.atof( splt[3] ), \
                string.atof( splt[4] ) ] )
            self.chrg.append( .0 )
            self.z.append( 0 )
            self.segn.append( "SEGN" )
            self.resn.append( "RESN" )
            self.resid.append( 0 )
            m+=1
        if( fd != sys.stdin ): fd.close()


    def save_xyz( self, name=None, sele=None ):
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        # Atomic numbers *should* be defined... cuidadin...
        if( sele == None ):
            fd.write( "%d\n\n"%( self.size ) )
            m=0
            while( m < self.size ):
                pos=self.get_crd( m )
                fd.write( "%2s%16.6lf%12.6lf%12.6lf\n"%( \
                    PTable_smb[ self.get_z( m ) ], pos[0], pos[1], pos[2] ) )
                m+=1
        else:
            fd.write( "%d\n\n"%( sele.count() ) )
            m=0
            while( m < self.size ):
                if( sele.issel( m ) ):
                    pos=self.get_crd( m )
                    fd.write( "%2s%16.6lf%12.6lf%12.6lf\n"%( \
                        PTable_smb[ self.get_z( m ) ], pos[0], pos[1], pos[2] ) )
                m+=1
        if( fd != sys.stdout ): fd.close()


#
# Fill array charges from dynamo or charmm
#
#        kind: 'sysbin' (dynamo) // 'psf' (charmm)
    def fill_charges( self, fname, kind='sysbin' ):
        fd=file( fname, 'rb' )
        for i in range( 6 ):
            fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
        fd.read( 4 )
        if( struct.unpack( 'i', fd.read( 4 ) )[0] == self.size ):
            fd.read( 4 )
            for i in range( 2 ):
                fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
            fd.read(4)
            i=0
            for z in struct.unpack( '%di'%( self.size ), fd.read( self.size * 4 ) ):
                self.z[i]=z
                i+=1
            fd.read(4)
            fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
            fd.read(4)
            i=0
            for q in struct.unpack( '%dd'%( self.size ), fd.read( self.size * 8 ) ):
                self.chrg[i]=q
                i+=1
        fd.close()


#
# Mopac (93) IRC IO (cartesian form)
#
#    def load_mopacIRC ( self, name ):


#
# Grace IRC IO
#
#    def load_graceIRC ( self, name ):


#
# Molecule Operations..
#
    def guess_z( self, sele=None ):
        if( sele == None ):
            n=0
            while( n < self.size ):
                m=0
                flg=0
                while( flg == 0 and m < PTable_size ):
                    smb_len=len( PTable_smb[m] )
                    if( string.upper( self.get_atom( n )[0:smb_len]) == \
                    string.upper( PTable_smb[m] ) ):
                        self.set_z( n, m )
                        flg=1
                    else:
                        m+=1
                if( m == PTable_size ):
                    sys.stderr.write( "* Atom %4d (%4s) not assigned...\n" \
                        %( n+1, self.get_atom( n ) ) )
                n+=1
        else:
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    m=0
                    flg=0
                    while( flg == 0 and m < PTable_size ):
                        smb_len=len( PTable_smb[m] )
                        if( string.upper( self.get_atom( n )[0:smb_len])== \
                        string.upper( PTable_smb[m] ) ):
                            self.set_z( n, m )
                            flg=1
                        else:
                            m+=1
                    if( m == PTable_size ):
                        sys.stderr.write( "* Atom %4d (%4s) not assigned...\n" \
                            %( n+1, self.get_atom( n ) ) )
                n+=1

#
# Remember to call .define_limtis() after .chg_segn & .chg_resn
#
    def chg_segn( self, nsegn, segn=None, sele=None ):
        # Change only selected atoms
        if( sele != None ):
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    self.set_segn( n, nsegn )
                n+=1
        else:
            # No sele & no old segname: change all
            if( segn == None ):
                n=0
                while( n < self.size ):
                    self.set_segn( n, nsegn )
                    n+=1
            # Replace old segname by the new one
            else:
                curr_segn=string.split( segn )
                idx=0
                seg_size=self.seg_lim_size - 1
                while( idx < seg_size ):
                    if( self.get_segn( self.seg_lim[idx] ) in curr_segn ):
                        for n in range( self.seg_lim[idx], self.seg_lim[idx + 1] ):
                            self.set_segn( n, nsegn )
                    idx+=1
#        self.define_limits()


    def chg_resn( self, nresn, resn=None, sele=None ):
        # Change only selected atoms
        if( sele != None ):
            n=0
            while( n < self.size ):
                if( sele.issel( n ) ):
                    self.set_resn( n, nresn )
                n+=1
        else:
            # No sele & no old resname: change all
            if( resn == None ):
                n=0
                while( n < self.size ):
                    self.set_resn( n, nresn )
                    n+=1
            # Replace old resname(s) by the new one: loop over all
            else:
                curr_resn=string.split( resn )
                idx=0
                res_size=self.res_lim_size - 1
                while( idx < res_size ):
                    if( self.get_resn( self.res_lim[idx] ) in curr_resn ):
                        for n in range( self.res_lim[idx], self.res_lim[idx + 1] ):
                            self.set_resn( n, nresn )
                    idx+=1
#        self.define_limits()
            

    def hard_norm( self ):
#        lst_segn=self.segn[0]
#        lst_resn=self.resn[0]
#        lst_resid=self.resid[0]
#        lst_atmlst=[ self.atom[0] ]
        lst_segn=""
        lst_resn=""
        lst_resid=0
        lst_atmlst=[]
#
# Quick & dirty
#
#        n=1
#        acc=1
#        while( n < self.size ):
#            if( lst_segn != self.segn[n] ):
#                acc=1
#                lst_atmlst=[ self.atom[n] ]
#                lst_segn=self.segn[n]
#                lst_resn=self.resn[n]
#                lst_resid=self.resid[n]
#            elif( lst_resn != self.resn[n] or 
#                    lst_resid != self.resid[n] or 
#                    self.atom[n] in lst_atmlst ):
#                acc+=1
#                lst_atmlst=[ self.atom[n] ]
#                lst_resn=self.resn[n]
#                lst_resid=self.resid[n]
#            self.resid[n]=acc
#            lst_atmlst.append( self.atom[n] )
#            n+=1
#
# Further logical/physical separation...
#
        n=1
        acc=1
        while( n < self.size ):
            if( lst_segn != self.get_segn( n ) ):
                acc=1
                lst_atmlst=[ self.get_atom( n ) ]
                lst_segn=self.get_segn( n )
                lst_resn=self.get_resn( n )
                lst_resid=self.get_resid( n )
            elif( lst_resn != self.get_resn( n ) or 
                    lst_resid != self.get_resid( n ) or 
                    self.get_atom( n ) in lst_atmlst ):
                acc+=1
                lst_atmlst=[ self.get_atom( n ) ]
                lst_resn=self.get_resn( n )
                lst_resid=self.get_resid( n )
            self.set_resid( n, acc )
            lst_atmlst.append( self.get_atom( n ) )
            n+=1
#        self.define_limits()


    def norm_resid( self, segn=None, acc=0 ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __norm_resid_segn( self, segn, acc ):
            flg=0
            idx=0
            seg_size=self.seg_lim_size - 1
            while( flg == 0 and idx < seg_size ):
                if( segn == self.get_segn( self.seg_lim[idx] ) ):
                    flg=1
                else:
                    idx+=1
            if( flg == 1 ):
                for n in range( self.res_lim.index( self.seg_lim[idx] ), \
                self.res_lim.index( self.seg_lim[idx + 1] ) ):
                    acc+=1
                    m=self.res_lim[n]
                    while( m < self.res_lim[n + 1] ):
                        self.set_resid( m, acc )
                        m+=1
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( segn != None ):
            for item in string.split( segn ):
                __norm_resid_segn( self, item, acc )
        else:
            n=0
            ns=self.seg_lim_size - 1
            while( n < ns ):
                __norm_resid_segn( self, self.get_segn( self.seg_lim[n] ), acc )
                n+=1
#            for item in self.seg_lim[:-1]:
#                __norm_resid_segn( self, self.get_segn( item ), acc )


    def info( self, name=None, segn=None ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __segn_info( self, segn, fd ):
            flg=0
            idx=0
            seg_size=self.seg_lim_size - 1
            while( flg == 0 and idx < seg_size ):
                if( segn == self.get_segn( self.seg_lim[ idx ] ) ):
                    flg=1
                else:
                    idx+=1
            if( flg == 1 ):
                fd.write( "\n.: %s :.\n"%( segn ) )
                cnt=0
                m=-1
                for n in range( self.res_lim.index( self.seg_lim[idx] ), \
                self.res_lim.index( self.seg_lim[idx + 1] ) ):
                    m+=1
                    cnt+=1
                    if( m == 13 ): 
                        m=0
                        fd.write( "-\n" )
                    fd.write( "%s "%( self.get_resn( self.res_lim[n] ) ) )
                fd.write( "\n%d Residues\n"%( cnt ) )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        fd.write( "%d Atoms, %d Residues, %d Chains\n"% \
            ( self.size, self.res_lim_size - 1, self.seg_lim_size - 1 ) )
        if( segn != None ):
            for item in string.split( segn ):
                __segn_info( self, item, fd )
        else:
            n=0
            ns=self.seg_lim_size - 1
            while( n < ns ):
                __segn_info( self, self.get_segn( self.seg_lim[n] ), fd )
                n+=1
#            for item in self.seg_lim[:-1]:
#                __segn_info( self, self.get_segn( item ), fd )
        if( fd != sys.stdout ): fd.close()

    def info_seq( self, name=None ):
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        fd.write( "Sequence\n%5d\n"%( self.seg_lim_size - 1 ) )
        n=0
        nx=self.seg_lim_size - 1
        while( n < nx ):
            ri=self.res_lim.index(self.seg_lim[n])
            rf=self.res_lim.index(self.seg_lim[n+1])
            fd.write( "\nSubsystem %s\n%5d\n"%( self.get_segn( self.seg_lim[n] ), rf - ri ) )
            m=ri
            k=1
            while( m < rf ):
                fd.write( "%s ; "%( self.get_resn( self.res_lim[m] ) ) )
                if( k == 13 ):
                    fd.write( "\n" )
                    k=0
                k+=1
                m+=1
            fd.write( "\nEnd\n" )
            n+=1
        fd.write( "\nEnd" )
        if( fd != sys.stdout ): fd.close()
        

#
# Generic utilities and properties
#
    def mass_center( self, sele=None ):
        mc=[ .0, .0, .0 ]
        mt=.0
        if( sele == None ):
            m=0
            while( m < self.size ):
                mas=PTable_mass[ self.get_z( m ) ]
                pos=self.get_crd( m )
                mc[0]+=pos[0] * mas
                mc[1]+=pos[1] * mas
                mc[2]+=pos[2] * mas
                mt+=mas
                m+=1
        else:
            m=0
            while( m < self.size ):
                if( sele.issel( m ) ):
                    mas=PTable_mass[ self.get_z( m ) ]
                    pos=self.get_crd( m )
                    mc[0]+=pos[0] * mas
                    mc[1]+=pos[1] * mas
                    mc[2]+=pos[2] * mas
                    mt+=mas
                m+=1
        mc[0]/=mt
        mc[1]/=mt
        mc[2]/=mt
        return( mc )


    # Electric field given in Hartrees per Bohr
    def elec_fld( self, crd, sele=None ):
        efv=[ .0, .0, .0 ]
        dst=[ .0, .0, .0 ]
        if( sele == None ):
            m=0
            while( m < self.size ):
                pos=self.get_crd( m )
                dst[0]=( crd[0] - pos[0] ) / _a0
                dst[1]=( crd[1] - pos[1] ) / _a0
                dst[2]=( crd[2] - pos[2] ) / _a0
                mod_dst=Module( dst )
                if( mod_dst != .0 ):
                    chrg=self.get_chrg( m )
                    efv[0]+=chrg * dst[0] / ( mod_dst * mod_dst * mod_dst )
                    efv[1]+=chrg * dst[1] / ( mod_dst * mod_dst * mod_dst )
                    efv[2]+=chrg * dst[2] / ( mod_dst * mod_dst * mod_dst )
                m+=1
        else:
            m=0
            while( m < self.size ):
                if( sele.issel( m ) ):
                    pos=self.get_crd( m )
                    dst[0]=( crd[0] - pos[0] ) / _a0
                    dst[1]=( crd[1] - pos[1] ) / _a0
                    dst[2]=( crd[2] - pos[2] ) / _a0
                    mod_dst=Module( dst )
                    if( mod_dst != .0 ):
                        chrg=self.get_chrg( m )
                        efv[0]+=chrg * dst[0] / ( mod_dst * mod_dst * mod_dst )
                        efv[1]+=chrg * dst[1] / ( mod_dst * mod_dst * mod_dst )
                        efv[2]+=chrg * dst[2] / ( mod_dst * mod_dst * mod_dst )
                m+=1
        return( efv )
        

    # Electric potential given in Hartrees
    def elec_pot( self, crd, chrg, sele=None ):
        ept=.0
        dst=[ .0, .0, .0 ]
        if( sele == None ):
            m=0
            while( m < self.size ):
                pos=self.get_crd( m )
                dst[0]=( crd[0] - pos[0] ) / _a0
                dst[1]=( crd[1] - pos[1] ) / _a0
                dst[2]=( crd[2] - pos[2] ) / _a0
                mod_dst=Module( dst )
                if( mod_dst != .0 ):
                    ept+=chrg * self.get_chrg( m ) / mod_dst
                m+=1
        else:
            m=0
            while( m < self.size ):
                if( sele.issel( m ) ):
                    pos=self.get_crd( m )
                    dst[0]=( crd[0] - pos[0] ) / _a0
                    dst[1]=( crd[1] - pos[1] ) / _a0
                    dst[2]=( crd[2] - pos[2] ) / _a0
                    mod_dst=Module( dst )
                    if( mod_dst != .0 ):
                        ept+=chrg * self.get_chrg( m ) / mod_dst
                m+=1
        return( ept )
        

    def dip_moment( self, sele=None ):
        dip=[ .0, .0, .0 ]
        if( sele == None ):
            m=0
            while( m < self.size ):
                pos=self.get_crd( m )
                chrg=self.get_chrg( m )
                dip[0]+chrg * pos[0]
                dip[1]+chrg * pos[1]
                dip[2]+chrg * pos[2]
                m+=1
        else:
            m=0
            while( m < self.size ):
                if( sele.issel( m ) ):
                    pos=self.get_crd( m )
                    chrg=self.get_chrg( m )
                    dip[0]+chrg * pos[0]
                    dip[1]+chrg * pos[1]
                    dip[2]+chrg * pos[2]
                m+=1
        return( dip )


    # Could be done creating a new class, and returning it after...
    def convert_as_topo( self, conv_tab ):
        # Load the conversion table
        tab_res=[]
        tab_res_size=[]
        tab_labels_top=[]
        tab_labels_mol=[]
        fd=open( conv_tab, "rt" )
        line=fd.readline()
        while( line != "" ):
            splt=string.split( line )
            tab_res.append( splt[0] )
            tmp_top=[]
            tmp_mol=[]
            m=0
            max=string.atoi( splt[1] )
            tab_res_size.append( max )
            while( m < max ):
                line=fd.readline()
                splt=string.split( line )
                tmp_top.append( splt[0] )
                if( splt[1] == "#" ):
                    tmp_mol.append( splt[0] )
                else:
                    tmp_mol.append( splt[1] )
                m+=1
            tab_labels_top.append( tmp_top[:] )
            tab_labels_mol.append( tmp_mol[:] )
            del tmp_top, tmp_mol
            line=fd.readline()
        fd.close()
        # sort/modify current molecule: loop over each residue
        n=0
        max=self.res_lim_size - 1
        while( n < max ):
            idx_a=self.res_lim[n]
            idx_b=self.res_lim[n + 1]
            try:
                idx_t=tab_res.index( self.get_resn( idx_a ) )
            except ValueError:
                sys.stderr.write( "* Residue \'%s\' not found in topology\n"% \
                    ( self.get_resn( self.res_lim[n] ) ) )
            else:
                # loop over each table-atom, trying to find it in the molecule
                tmp_chrg=[]
                tmp_atom=[]
                tmp_crd=[]
                tmp_z=[]
                tmp_len=0
                m=0
                while( m < tab_res_size[idx_t] ):
                    k=idx_a
                    flg=0
                    while( k < idx_b and flg == 0 ):
                        flg=( tab_labels_mol[idx_t][m] == self.get_atom( k ) )
                        if( flg == 0 ): k+=1
                    if( flg == 1 ):
                        tmp_atom.append( tab_labels_top[idx_t][m] )
                        tmp_chrg.append( self.get_chrg( k ) )
                        tmp_crd.append( self.get_crd( k ) )
                        tmp_z.append( self.get_z( k ) )
                        tmp_len+=1
                    else:
                        sys.stderr.write( "* Atom \'%s\' not found in Residue \'%s%d\'\n"% \
                            ( tab_labels_mol[idx_t][m], tab_res[idx_t], self.get_resid( idx_a ) ) )
                    m+=1
                if( (idx_b-idx_a) > tmp_len ):
                    k=idx_a
                    while( k < idx_b ):
                        if( not self.get_atom( k ) in tab_labels_mol[idx_t] ):
                            tmp_atom.append( self.get_atom( k ) )
                            tmp_chrg.append( self.get_chrg( k ) )
                            tmp_crd.append( self.get_crd( k ) )
                            tmp_z.append( self.get_z( k ) )
                            sys.stderr.write( "* Extrange atom \'%s\' in Residue \'%s%d\'\n"% \
                                ( self.get_atom( k ), self.get_resn( idx_a ), self.get_resid( idx_a ) ) )
                        k+=1
                k=idx_a
                m=0
                while( k < idx_b ):
                    self.set_atom( k, tmp_atom[m] )
                    self.set_chrg( k, tmp_chrg[m] )
                    self.set_crd( k, tmp_crd[m] )
                    self.set_z( k, tmp_z[m] )
                    k+=1
                    m+=1
                del tmp_chrg, tmp_atom, tmp_crd, tmp_z
            n+=1
        del tab_res, tab_res_size, tab_labels_top, tab_labels_mol


# How to define external procedures to sort: Sort by default using the Z cartesian component
#
#    def compare ( data, id, ref, lt_flg ):
#        if ( lt_flg ):
#            return(data.get_crd(id)[2]<ref)
#        else:
#            return(data.get_crd(id)[2]>ref)
#
#    def getval ( data, id ):
#        return(data.get_crd(id)[2])
#
    def __quicksort( self, idx, lo0, hi0, getval, cmpcall ):
        lo=lo0
        hi=hi0
        if( hi0 > lo0 ):
            mid=getval( self,idx[( lo0 + hi0 ) / 2] )
            while( lo <= hi ):
                while( lo < hi0 and cmpcall( self, idx[lo], mid, 1 ) ): lo+=1
                while( hi > lo0 and cmpcall( self, idx[hi], mid, 0 ) ): hi-=1
                if( lo <= hi ):
                    tmp=idx[lo]
                    idx[lo]=idx[hi]
                    idx[hi]=tmp
                    lo+=1
                    hi-=1
            if( lo0 < hi ): self.__quicksort( idx, lo0, hi, getval, cmpcall )
            if( lo < hi0 ): self.__quicksort( idx, lo, hi0, getval, cmpcall )

    def sort( self, getval=None, cmpcall=None ):
        idx=range( self.size )
        self.__quicksort( idx, 0, self.size - 1, getval, cmpcall )
        return( idx )


    def charmm_sele( self, name=None, sele=None, byres=1 ):
        __trunc=50
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        # Quadruplicated code!!!! Yeah!!!!
        if( sele == None ):
            # Select by *full* residue
            if( byres == 1 ):
                fd.write( "Defi SS1 sele -\n" )
                res_size=self.res_lim_size - 1
                n=0
                acc=0
                who=1
                while( n < res_size ):
                    fd.write( "( Segid %s .And. Resi %d )"%( \
                        self.get_segn( self.res_lim[n] ), \
                        self.get_resid( self.res_lim[n] ) ) )
                    acc+=1
                    if( acc > __trunc ):
                        who+=1
                        acc=1
                        fd.write( " -\nEnd\nDefi SS%d sele -\n"%( who ) )
                    else:
                        fd.write( " .Or. -\n" )
                    n+=1
                fd.write( "End\nDefi MSel sele " )
                m=0
                while( m< ( who - 1 ) ):
                    fd.write( "SS%d .Or. "%( m + 1 ) )
                    m+=1
                fd.write( "SS%d end"%( who ) )
            # Ok, selected all atoms...
            else:
                fd.write( "Defi Core sele -\n" )
                n=0
                while( n < self.size ):
                    fd.write( "( Segid %s .And. Resi %d .And. Type %s ) .Or. -\n"%( \
                        self.get_segn( n ), self.get_resid( n ), self.get_atom( n ) ) )
                    n+=1
                fd.write( "End\n" )
        else:
            # Select by *full* residue
            if( byres == 1 ):
                fd.write( "Defi SS1 sele -\n" )
                res_size=self.res_lim_size - 1
                n=0
                acc=0
                who=1
                while( n < res_size ):
                    flg=0
                    idx=self.res_lim[n]
                    midx=self.res_lim[n + 1]
                    while( flg == 0 and idx < midx ):
                        flg|=sele.issel( idx )
                        idx+=1
                    if( flg == 1 ):
                        fd.write( "( Segid %s .And. Resi %d )"%( \
                            self.get_segn( self.res_lim[n] ), \
                            self.get_resid( self.res_lim[n] ) ) )
                        acc+=1
                        if( acc > __trunc ):
                            who+=1
                            acc=1
                            fd.write( " -\nEnd\nDefi SS%d sele -\n"%( who ) )
                        else:
                            fd.write( " .Or. -\n" )
                    # Jump to the next residue
                    n+=1
                fd.write( "End\nDefi MSel sele " )
                m=0
                while( m < ( who - 1 ) ):
                    fd.write( "SS%d .Or. "%( m + 1 ) )
                    m+=1
                fd.write( "SS%d end"%( who ) )
            # Ok, selected all atoms...
            else:
                fd.write( "Defi Core sele -\n" )
                n=0
                while( n < self.size ):
                    if( sele.issel( n ) ):
                        fd.write( "( Segid %s .And. Resi %d .And. Type %s ) .Or. -\n"%( \
                            self.get_segn( n ), self.get_resid( n ), self.get_atom( n ) ) )
                    n+=1
                fd.write( "End\n" )
        if( fd != sys.stdout ): fd.close()
    
    
    def dynamo_sele( self, name=None, sele=None ):
        __trunc=12
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        fd.write( "SUBROUTINE MY_SELE( SELE )\n" )
        fd.write( "\tUSE ATOMS, ONLY : NATOMS\n" )
        fd.write( "\tUSE ATOM_MANIPULATION, ONLY : ATOM_SELECTION\n" )
        fd.write( "\tLOGICAL, DIMENSION(1:NATOMS), INTENT(INOUT) :: SELE\n" )
        fd.write( "\tSELE = .FALSE.\n" )
        if( sele == None ):
            s_idx=0    
            s_len=len( self.seg_lim ) - 1
            while( s_idx < s_len ):
                fd.write( "\tSELE = SELE .OR. ATOM_SELECTION( &\n" )
                fd.write( "\t\tSUBSYSTEM = (/ \'%s\' /), &\n"%( self.get_segn( self.seg_lim[s_idx] ) ) )
                fd.write( "\t\tRESIDUE_NUMBER = (/ " )
                r_idxa=self.res_lim.index( self.seg_lim[s_idx] )
                r_idxb=self.res_lim.index( self.seg_lim[s_idx + 1] ) - 1
                acc=0
                while( r_idxa < r_idxb ):
                    fd.write( "%d, "%( self.get_resid( self.res_lim[r_idxa] ) ) )
                    acc+=1
                    if( acc > __trunc ):
                        fd.write( " &\n" )
                        acc=0
                    r_idxa+=1
                fd.write( "%d /) )\n"%( self.get_resid( self.res_lim[r_idxa] ) ) )
                s_idx+=1
            fd.write( "END SUBROUTINE\n" )
        else:
            idx_seg=0
            midx_seg=self.seg_lim_size - 1
            while( idx_seg < midx_seg ):
                tmp_res=[]
                tmp_n=0
                idx_res=self.res_lim.index( self.seg_lim[idx_seg] )
                midx_res=self.res_lim.index( self.seg_lim[idx_seg + 1] )
                while( idx_res < midx_res ):
                    flg=0
                    idx=self.res_lim[idx_res]
                    midx=self.res_lim[idx_res + 1]
                    while( flg == 0 and idx < midx ):
                        flg|=sele.issel( idx )
                        idx+=1
                    if( flg == 1 ):
                        tmp_res.append( idx_res )
                        tmp_n+=1
                    idx_res+=1
                if( tmp_n > 0 ):
                    fd.write( "\tSELE = SELE .OR. ATOM_SELECTION( &\n" )
                    fd.write( "\t\tSUBSYSTEM = (/ \'%s\' /), &\n"%( self.get_segn( self.seg_lim[idx_seg] ) ) )
                    fd.write( "\t\tRESIDUE_NUMBER = (/ " )
                    n=0
                    acc=0
                    tmp_n-=1
                    while( n < tmp_n ):
                        fd.write( "%d, "%( self.get_resid( self.res_lim[tmp_res[n]] ) ) )
                        acc+=1
                        if( acc > __trunc ):
                            fd.write( " &\n" )
                            acc=0
                        n+=1
                    fd.write( "%d /) )\n"%( self.get_resid( self.res_lim[tmp_res[tmp_n]] ) ) )
                del tmp_res
                idx_seg+=1
            fd.write( "END SUBROUTINE\n" )
        if( fd != sys.stdout ): fd.close()


    # HIGHLY EXPERIMENTAL CODE!!!
    # kind: 'sysbin' (dynamo) // 'psf' (charmm)
    def fill_charges( self, fname, kind='sysbin' ):
        fd=file( fname, 'rb' )
        for i in range( 6 ):
            fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
        fd.read( 4 )
        if( struct.unpack( 'i', fd.read( 4 ) )[0] == self.size ):
            fd.read( 4 )
            for i in range( 2 ):
                fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
            fd.read(4)
            i=0
            for z in struct.unpack( '%di'%( self.size ), fd.read( self.size * 4 ) ):
                self.z[i]=z
                i+=1
            fd.read(4)
            fd.read( struct.unpack( 'i', fd.read( 4 ) )[0] + 4 )
            fd.read(4)
            i=0
            for q in struct.unpack( '%dd'%( self.size ), fd.read( self.size * 8 ) ):
                self.chrg[i]=q
                i+=1
        fd.close()


#######################################################################
#                                                                     #
#  Selections                                                         #
#                                                                     #
#######################################################################
class Sele:
#
# Init all the variables...
#
    def __init__( self, size=0, mode=False ):
        self.data=[]
        self.size=size;
        n=0
        while( n < size ):
            self.data.append( mode )
            n+=1


    def __clean( self ):
        del self.data
        del self.size

    def __del__( self ):
        self.__clean()


    def issel( self, n ):
        return( self.data[n] )


    def count( self ):
        out=0
        n=0
        while( n < self.size ):
            if( self.issel( n ) ):
                out+=1
            n+=1
        return( out )

    
    def make_list( self ):
        out=[]
        n=0
        while( n < self.size ):
            if( self.issel( n ) ):
                out.append( n )
            n+=1
        return( out )


    def set_all( self, mode=True ):
        n=0
        while( n < self.size ):
            self.data[n]=mode
            n+=1


    def set( self, n, mode=True ):
        self.data[n]=mode


    # segn    :    string 
    # resn    :    string
    # resid   :    array
    # atom    :    array
    def select( self, molec, segn, resn='', resid=[], atom=[], mode=True ):
        if( self.size == 0 ):
            self.__init__( molec.size, not mode )
        if( atom != [] ):
            for n in atom:
                self.data[n]=mode
        else:
            segn_lst=string.split( segn )
            segn_size=molec.seg_lim_size - 1
            resn_lst=string.split( resn )
            # For each segname, search in the whole molecule
            for curr_segn in segn_lst:
                seg_idx=0
                seg_flg=0
                while( seg_flg == 0 and seg_idx < segn_size ):
                    if( molec.get_segn( molec.seg_lim[seg_idx] ) == curr_segn ):
                        seg_flg=1
                    else:
                        seg_idx+=1
                # Try with the resname or resid
                if( seg_flg == 1 ):
                    # Don't check for exceptions... IT SHOULD WORK!!!
                    res_idxa=molec.res_lim.index( molec.seg_lim[seg_idx] )
                    res_idxb=molec.res_lim.index( molec.seg_lim[seg_idx + 1] )
                    for curr_res in range( res_idxa, res_idxb ):
                        # Few items in resn & resid!!
                        resn_ok=0
                        for item in resn_lst:
                            resn_ok=resn_ok or molec.get_resn( molec.res_lim[curr_res] ) == item
                        resid_ok=0
                        for item in resid:
                            resid_ok=resid_ok or molec.get_resid( molec.res_lim[curr_res] ) == item
                        if( ( resn_ok == 1 and resid_ok == 1  ) or \
                        ( resn_ok == 1 and resid==[] ) or \
                        ( resn_lst == [] and resid_ok == 1 ) or \
                        ( resn_lst == [] and resid == [] ) ):
                            for n in range( molec.res_lim[curr_res], molec.res_lim[curr_res + 1] ):
                                self.data[n]=mode
    

    def rad_sel( self, molec, crd, rcut, mode=True ):
        if( self.size == 0 ):
            self.__init__( molec.size, not mode )
        n=0
        res_size=molec.res_lim_size - 1
        while( n < molec.size ):
            if( Dist( molec.get_crd( n ), crd ) <= rcut ):
                flg=0
                idx=0
                while( flg == 0 and idx < res_size ):
                    if( molec.res_lim[idx] > n ):
                        flg=1
                    else:
                        idx+=1
                if( flg == 1 ):
                    for m in range( molec.res_lim[idx - 1], molec.res_lim[idx] ):
                        self.data[m]=mode
                    # jump to the next residue...
                    n=molec.res_lim[idx] - 1
            n+=1


    def sph_sel( self, molec, sele, rcut, mode=1 ):
        if( self.size == 0 ):
            self.__init__( molec.size, not mode )
        # Smart, but not very optimal...
#        n=0
#        while ( n < sele.size ):
#            if ( sele.issel( n ) ):
#                self.rad_sel( molec, molec.get_crd( n ), rcut, mode )
#            n+=1
        # Only loop once over the moelcule:  sele.size < molec.size
        sele_crd=[]
        sele_siz=0
        res_size=molec.res_lim_size - 1
        n=0
        while( n < sele.size ):
            if( sele.issel( n ) ):
                sele_crd.append( n )
                sele_siz+=1
            n+=1
        n=0
        while( n < molec.size ):
            pos=molec.get_crd( n )
            shld_sele=0
            m=0
            while( m < sele_siz and shld_sele == 0 ):
                shld_sele=shld_sele or \
                    Dist( pos, molec.get_crd( sele_crd[m] ) ) <= rcut
                m+=1
            # Ok, any of the sub-selected is closer to this *residue*
            if( shld_sele == 1 ):
                flg=0
                idx=0
                while( flg == 0 and idx < res_size ):
                    if( molec.res_lim[idx] > n ):
                        flg=1
                    else:
                        idx+=1
                if( flg == 1 ):
                    for m in range( molec.res_lim[idx - 1], molec.res_lim[idx] ):
                        self.data[m]=mode
                    # jump to the next residue...
                    n=molec.res_lim[idx] - 1
            n+=1

    
    def bool_not( self ):
        n=0
        while( n < self.size ):
            self.data[n]=not self.data[n]
            n+=1


    def bool_or( self, sele ):
        n=0
        while( n < self.size ):
            self.data[n]=self.data[n] or sele.issel(n)
            n+=1
            

    def bool_and( self, sele ):
        n=0
        while( n < self.size ):
            self.data[n]=self.data[n] and sele.issel(n)
            n+=1

    def flush( self, molec ):
        out=Molec()
        n=0
        lseg=None
        lres=None
        lrid=None
        m=-1
        while( n < self.size ):
            if( self.issel( n ) ):
                m+=1
                out.size=out.size + 1
                out.segn.append( molec.get_segn( n ) )
                out.resn.append( molec.get_resn(n))
                out.resid.append( molec.get_resid( n ) )
                out.atom.append( molec.get_atom( n ) )
                out.crd.append( molec.get_crd( n ) )
                out.chrg.append( molec.get_chrg( n ) )
                out.z.append( molec.get_z( n ) )
                # Fill limits
                if( lrid != out.get_resid( m ) or \
                lres != out.get_resn( m ) or \
                lseg != out.get_segn( m ) ):
                    if( lseg != out.get_segn( m ) ):
                        out.seg_lim.append( m )
                        out.seg_lim_size+=1
                        lseg=out.get_segn( m )
                    out.res_lim.append( m )
                    out.res_lim_size+=1
                    lrid=out.get_resid( m )
                    lres=out.get_resn( m )
            n+=1
        out.seg_lim.append( out.size )
        out.seg_lim_size+=1
        out.res_lim.append( out.size )
        out.res_lim_size+=1
        return( out )
    

#######################################################################
#                                                                     #
#  Z-Matrix                                                           #
#                                                                     #
#######################################################################
class ZMat:
#
# Init all the variables...
#
    def __init__( self, size=0 ):
        self.size=size
        self.atom=[]
        self.dist=[]
        self.angl=[]
        self.dihe=[]
        self.na=[]
        self.nb=[]
        self.nc=[]
        # Z-Mat: Average vars
        self.aver_dist=[]
        self.aver_angl=[]
        self.aver_dcos=[]
        self.aver_dsin=[]
        self.aver_npts=.0
        # Define an empty structure, may be useless...
        n=0
        while( n < size ):
            self.atom.append( "X" )
            self.dist.append( .0 )
            self.angl.append( .0 )
            self.dihe.append( .0 )
            self.na.append( 0 )
            self.nb.append( 0 )
            self.nc.append( 0 )
            n+=1


    def __clean( self ):
        del self.size
        del self.atom
        del self.dist
        del self.angl
        del self.dihe
        del self.na
        del self.nb
        del self.nc

    def __del__( self ):
        self.__clean()


#
# Physical / Logical separation...
#
    def get_atom( self, n ):
        return( self.atom[n] )

    def get_dist( self, n ):
        return( self.dist[n] )

    def get_angl( self, n ):
        return( self.angl[n] )

    def get_dihe( self, n ):
        return( self.dihe[n] )

    def get_na( self, n ):
        return( self.na[n] )

    def get_nb( self, n ):
        return( self.nb[n] )

    def get_nc( self, n ):
        return( self.nc[n] )
        
    def set_atom( self, n, atom ):
        self.atom[n]=atom

    def set_dist( self, n, dist ):
        self.dist[n]=dist

    def set_angl( self, n, angl ):
        self.angl[n]=angl

    def set_dihe( self, n, dihe ):
        self.dihe[n]=dihe

    def set_na( self, n, na ):
        self.na[n]=na

    def set_nb( self, n, nb ):
        self.nb[n]=nb

    def set_nc( self, n, nc ):
        self.nc[n]=nc


#
# Misc functions..
#
    # Connectivity is provided as MOPAC one, but without the first
    # atom and without the "zeros", so no rearrangement of the position
    # of the atoms. May be in the future something will be done
    def load_conn( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            fd=open( name, "rt" )
        self.set_na( 1, string.atoi( fd.readline() ) )
        tmp=string.split( fd.readline() )
        if( len( tmp ) != 2 ): return
        self.set_na( 2, string.atoi( tmp[0] ) )
        self.set_nb( 2, string.atoi( tmp[1] ) )
        n=3
        while( n < self.size ):
            tmp=string.split( fd.readline() )
            if( len( tmp ) != 3 ): return
            self.set_na( n, string.atoi( tmp[0] ) )
            self.set_nb( n, string.atoi( tmp[1] ) )
            self.set_nc( n, string.atoi( tmp[2] ) )
            n+=1
        if( fd != sys.stdin ): fd.close()


    def import_crd( self, molec, sele_list=None, label=True ):
        if( not sele_list ):
            sele_list=range( molec.size )
        if( self.size == 0 ):
            self.__init__( len( sele_list ) )
        if( label ):
            self.set_atom( 0, molec.get_atom( sele_list[0] ) )
            self.set_atom( 1, molec.get_atom( sele_list[1] ) )
            self.set_atom( 2, molec.get_atom( sele_list[2] ) )
        self.set_dist( 0, .0 )
        self.set_angl( 0, .0 )
        self.set_dihe( 0, .0 )
        self.set_dist( 1, \
            Dist( molec.get_crd( sele_list[1] ), molec.get_crd( sele_list[self.get_na( 1 ) - 1] ) ) )
        self.set_angl( 1, .0 )
        self.set_dihe( 1, .0 )
        self.set_dist( 2, \
            Dist( molec.get_crd( sele_list[2] ), molec.get_crd( sele_list[self.get_na( 2 ) - 1] ) ) )
        self.set_angl( 2, \
            Angl( molec.get_crd( sele_list[2] ), \
                molec.get_crd( sele_list[self.get_na( 2 ) - 1] ), \
                molec.get_crd( sele_list[self.get_nb( 2 ) - 1] ) ) )
        self.set_dihe( 2, .0 )
        n=3
        while( n < self.size ):
            if( label ):
                self.set_atom( n, molec.get_atom( sele_list[n] ) )
            self.set_dist( n, \
                Dist( molec.get_crd( sele_list[n] ), molec.get_crd( sele_list[self.get_na( n ) - 1] ) ) )
            self.set_angl( n, \
                Angl( molec.get_crd( sele_list[n] ), \
                    molec.get_crd( sele_list[self.get_na( n ) - 1] ), \
                    molec.get_crd( sele_list[self.get_nb( n ) - 1] ) ) )
            self.set_dihe( n, \
                Dihe( molec.get_crd( sele_list[n] ), \
                    molec.get_crd( sele_list[self.get_na( n ) - 1] ), \
                    molec.get_crd( sele_list[self.get_nb( n ) - 1] ), \
                    molec.get_crd( sele_list[self.get_nc( n ) - 1] ) ) )
            n+=1
        

    def export_crd( self, molec, label=False ):
        if( molec.size == 0 ):
            molec.__init__( self.size )
            label=True
        # 1st
        if( label ):
            molec.set_atom( 0, self.get_atom( 0 ) )
        molec.set_crd( 0, [.0, .0, .0 ] )
        # 2nd
        if( label ):
            molec.set_atom( 1, self.get_atom( 1 ) )
        molec.set_crd( 1, [ molec.get_crd( 0 )[0] + self.get_dist( 1 ), .0, .0 ] )
        # 3rd
        if( label ):
            molec.set_atom( 2, self.get_atom( 2 ) )
        pos=[ .0, .0, .0 ]
        if( self.get_na( 2 ) == 1 ):
            pos[0]=molec.get_crd( 0 )[0] + \
                self.get_dist( 2 ) * math.cos( self.get_angl( 2 ) / _R2D )
        else:
            pos[0]=molec.get_crd( 1 )[0] - \
                self.get_dist( 2 ) * math.cos( self.get_angl( 2 ) / _R2D )
        pos[1]=self.get_dist( 2 ) * math.sin( self.get_angl( 2 ) / _R2D )
        molec.set_crd( 2, pos )
        # Other
        vb=[ .0, .0, .0 ]
        va=[ .0, .0, .0 ]
        vd=[ .0, .0, .0 ]
        n=3
        while( n < self.size ):
            if( label ):
                molec.set_atom( n, self.get_atom( n ) )
            cosa=math.cos( self.get_angl( n ) / _R2D )
            pa=molec.get_crd( self.get_na( n ) - 1 )
            pb=molec.get_crd( self.get_nb( n ) - 1 )
            vb[0]=pb[0] - pa[0]
            vb[1]=pb[1] - pa[1]
            vb[2]=pb[2] - pa[2]
            r=1. / Module( vb )
            if( math.fabs( cosa ) >= 0.9999999991 ):
                r=r * cosa * self.get_dist( n )
                pos[0]=pa[0] + vb[0] + r
                pos[1]=pa[1] + vb[1] + r
                pos[2]=pa[2] + vb[2] + r
                molec.set_crd( n, pos )
            else:
                pc=molec.get_crd( self.get_nc( n ) - 1 )
                va[0]=pc[0] - pa[0]
                va[1]=pc[1] - pa[1]
                va[2]=pc[2] - pa[2]
                xyb=math.sqrt( vb[0] * vb[0] + vb[1] * vb[1] )
                flag=0
                if( xyb <= 0.10 ):
                    xpa=va[2]
                    va[2]=-va[0]
                    va[0]=xpa
                    xpb=vb[2]
                    vb[2]=-vb[0]
                    vb[0]=xpb
                    xyb=math.sqrt( vb[0] * vb[0] + vb[1] * vb[1] )
                    flag=1
                costh=vb[0] / xyb
                sinth=vb[1] / xyb
                xpa=va[0] * costh + va[1] * sinth
                ypa=va[1] * costh - va[0] * sinth
                sinph=vb[2] * r
                cosph=math.sqrt( math.fabs( 1. - sinph * sinph ) )
                xqa=xpa * cosph + va[2] * sinph
                zqa=va[2] * cosph - xpa * sinph
                yza=math.sqrt( ypa * ypa + zqa * zqa )
                coskh=ypa / yza
                sinkh=zqa / yza
                if( yza < 1.0e-10 ):
                    coskh=1.
                    sinkh=.0 
                sina=math.sin( self.get_angl( n ) / _R2D )
                sind=-math.sin( self.get_dihe( n ) / _R2D )
                cosd=math.cos( self.get_dihe( n ) / _R2D )
                vd[0]=self.get_dist( n ) * cosa
                vd[1]=self.get_dist( n ) * sina * cosd
                vd[2]=self.get_dist( n ) * sina * sind
                ypd=vd[1] * coskh - vd[2] * sinkh
                zpd=vd[2] * coskh + vd[1] * sinkh
                xpd=vd[0] * cosph - zpd * sinph
                zqd=zpd * cosph + vd[0] * sinph
                xqd=xpd * costh - ypd * sinth
                yqd=ypd * costh + xpd * sinth
                if( flag == 1 ):
                    xrd=-zqd
                    zqd=xqd
                    xqd=xrd
                pos[0]=xqd + pa[0]
                pos[1]=yqd + pa[1]
                pos[2]=zqd + pa[2]
                molec.set_crd( n, pos )
            n+=1


    def average_start( self ):
        if( self.size == 0 ): return
        n=0
        while( n < self.size ):
            self.aver_dist.append( .0 )
            self.aver_angl.append( .0 )
            self.aver_dcos.append( .0 )
            self.aver_dsin.append( .0 )
            n+=1
        self.aver_npts=.0


    def average_append( self, molec, sele_list=None, label=True ):
        self.import_crd( molec, sele_list, label )
        self.aver_dist[1]+=self.get_dist( 1 )
        self.aver_dist[2]+=self.get_dist( 2 )
        self.aver_angl[2]+=self.get_angl( 2 )
        n=3
        while( n < self.size ):
            self.aver_dist[n]+=self.get_dist( n )
            self.aver_angl[n]+=self.get_angl( n )
            self.aver_dcos[n]+=math.cos( self.get_dihe( n ) / _R2D )
            self.aver_dsin[n]+=math.sin( self.get_dihe( n ) / _R2D )
            n+=1
        self.aver_npts+=1.


    def average_stop( self ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __fix_angle( x, y ):
            if ( x==.0 and y==.0 ): return(    .0 )
            if ( x>.0  and y==.0 ): return(    .0 )
            if ( x==.0 and y>.0  ): return(  90.  )
            if ( x<.0  and y==.0 ): return( 180.  )
            if ( x==.0 and y<.0  ): return( 270.  )
            o=math.acos( x / math.sqrt( x * x + y * y ) ) * _R2D
            if ( y>.0 ):
                return( o )
            else:
                return( 360. - o )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        self.set_dist( 0, .0 )
        self.set_angl( 0, .0 )
        self.set_dihe( 0, .0 )
        self.set_dist( 1, self.aver_dist[1] / self.aver_npts )
        self.set_angl( 1, .0 )
        self.set_dihe( 1, .0 )
        self.set_dist( 2, self.aver_dist[2] / self.aver_npts )
        self.set_angl( 2, self.aver_angl[2] / self.aver_npts )
        self.set_dihe( 2, .0 )
        n=3
        while ( n < self.size ):
            self.set_dist( n, self.aver_dist[n] / self.aver_npts )
            self.set_angl( n, self.aver_angl[n] / self.aver_npts )
            self.set_dihe( n, __fix_angle( self.aver_dcos[n], self.aver_dsin[n] ) )
            n+=1


#
# With ZMatrix, selections *must* be 3N-6 sized!! (Int. Coord.)
#
# Gaussian IO
#
#    def load_gauss ( self, name, sele=None ):
#        if ( name=='' ):
#            fd=sys.stdin
#        else:
#            fd=open(name,'rt')
#        self.__clean()
#        self.__init__()
#        line=fd.readline()
#        while ( line!='' ):
#            line=fd.readline()
#        if ( fd!=sys.stdin ): fd.close()


    def save_gauss( self, name=None, sele=None ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __const_var( fd, test ):
            if( test ): fd.write( "\tf" )
            fd.write( "\n" )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        # Flush connectivity table
        fd.write( "%-2s\n"%( self.get_atom( 0 ) ) )
        fd.write( "%-2s %2d d02\n"%( self.get_atom( 1 ), self.get_na( 1 ) ) )
        fd.write( "%-2s %2d d03 %2d a03\n"%( \
            self.get_atom( 2 ), self.get_na( 2 ), self.get_nb( 2 ) ) )
        n=3
        while( n < self.size ):
            fd.write( "%-2s %2d d%02d %2d a%02d %2d t%02d\n"%( \
                self.get_atom( n ), \
                self.get_na( n ), n + 1, \
                self.get_nb( n ), n + 1, \
                self.get_nc( n ), n + 1 ) )
            n+=1
        # Flush internal coordinates
        if( sele == None ):
            fd.write( "\nd02\t%lf\n"%( self.get_dist( 1) ) )
            fd.write( "d03\t%lf\n"%( self.get_dist( 2 ) ) )
            fd.write( "a03\t%lf\n"%( self.get_angl( 2 ) ) )
            n=3
            while( n < self.size ):
                fd.write( "d%02d\t%lf\n"%( n + 1, self.get_dist( n ) ) )
                fd.write( "a%02d\t%lf\n"%( n + 1, self.get_angl( n ) ) )
                fd.write( "t%02d\t%lf\n"%( n + 1, self.get_dihe( n ) ) )
                n+=1
        else:
            fd.write( "\nd02\t%lf"%( self.get_dist( 1 ) ) )
            __const_var( fd, sele.issel( 0 ) )
            fd.write( "d03\t%lf"%( self.get_dist( 2 ) ) )
            __const_var( fd, sele.issel( 1 ) )
            fd.write( "a03\t%lf"%( self.get_angl( 2 ) ) )
            __const_var( fd, sele.issel( 2 ) )
            n=3
            while( n < self.size ):
                nci=3 * n - 6
                fd.write( "d%02d\t%lf"%( n + 1, self.get_dist( n ) ) )
                __const_var( fd, sele.issel( nci ) )
                fd.write( "a%02d\t%lf"%( n + 1, self.get_angl( n ) ) )
                __const_var( fd, sele.issel( nci + 1 ) )
                fd.write( "t%02d\t%lf"%( n + 1, self.get_dihe( n ) ) )
                __const_var( fd, sele.issel( nci + 2 ) )
                n+=1
        fd.write( "\n\n" )
        if( fd != sys.stdout ): fd.close()


#
# Mopac (93) IO
#
#    def load_mopac ( self, name, sele=None ):
#        if ( name=='' ):
#            fd=sys.stdin
#        else:
#            fd=open(name,'rt')
#        self.__clean()
#        self.__init__()
#        line=fd.readline()
#        while ( line!='' ):
#            line=fd.readline()
#        if ( fd!=sys.stdin ): fd.close()


    def save_mopac( self, name=None, sele=None ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __const_var( fd, test ):
            if( test ): 
                fd.write( "  0")
            else:
                fd.write( "  1" )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        if( sele == None ):
            # 1st
            fd.write( " %2s%14.8lf%3d%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( \
                self.get_atom( 0 ), .0, 0, .0, 0, .0, 0, 0, 0, 0 ) )
            # 2nd
            fd.write( " %2s%14.8lf%3d%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( \
                self.get_atom( 1 ), self.get_dist( 1 ), 1, .0, 0, .0, 0, self.get_na( 1 ), 0, 0 ) )
            # 3rd
            fd.write( " %2s%14.8lf%3d%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( \
                self.get_atom( 2 ), \
                self.get_dist( 2 ), 1, \
                self.get_angl( 2 ), 1, \
                .0, 0, self.get_na( 2 ), self.get_nb( 2 ), 0 ) )
            n=3
            while( n < self.size ):
                fd.write( " %2s%14.8lf%3d%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( \
                    self.get_atom( n ), \
                    self.get_dist( n ), 1, \
                    self.get_angl( n ), 1, \
                    self.get_dihe( n ), 1, \
                    self.get_na( n ), self.get_nb( n ), self.get_nc( n ) ) )
                n+=1
        else:
            # 1st
            fd.write( " %2s%14.8lf%3d%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( \
                self.get_atom( 0 ), .0, 0, .0, 0, .0, 0, 0, 0, 0 ) )
            # 2nd
            fd.write( " %2s%14.8lf"%( self.get_atom( 1 ), self.get_dist( 1 ) ) )
            __const_var( fd, sele.issel( 0 ) )
            fd.write( "%13.7lf%3d%13.7lf%3d%5d%5d%5d \n"%( .0, 0, .0, 0, self.get_na( 1 ), 0, 0 ) )
            # 3rd
            fd.write( " %2s%14.8lf"%( self.get_atom( 2 ), self.get_dist( 2 ) ) )
            __const_var( fd, sele.issel( 1 ) )
            fd.write( "%13.7lf"%( self.get_angl( 2 ) ) )
            __const_var( fd, sele.issel( 2 ) )
            fd.write( "%13.7lf%3d%5d%5d%5d \n"%( .0, 0, self.get_na( 2 ), self.get_nb( 2 ), 0 ) )
            n=3
            while( n < self.size ):
                nci=3 * n - 6
                fd.write( " %2s%14.8lf"%( self.get_atom( n ), self.get_dist( n ) ) )
                __const_var( fd, sele.issel( nci ) )
                fd.write( "%13.7lf"%( self.get_angl( n ) ) )
                __const_var( fd, sele.issel( nci + 1 ) )
                fd.write( "%13.7lf"%( self.get_dihe( n ) ) )
                __const_var( fd, sele.issel( nci + 2 ) )
                fd.write( "%5d%5d%5d \n"%( self.get_na( n ), self.get_nb( n ), self.get_nc( n ) ) )
                n+=1
        fd.write( "\n" )
        if( fd != sys.stdout ): fd.close()


#######################################################################
#                                                                     #
#  Topologies                                                         #
#                                                                     #
#######################################################################
class Topo:
    def __init__( self ):
        self.size=0
        self.label=[]
        self.chrg=[]
        self.z=[]
# lista equvalente a self.res_lim, pero almacenando los nombres de los
# residuos para que la busqueda sea mas rapida (empleando .index)...
# el tamanyo sera por tanto res_lim_size-1
        self.resn=[]
        self.res_lim=[]
        self.res_lim_size=0


    def __clean( self ):
        del self.size
        del self.label
        del self.chrg
        del self.z
        del self.resn
        del self.res_lim
        del self.res_lim_size

    def __del__( self ):
        self.__clean()


    def get_label( self, n ):
        return( self.label[n] )
    
    def get_chrg( self, n ):
        return( self.chrg[n] )

    def get_z( self, n ):
        return( self.z[n] )

    def get_resn( self, n ):
        return( self.resn[n] )

    def set_label( self, n ,x ):
        self.label[n]=x

    def set_chrg( self, n, x ):
        self.chrg[n]=x

    def set_z( self, n, x ):
        self.z[n]=x


    def load_charmm( self, name=None ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __z_by_mass( mass ):
            # In proteins the most part of the atoms will be from the 1st row...
            n=1
            flg=0
            while( n < PTable_size and flg == 0 ):
                # Not very *impressive*... but seems it works...
                flg=int( PTable_mass[n] * 10 ) > int( mass * 10 )
                n+=1
            if( flg == 0 ): 
                return(0)
            else:
                return( n - 2 )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( name == None ):
            fd=sys.stdin
        else:
            fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        line=fd.readline()
        # Build a conversion table between labels & types...
        # takes advantage of non-overflow behaviour of string vars... ([0:__])
        flg=0
        while( line != "" and  flg == 0 ):
            flg=( line[0:4] == "MASS" )
            if( flg == 0 ): line=fd.readline()
        splt=string.split( line )
        conv_tbl=[ splt[2], __z_by_mass( string.atof( splt[3] ) ) ]
        flg=0
        while( line != "" and flg == 0 ):
            if( line[0:4] == "MASS" ):
                splt=string.split( line )
                conv_tbl.append( splt[2] )
                conv_tbl.append( __z_by_mass( string.atof( splt[3] ) ) )
            flg=( line[0] == "\n" )
            if( flg == 0 ): line=fd.readline()
        # Start loading residues...
        flg=0
        while( line != "" and flg == 0 ):
            if( line[0:4] == "RESI" or line[0:4] == "PRES" ):
                splt=string.split( line )
                self.resn.append( splt[1] )
                self.res_lim.append( self.size )
                self.res_lim_size+=1
            elif( line[0:4] == "ATOM" ):
                splt=string.split( line )
                self.size+=1
                self.label.append( splt[1] )
                self.chrg.append( string.atof( splt[3] ) )
                try:
                    z=conv_tbl.index( splt[2] )
                except ValueError:
                    self.z.append( 0 )
                else:
                    self.z.append( conv_tbl[z + 1] )
            flg=( line == "END\n" )
            line=fd.readline()
        del conv_tbl
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        if( fd != sys.stdin ): fd.close()

    
    def load_opls( self, name=None ):
        if( name == None ):
            fd=sys.stdin
        else:
            fd=open( name, "rt" )
        self.__clean()
        self.__init__()
        line=fd.readline()
        # Build a conversion table between labels & types...
        # Again takes advantage of non-overflow of string vars... ([0:__])
        flg=0
        while( line != "" and flg == 0 ):
            flg=( string.upper( line[0:4] ) == "TYPE" )
            line=fd.readline()
        conv_tbl=[]
        flg=0
        while( line != "" and flg == 0 ):
            if( line[0] != "!" ):
                splt=string.split( line )
                if( len( splt ) >= 4 ):
                    conv_tbl.append( splt[0] )
                    conv_tbl.append( string.atoi( splt[1] ) )
            line=fd.readline()
            flg=( string.upper( line[0:3] ) == "END" )
        # Start loadding the OPLS...
        flg=0
        while( line != "" and flg == 0 ):
            flg=( string.upper( line[0:4] ) == "RESI" )
            line=fd.readline()
        flg=0
        while( line!= "" and flg == 0 ):
            if( string.upper( line[0:4] ) == "RESI" ):
                self.resn.append( string.split( line )[1] )
                self.res_lim.append( self.size )
                self.res_lim_size+=1
                line=fd.readline()
                # Avoid f*cking comments...
                while( line[0] == "!" ): line=fd.readline()
                # store the residue length
                n=string.atoi( string.split( line )[0] )
                self.size+=n
                m=0
                while( m < n ):
                    line=fd.readline()
                    # Avoid f*cking comments...
                    while( line[0] == "!" ): line=fd.readline()
                    splt=string.split( line )
                    self.label.append( splt[0] )
                    self.chrg.append( string.atof( splt[2] ) )
                    try:
                        w=conv_tbl.index( splt[1] )
                    except ValueError:
                        self.z.append( 0 )
                    else:
                        self.z.append( conv_tbl[w + 1] )
                    m+=1
            flg=( string.upper( line[0:3] ) == "END" )
            line=fd.readline()
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        # Variants *not* implemented,...  append default values...
        self.resn.append( "NTER" )
        self.size+=4
        self.label.append( "N" )
        self.z.append( 7 )
        self.chrg.append( -.30 )
        self.label.append( "HT1" )
        self.z.append( 1 )
        self.chrg.append( .33 )
        self.label.append( "HT2" )
        self.z.append( 1 )
        self.chrg.append( .33 )
        self.label.append( "HT3" )
        self.z.append( 1 )
        self.chrg.append( .33 )
        self.res_lim.append( self.size )
        self.res_lim_size+=1

        self.resn.append( "CTER" )
        self.size+=3
        self.label.append( "C" )
        self.z.append( 6 )
        self.chrg.append( .7 )
        self.label.append( "OT1" )
        self.z.append( 8 )
        self.chrg.append( -.8 )
        self.label.append( "OT2" )
        self.z.append( 8 )
        self.chrg.append( -.8 )
        self.res_lim.append( self.size )
        self.res_lim_size+=1
        # -------------------------------- 
        del conv_tbl
        if( fd != sys.stdin ): fd.close()


    # term: 'TOP_RESN SEGN RESID...'
    def apply( self, molec, term="" ):
        r_n=0
        r_sz=molec.res_lim_size - 1
        # Find current residue in topology...
        while( r_n < r_sz ):
            r_m=molec.res_lim[r_n]
            try:
                t_i=self.resn.index( molec.get_resn( r_m ) )
            except ValueError:
                pass
            else:
# - Fix this using subvectors [:] for performig the identification...
                # Patch residue Charges & Z... SAME ORDER & SIZE!!!
                t_n=self.res_lim[t_i]
                t_s=self.res_lim[t_i + 1]
                while( t_n < t_s ):
                    molec.set_chrg( r_m, self.get_chrg( t_n ) )
                    molec.set_z( r_m, self.get_z( t_n ) )
                    r_m+=1
                    t_n+=1
# --------------------------------------------------------------------
            r_n+=1
        # Apply Terminals... Not full checking done...
        splt=string.split( term )
        ts=len(splt)
        if( ts > 0 ):
            n=0
            while( n < ts ):
                try:
                    t_i=self.resn.index( splt[n] )
                except ValueError:
                    pass
                else:
                    s_i=0
                    s_s=molec.seg_lim_size - 1
                    s_flg=0
                    while( s_i < s_s and s_flg == 0 ):
                        if( splt[n+1] == molec.get_segn( molec.seg_lim[s_i] ) ):
                            s_flg=1
                        else:
                            s_i+=1
                    try:
                        r_i=molec.res_lim.index( molec.seg_lim[s_i] )
                    except ValueError:
                        r_i=0
                    try:
                        r_s=molec.res_lim.index( molec.seg_lim[s_i + 1] )
                    except ValueError:
                        r_s=molec.res_lim_size - 1
                    r_flg=0
                    while( r_i < r_s and r_flg == 0 and s_flg == 1 ):
                        if( splt[n+2] == molec.get_resid( molec.res_lim[r_i] ) ):
                            r_flg=1
                        else:
                            r_i+=1
                    if( s_flg == 1 and r_flg == 1 ):
# - Fix this using subvectors [:] for performig the identification...
                        acc_t=self.res_lim[t_i]
                        acc_m=molec.res_lim[r_i]
                        m=0
                        s=self.res_lim[t_i + 1] - acc_t
                        while( m < s ):
                            molec.set_chrg( acc_m + m, self.get_chrg( acc_t + m ) )
                            molec.set_z( acc_m + m, self.get_z( acc_t + m ) )
                            m+=1
# -----------------------------------------------------------------------
                n+=3


    def save_conv_tab( self, name=None ):
        if( name == None ):
            fd=sys.stdout
        else:
            fd=open( name, "wt" )
        n=0
        max=self.res_lim_size - 1
        while( n < max ):
            n_a=self.res_lim[n]
            n_b=self.res_lim[n + 1]
            fd.write( "%s\t%d\n"%( self.get_resn( n ), n_b - n_a ) )
            while( n_a < n_b ):
                fd.write( "\t%s\t#\n"%( self.get_label( n_a ) ) )
                n_a+=1
            n+=1
        if ( fd != sys.stdout ): fd.close()
    

#######################################################################
#                                                                     #
#  Linear Algebra                                                     #
#                                                                     #
#######################################################################
# --------------------------------------------------------------------
# Vectors
# --------------------------------------------------------------------
class Vector:
    def __init__( self, n=0 ):
        self.size=n
        self.vec=[]
        m=0
        while( m < n ):
            self.vec.append( .0 )
            m+=1


    def get( self, n ):
        return( self.vec[n] )

    def set( self, n, x ):
        self.vec[n]=x

    def set_full( self, list ):
        self.size=len( list )
        del self.vec
        self.vec=list[:]


    def __clean( self ):
        del self.vec
        del self.size

    def __del__( self ):
        self.__clean()


    def module( self ):
        out=.0
        m=0
        while( m < self.size ):
            out+=self.get( m ) ** 2.
            m+=1
        return( math.sqrt( out ) )


    #  [ a0, a1, ..., an ]  ==  a0 + a1 · x + ... + an · x^n
    def poly_val( self, x ):
        out=.0
        n=0
        while( n < self.size ):
            out+=self.get( n ) * ( x ** n )
            n+=1
        return( out )

        
    def dot( self, vector ):
        out=.0
        if( self.size == vector.size ):
            m=0
            while( m < self.size ):
                out+=self.get( m ) * vector.get( m )
                m+=1
        return( out )


    # 'space' is a list containing so many vectors as the dimension minus 2
    def cross( self, space ):
        lspace=len( space )
        if( lspace == ( self.size - 2 ) ):
            ok=1
            i=0
            while( i < lspace ):
                ok=ok and ( self.size == space[i].size )
                i+=1
            if( ok ):
                out=Vector( self.size )
                tmp_mat=Matrix( self.size - 1 )
                i=0
                while( i < self.size ):
                    tmp_row=[]
                    k=0
                    while( k < self.size ):
                        if( k != i ):
                            tmp_row.append( self.get( k ) )
                        k+=1
                    tmp_mat.set_row( 0, tmp_row )
                    del tmp_row
                    j=0
                    while( j < lspace ):
                        tmp_row=[]
                        k=0
                        while( k < self.size ):
                            if( k != i ):
                                tmp_row.append( space[j].get( k ) )
                            k+=1
                        tmp_mat.set_row( j + 1, tmp_row )
                        del tmp_row
                        j+=1
                    out.set( i, ( (-1) ** i ) * tmp_mat.det() )
                    i+=1
                tmp_mat.__clean()
                return( out )
            else:
                return( Vector( 0 ) )
        else:
            return( Vector( 0 ) )


# --------------------------------------------------------------------
# Matrices
# --------------------------------------------------------------------
class Matrix:
    # By default build an identity matrix...
    def __init__( self, n, m=None ):
        self.n=n
        if( m == None ):
            self.m=n
        else:
            self.m=m
        self.mat=[]
        i=0
        while( i < self.n ):
            row=[]
            j=0
            while( j < self.m ):
                if( i == j ):
                    row.append( 1. )
                else:
                    row.append( .0 )
                j+=1
            self.mat.append( row )
            del row
            i+=1


    def __clean( self ):
        del self.mat

    def __del__( self ):
        self.__clean()


    def get( self, n, m ):
        return( self.mat[n][m] )
        
    def get_row( self, n ):
        return( self.mat[n][:] )
        
    def get_col( self, m ):
        out=[]
        n=0
        while( n < self.n ):
            out.append( self.get( n, m ) )
            n+=1
        return( out )

    def set( self, n, m , x ):
        self.mat[n][m]=x

    def set_row( self, n, list ):
        if( self.m == len( list ) ):
            i=0
            while( i < self.m ):
                self.set( n, i, list[i] )
                i+=1

    def set_col( self, m, list ):
        if( self.n == len( list ) ):
            j=0
            while( j < self.n ):
                self.set( j, m, list[j] )
                j+=1


    # Matrix * Vector: n·m x m·1 = n·1
    def vec_mult( self, vector ):
        if( self.m == vector.size ):
            out=Vector( self.n )
            i=0
            while( i < self.n ):
                tmp=.0
                j=0
                while( j < self.m ):
                    tmp+=self.get( i, j ) * vector.get( j )
                    j+=1
                out.set( i, tmp )
                i+=1
            return( out )
        else:
            return( Vector( 0 ) )
        

    # Matrix * Matrix: a·b x b·c = a·c
    def mat_mult( self, matrix ):
        if( self.m == matrix.n ):
            out=Matrix( self.n, matrix.m )
            i=0
            while( i < self.n ):
                j=0
                while( j < matrix.m ):
                    tmp=.0
                    k=0
                    while( k < self.m ):
                        tmp+=self.get( i, k ) * matrix.get( k, j )
                        k+=1
                    out.set( i, j, tmp )
                    j+=1
                i+=1
            return( out )
        else:
            return( Matrix( 0 ) )


    #
    # Only way to define recursive functions inside a class !?!?!?
    #
    # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
    def __det( self, mat, sz ):
        out=.0
        if( sz == 2 ):
            out=mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
        else:
            i=0
            while( i < sz ):
                if( mat[0][i] != .0 ):
                    tmp_mat=[]
                    j=1
                    while( j < sz ):
                        tmp=[]
                        k=0
                        while( k < sz ):
                            if( k != i ):
                                tmp.append( mat[j][k] )
                            k+=1
                        tmp_mat.append( tmp )
                        del tmp
                        j+=1
                    out+=( (-1) ** i ) * mat[0][i] * self.__det( tmp_mat, sz - 1 )
                    del tmp_mat
                i+=1
        return( out )
    # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
    def det( self ):
        if( self.n == self.m ):
            return( self.__det( self.mat, self.n ) )
        else:
            return( .0 )


    def inv( self ):
        if( self.n == self.m ):
            d=self.det()
            if( d != .0 ):
                out=Matrix( self.n )
                if( self.n == 2 ):
                    out.set( 0, 0,  self.get( 1, 1 ) / d )
                    out.set( 0, 1, -self.get( 1, 0 ) / d )
                    out.set( 1, 0, -self.get( 0, 1 ) / d )
                    out.set( 1, 1,  self.get( 0, 0 ) / d )
                else:
                    i=0
                    while( i < self.n ):
                        j=0
                        while( j < self.n ):
                            tmp_mat=[]
                            k=0
                            while( k < self.n ):
                                if( k != i ):
                                    tmp=[]
                                    l=0
                                    while( l < self.n ):
                                        if( l != j ):
                                            tmp.append( self.get( k, l ) )
                                        l+=1
                                    tmp_mat.append( tmp )
                                    del tmp
                                k+=1        
                            out.set( j, i, \
                            ( (-1) ** ( i + j ) ) * self.__det( tmp_mat, self.n - 1 ) / d )
                            del tmp_mat
                            j+=1
                        i+=1
                return( out )
            else:
                return( Matrix( 0 ) )


#
# Linear System Solvers...
#
    def gauss_jordan( self, ind ):
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        def __norm_rows( self, ind ):
            n=0
            while( n < ind.size ):
                max=math.fabs( self.get( n, 0 ) )
                min=max
                m=0
                while( m < ind.size ):
                    curr=math.fabs( self.get( m, 0 ) )
                    if( max < curr ): max=curr
                    if( min > curr ): min=curr
                    m+=1
                mid=( max + min ) / 2.
                if( mid != .0 ):
                    m=0
                    while( m < ind.size ):
                        self.set( n, m, self.get( n, m ) / mid )
                        m+=1
                    ind.set( n, ind.get( n ) / mid )
                n+=1
        def __swap_rows( self, ind ):
            max_it=ind.size ** 3        
            n=0
            o=0
            while( n < ind.size and o < max_it ):
                if( self.get( n, n ) == .0 ):
                    m=0
                    flg=0
                    while( m < ind.size and flg == 0 ):
                        if( self.get( m, n ) != .0 ):
                            mat_swap=self.get_row( n )
                            ind_swap=ind.get( n )
                            self.set_row( n, self.get_row( m ) )
                            ind.set( n, ind.get( m ) )
                            self.set_row( m, mat_swap )
                            ind.set( m, ind_swap )
                            flg=1
                        else:
                            m+=1
                    n=0
                else:
                    n+=1
                o+=1
            return( o < max_it )
        # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
        if( self.n != self.m or self.n != ind.size ):
            return( Vector( 0 ) )
        out=Vector( ind.size )
        #Check diagonal
        diag_ok=1
        n=0
        while( n < ind.size ):
            diag_ok=( diag_ok and self.get( n, n ) != .0 )
            n+=1
        if( diag_ok == 0 ):
            if( __swap_rows( self, ind ) == 0 ):
                return( Vector( 0 ) )
        # Norm rows
        __norm_rows( self, ind )
        # Lower diagonal
        l=0
        ls=ind.size - 1
        while( l < ls ):
            n=l + 1
            while( n < ind.size ):
                head=self.get( n, l )
                if( head != .0 ):
                    ind.set( n, ind.get( n ) * self.get( l, l ) - ind.get( l ) * head )
                    m=0
                    while( m < ind.size ):
                        self.set( n, m, self.get( l, l ) * self.get( n, m ) - head * self.get( l, m ) )
                        m+=1
                n+=1
            l+=1
        #Check diagonal
        diag_ok=1
        n=0
        while( n < ind.size ):
            diag_ok=( diag_ok and self.get( n, n ) != .0)
            n+=1
        if( diag_ok == 0 ):
            if( __swap_rows(self,ind)==0 ):
                return(Vector(0))
        # Norm rows
        __norm_rows( self, ind )
        # Upper diagonal
        u=ind.size - 1
        while( u > -1 ):
            n=u - 1
            while( n > -1 ):
                head=self.get( n, u )
                if( head != .0 ):
                    ind.set( n, ind.get( n ) * self.get( u, u ) - ind.get( u ) * head )
                    m=ind.size - 1
                    while( m > -1 ):
                        self.set( n, m, self.get( u, u ) * self.get( n, m ) - head * self.get( u, m ) )
                        m-=1
                n-=1
            u-=1
        #Check diagonal
        diag_ok=1
        n=0
        while( n < ind.size ):
            diag_ok=( diag_ok and self.get( n, n ) != .0 )
            n+=1
        if( diag_ok == 0 ):
            if( __swap_rows( self, ind ) == 0 ):
                return( Vector( 0 ) )
        # Flush result
        n=0
        while( n < ind.size ):
            out.set( n, ind.get( n ) / self.get( n, n ) )
            n+=1
        return( out )


    def cramer( self, ind ):
        if( self.n == self.m and self.n == ind.size ):
            d=self.det()
            if( d != .0 ):
                out=Vector( self.n )
                i=0
                while( i < self.n ):
                    tmp_mat=[]
                    j=0
                    while( j < self.n ):
                        tmp=[]
                        k=0
                        while( k < self.n ):
                            if( k == i ):
                                tmp.append( ind.get( j ) )
                            else:
                                tmp.append( self.get( j, k ) )
                            k+=1
                        tmp_mat.append( tmp )
                        del tmp
                        j+=1
                    out.set( i, self.__det( tmp_mat, self.n ) / d )
                    del tmp_mat
                    i+=1
                return( out )
            else:
                return( Vector( 0 ) )
        else:
            return( Vector( 0 ) )


    def solinv( self, ind ):
        if( self.n == self.m and self.n == ind.size ):
            mi=self.inv()
            if( mi.n > 0 ):
                out=mi.vec_mult( ind )
                del mi
                return( out )
            else:
                return( Vector( 0 ) )
        else:
            return( Vector( 0 ) )

    
#
# Fit data into a polynome of Nth degree
#
def PolyFit( vx, vy, order, method="G" ):
    # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
    def __gen_xsum( v, k ):
        out=.0
        n=0
        while( n < v.size ):
            out+=v.get( n ) ** k
            n+=1
        return( out )

    def __gen_yxsum( va, vb, k ):
        out=.0
        n=0
        while( n < va.size ):
            out+=va.get( n ) * vb.get( n ) ** k
            n+=1
        return( out )

    def __mean( v ):
        out=.0
        n=0
        while( n < v.size ):
            out+=v.get( n )
            n+=1
        return( out / v.size )
    # INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS - INTERNALS
    k=order + 1
    if( vx.size < k or vx.size != vy.size ):
        return( Vector( 0 ) )
    # Independent terms...
    ind=Vector( k )
    n=0
    while( n < k ):
        ind.set( n, __gen_yxsum( vy, vx, n ) )
        n+=1
    # Matrix terms...
    tmp_sums=[ vx.size ]
    n=1
    s=2 * k - 1
    while( n < s ):
        tmp_sums.append( __gen_xsum( vx, n ) )
        n+=1
    mat=Matrix( k )
    n=0
    while( n < k ):
        m=0
        while( m < k ):
            mat.set( n, m, tmp_sums[n + m] )
            m+=1
        n+=1
    del tmp_sums
    # Resolve the system 
    if( string.upper( method ) == "I" ):
        coeff=mat.solinv( ind )
    elif( string.upper( method ) == "C" ):
        coeff=mat.cramer( ind )
    else:
        coeff=mat.gauss_jordan( ind )
    del mat, ind
    if( coeff.size > 0 ):
        # Calculate correlation of the fit
        y_m=__mean( vy )
        y_d=.0
        y_s=.0
        n=0
        while( n < vx.size ):
            pv=vy.get( n ) - coeff.poly_val( vx.get( n ) )
            y_d+=pv ** 2
            y_s+=( vy.get( n ) - y_m ) ** 2
            n+=1
        return( math.sqrt( math.fabs( 1 - y_d / y_s ) ), coeff )
    else:
        return( 0, coeff )


#######################################################################
#                                                                     #
#  GNU Plot                                                           #
#                                                                     #
#######################################################################
class GPlot:
    def __init__( self ):
        self.GPLOT_PIPE="/tmp/gnu.%s.%d"%( os.environ["USER"], os.getpid() )
        self.GPLOT_EXEC="/usr/bin/env gnuplot"
        try:
            os.mkfifo( self.GPLOT_PIPE )
        except OSError:
            sys.stderr.write( "* Pipe already exists !?!?\n" )
        self.GPLOT_PID=os.fork()
        if( self.GPLOT_PID == 0 ):
            os.system( self.GPLOT_EXEC + " " + self.GPLOT_PIPE )
            os._exit( 0 )
        time.sleep( 2 )
        self.GPLOT_FD=open( self.GPLOT_PIPE, "wt" )

    def feed( self, line ):
        self.GPLOT_FD.write( line + "\n" )

    def plot( self ):
        self.GPLOT_FD.close()
        os.waitpid( self.GPLOT_PID, 0 )
        os.unlink( self.GPLOT_PIPE )


#######################################################################
#                                                                     #
#  VMD  (blocks reading from the pipe...)                             #
#                                                                     #
#######################################################################
class VMD:
    def __init__( self, molec, sele = None ):
        self.VMD_EXEC="/tmp/vmd.%s.%d.exe"%( os.environ["USER"], os.getpid() )
        self.VMD_PIPE="/tmp/vmd.%s.%d.scr"%( os.environ["USER"], os.getpid() )
        self.VMD_COOR="/tmp/vmd.%s.%d.pdb"%( os.environ["USER"], os.getpid() )
        try:
            os.mkfifo( self.VMD_PIPE )
        except OSError:
            sys.stderr.write( "* Pipe already exists !?!?\n" )
        fd=file( self.VMD_EXEC, "wt" )
        fd.write( "#!/usr/bin/bash\nexport VMDDIR=/usr/local/Chem/vmd-1.8.2\nexport VMDDISPLAYDEVICE=win\nexport VMDSCRHEIGHT=6.0\nexport VMDSCRDIST=-2.0\nexport VMDTITLE=off\nexport VMDSCRPOS=\"0 0\"\nexport VMDSCRSIZE=\"704 576\"\nexport VMD_WINGEOM=\"-geometry 80x11-0-0\"\nexport TCL_LIBRARY=$VMDDIR/lib/tcl\nexport TK_LIBRARY=$VMDDIR/lib/tk\nexport PYTHONHOME=$VMDDIR\nexport PYTHONPATH=$VMDDIR/scripts/python:$PYTHONPATH\nexport BABEL_DIR=/usr/local/Chem/babel-1.6\nexport VMDBABELBIN=$BABEL_DIR\nexport STRIDE_BIN=$VMDDIR/stride_LINUX\nexport SURF_BIN=$VMDDIR/surf_LINUX\nexport TACHYON_BIN=$VMDDIR/tachyon_LINUX\n$VMDDIR/vmd_LINUX -e %s > /dev/null"%( self.VMD_PIPE ) )
        fd.close()
        os.chmod( self.VMD_EXEC, stat.S_IRWXU )
        self.VMD_PID=os.fork()
        if( self.VMD_PID == 0 ):
            os.system( self.VMD_EXEC )
            os._exit( 0 )
        time.sleep( 2 )
        self.VMD_FD=open( self.VMD_PIPE, "wt" )
        self.VMD_FD.write( "menu main on\naxes location off\n" )
        molec.save_pdb( self.VMD_COOR, sele = sele )
        self.VMD_FD.write( "mol load pdb %s"%( self.VMD_COOR ) )
        if( sele != None ):
            pass
        self.VMD_FD.close()
        os.waitpid( self.VMD_PID, 0 )
        try:
            os.unlink( self.VMD_EXEC )
            os.unlink( self.VMD_PIPE )
            os.unlink( self.VMD_COOR )
        except OSError:
            pass


