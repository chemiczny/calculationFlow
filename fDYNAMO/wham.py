#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import	os
import	sys
import	math
import	string

class WHAM:
	def __init__( self, temp = 303., nbins = None ):
		self.__rt   = temp * 1.e-3 * 6.0221367e23 * 1.380658e-23
		self.__nb   = nbins
		self.__umb  = []
		self.__umbe = []
		self.__fc   = []
		self.__ref  = []
		self.__crd  = []
		self.__crdn = []
		self.__frq  = []
		self.__f    = []
		self.__rho  = []
		self.__pmf  = []
		self.__nw   = 0
		self.__idx  = []

	def __sort( self, idx, lst, lo0, hi0 ):
		lo = lo0
		hi = hi0
		if( hi0 > lo0 ):
			m = lst[ idx[ ( lo0 + hi0 ) / 2 ] ]
			while( lo <= hi ):
				while( lo < hi0 and lst[idx[lo]] < m ): lo += 1
				while( hi > lo0 and lst[idx[hi]] > m ): hi -= 1
				if( lo <= hi ):
					t = idx[lo]
					idx[lo] = idx[hi]
					idx[hi] = t
					lo += 1
					hi -= 1
			if( lo0 < hi ): self.__sort( idx, lst, lo0, hi )
			if( lo < hi0 ): self.__sort( idx, lst, lo, hi0 )

	def load_data( self, lst, dsp = 1.e-6 ):
		sch = '--scratch--.%d.%d'%( os.getpid(), os.getuid() )
		gd = file( sch, 'wt' )
		vmax = None
		vmin = None
		for fn in lst:
			fd = file( fn, 'rt' )
			t = string.split( fd.readline() )
			self.__fc.append( string.atof( t[0] ) )
			self.__ref.append( string.atof( t[1] ) )
			if( not vmax ): vmax = self.__ref[-1]
			if( not vmin ): vmin = self.__ref[-1]
			n = .0
			l = fd.readline()
			while( l != '' ):
				n += 1.
				v = string.atof( l )
				vmax = max( vmax, v )
				vmin = min( vmin, v )
				gd.write( l )
				l = fd.readline()
			fd.close()
			self.__frq.append( n )
			self.__idx.append( self.__nw )
			self.__nw += 1
		self.__sort( self.__idx, self.__ref, 0, self.__nw - 1 )
		gd.close()
		vmax += dsp
		vmin -= dsp
		if( not self.__nb ):
			self.__nb = 10 * self.__nw
		width = ( vmax - vmin ) / float( self.__nb )
		for i in xrange( self.__nb ):
			self.__crd.append( vmin + width * ( float( i + 1 ) - .5 ) )
			self.__crdn.append( .0 )
		fd = file( sch, 'rt' )
		l = fd.readline()
		while( l != '' ):
			v = string.atof( l )
			i = int( ( v - vmin ) / width )
			self.__crdn[i] += 1.
			l = fd.readline()
		fd.close()
		os.unlink( sch )

	def solve( self, maxit = 100000, toler = 1.e-3 ):
		for i in xrange( self.__nb ):
			self.__f.append( .0 )
			self.__rho.append( .0 )
			t = []
			e = []
			for j in xrange( self.__nw ):
				x = .5 * self.__fc[self.__idx[j]] * ( self.__crd[i] - self.__ref[self.__idx[j]] ) ** 2
				t.append( x )
				e.append( math.exp( - x / self.__rt ) )
			self.__umb.append( t[:] )
			self.__umbe.append( e[:] )
			del t, e
		f = False
		o = 0
		while( o < maxit and not f ):
			fold = self.__f[:]
			for i in xrange( self.__nb ):
				x = .0
				for j in xrange( self.__nw ):
					x += self.__frq[self.__idx[j]] * math.exp( - ( self.__umb[i][j] - self.__f[j] ) / self.__rt )
				self.__rho[i] = self.__crdn[i] / x
			for j in xrange( self.__nw ):
				x = .0
				for i in xrange( self.__nb ):
					x += self.__umbe[i][j] * self.__rho[i]
				self.__f[j] = - self.__rt * math.log( x )
			x = math.fabs( self.__f[0] - fold[0] )
			for j in xrange( 1, self.__nw ):
				x = max( x, math.fabs( self.__f[j] - fold[j] ) )
			f = x < toler
			o += 1
		print '# Number of Iterations: %d, MaxDiff: %.10lf, Converged: %s'%( o, x, f )
		if( f ):
			print '#\n#%9s%20s%20s%20s'%( 'Points', 'Reference', 'Force Constant', 'Free Energy' )
			for i in xrange( self.__nw ):
				print '#%9.0lf%20.10lf%20.10lf%20.10lf'%( self.__frq[self.__idx[i]], self.__ref[self.__idx[i]], self.__fc[self.__idx[i]], self.__f[i] )
			x = .0
			for i in xrange( self.__nb ):
				x += self.__rho[i]
			for i in xrange( self.__nb ):
				self.__rho[i] /= x
				if( self.__rho[i] > .0 ):
					self.__pmf.append( - self.__rt * math.log( self.__rho[i] ) )
				else:
					self.__pmf.append( .0 )
			x = self.__pmf[0]
			for i in xrange( 1, self.__nb ):
				x = max( x, self.__pmf[i] )
			print '#\n#%9s%20s%20s%20s'%( 'Points', 'Reference', 'Density', 'PMF' )
			for i in xrange( self.__nb ):
				print '%10.0lf%20.10lf%20.10lg%20.10lf'%( self.__crdn[i], self.__crd[i], self.__rho[i], self.__pmf[i] - x )






if( __name__ == '__main__' ):
	try:
		nb = string.atoi( sys.argv[1] )
	except:
		ni = 1
		nb = None
	else:
		ni = 2
	x = WHAM( nbins = nb )
	sys.stderr.write( '* Loading data...\n' )
	x.load_data( sys.argv[ni:] )
	sys.stderr.write( '* Solving WHAM...\n' )
	x.solve()
