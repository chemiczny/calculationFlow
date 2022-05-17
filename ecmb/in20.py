#!/usr/bin/env python

import	ecmb

m = ecmb.Molec()
m.load_crd( "test.crd" )
x = ecmb.Sele()
x.select( m, "MOL" )
print x.count()
s = ecmb.Sele()
s.sph_sel( m, x, 20. )
m.dynamo_sele( "in20.f90", sele = s )
