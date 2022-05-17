#!/usr/bin/env python

import	math
import	string
import	sys

class spline_1d:
	def __init__( self, x, y ):
		self.__n  = len( x )
		self.__x  = x[:]
		self.__y  = y[:]
		self.__y2 = list(range( self.__n ))
		# ------------------------------------------------ setup
		u = list(range( self.__n ))
		u[0] = .0
		u[self.__n - 1] = .0
		self.__y2[0] = .0
		self.__y2[self.__n - 1] = .0
		for i in range( 1, self.__n - 1 ):
			s = ( self.__x[i] - self.__x[i-1] ) / ( self.__x[i+1] - self.__x[i-1] )
			p = s * self.__y2[i-1] + 2.
			self.__y2[i] = ( s - 1. ) / p
			u[i]=( 6. * ( ( self.__y[i+1] - self.__y[i] ) / ( self.__x[i+1] - self.__x[i] ) - ( self.__y[i] - self.__y[i-1] ) / ( self.__x[i] - self.__x[i-1] ) ) / ( self.__x[i+1] - self.__x[i-1] ) - s * u[i-1] ) / p
		for i in range( self.__n - 2, -1, -1 ):
			self.__y2[i] = self.__y2[i] * self.__y2[i+1] + u[i]
		del u


	def calc( self, x ):
		rx = x
		if( rx < self.__x[0] ):
			rx = self.__x[0]
		if( rx > self.__x[self.__n - 1] ):
			rx = self.__x[self.__n - 1]
		klo = 1
		khi = self.__n - 1
		while( khi - klo > 1 ):
			k = ( khi + klo ) // 2
			if( self.__x[k] > rx ):
				khi = k
			else:
				klo = k
		h  = self.__x[khi] - self.__x[klo]
		a  = ( self.__x[khi] - rx ) / h
		b  = ( rx - self.__x[klo] ) / h
		ry = a * self.__y[klo] + b * self.__y[khi] + ( ( a ** 3 - a ) * self.__y2[klo] + ( b ** 3 - b ) * self.__y2[khi] ) * ( h * h ) / 6.
		dy = ( self.__y[khi] - self.__y[klo] ) / ( self.__x[khi] - self.__x[klo] ) + ( self.__x[khi] - self.__x[klo] ) * ( ( 3. * b * b - 1 ) * self.__y2[khi] - ( 3. * a * a - 1 ) * self.__y2[klo] ) / 6.
		return( (ry, dy) )



class spline_2d:
	def __init__( self, x, y, z ):
		self.__nx = len( x )
		self.__ny = len( y )
		self.__x  = x[:]
		self.__y  = y[:]
		self.__z  = z[:]
		# ------------------------------------------------ setup
		self.__z2x = range( self.__nx * self.__ny )
		t = range( self.__ny )
		for i in range( self.__nx ):
			for j in range( self.__ny ):
				t[j] = self.__z[self.__ny*i+j]
			o = spline_1d( self.__y, t )
			for j in range( self.__ny ):
				self.__z2x[self.__ny*i+j] = o._spline_1d__y2[j]
		del o, t
		t = range( self.__nx )
		self.__z2y = range( self.__nx * self.__ny )
		for j in range( self.__ny ):
			for i in range( self.__nx ):
				t[i] = self.__z[self.__ny*i+j]
			o = spline_1d( self.__x, t )
			for i in range( self.__nx ):
				self.__z2y[self.__ny*i+j] = o._spline_1d__y2[i]
		del o, t


	def calc( self, x, y ):
		tr = range( self.__nx )
		o = spline_1d( self.__y, self.__y )
		for i in range( self.__nx ):
			for j in range( self.__ny ):
				o._spline_1d__y[j]  = self.__z[self.__ny*i+j]
				o._spline_1d__y2[j] = self.__z2x[self.__ny*i+j]
			tr[i] = o.calc( y )[0]
		o = spline_1d( self.__x, tr )
		rx = o.calc( x )
		del o, tr
		tr = range( self.__ny )
		o = spline_1d( self.__x, self.__x )
		for j in range( self.__ny ):
			for i in range( self.__nx ):
				o._spline_1d__y[i]  = self.__z[self.__ny*i+j]
				o._spline_1d__y2[i] = self.__z2y[self.__ny*i+j]
			tr[j] = o.calc( x )[0]
		o = spline_1d( self.__y, tr )
		ry = o.calc( y )
		del o, tr
		return( (rx[0], rx[1], ry[1]) )



def parse_changing_Y( fname ):
	wx = []
	wy = []
	wz = []
	f = open( fname, "rt" )
	n = 0
	for l in f:
		t = l.split(  )
		if( len( t ) == 3 and l[0] != "#" ):
			n += 1
			wx.append( t[0] )
			wy.append( float( t[1] ) )
			wz.append( float( t[2] ) )
	f.close()
	ny = 0
	r = wx[ny]
	while( ny < n and r == wx[ny] ):
		ny += 1
	y = wy[0:ny]
	x = []
	for i in xrange( 0, n, ny ):
		x.append( string.atof( wx[i] ) )
	z = wz[0:n]
	return( x, y, z )



def parse_changing_X( fname ):
	wx = []
	wy = []
	wz = []
	f = open( fname, "rt" )
	n = 0
	for l in f:
		t = l.split(  )
		if( len( t ) == 3 and l[0] != "#" ):
			n += 1
			wx.append( string.atof( t[0] ) )
			wy.append( t[1] )
			wz.append( t[2] )
	f.close()
	nx = 0
	r = wy[nx]
	while( nx < n and r == wy[nx] ):
		nx += 1
	x = wx[0:nx]
	y = []
	for i in xrange( 0, n, nx ):
		y.append( string.atof( wy[i] ) )
	z = []
	ny = n / nx
	for i in xrange( nx ):
		for j in xrange( ny ):
			z.append( string.atof( wz[i+j*nx] ) )
	return( x, y, z )



cx = []
cy = []

f = open( "diffSmooth.log", "rt" )
for l in f:
	t = l.split(  )
	cx.append( float( t[0] ) )
	cy.append( float( t[1] ) )
f.close()
# -- spline needs data to be ordered from smaller to bigger...
if( cx[0] > cx[-1] ):
	cx.reverse()
	cy.reverse()
o = spline_1d( cx, cy )
f = open( "wham.log", "rt" )
g = open( "spline.log", "wt" )
for l in f:
	if( l[0] != "#" and l[0] != "*"):
		t = l.split(  )
		rx = float( t[1] )
		ry = float( t[3] )
		g.write( "%20.10lf%20.10lf\n"%( rx, ry + o.calc( rx )[0] ) )
g.close()
f.close()
