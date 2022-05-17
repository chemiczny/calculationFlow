#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 10:48:33 2021

@author: michal
"""

import numpy as np
#import matplotlib.pyplot as plt

def moving_average(x, w):
    tailsLen = (w-1)//2
    return np.convolve(  [x[0]]*tailsLen +  list(x) + [x[-1]]*tailsLen  , np.ones(w), 'valid') / w

data = np.loadtxt("diff.log")
threshold = 18
offset = 0

x = data[:,0]
y = data[:,1]

numberOfPoints2extrapolate = 3
yFixed = list(y[:numberOfPoints2extrapolate])

for i in range(numberOfPoints2extrapolate, len(y)):
    x2fit = x[i-numberOfPoints2extrapolate: i]
    y2fit = yFixed[i-numberOfPoints2extrapolate: i]

    coeffsFitted = np.polyfit(x2fit, y2fit, 1)
    polyFit = np.poly1d(coeffsFitted)
    
    originalValue = y[i] + offset
    xVal = x[i]
    
    fittedValue = polyFit(xVal)
    
    if abs(fittedValue - originalValue) > threshold:
        offset = fittedValue - y[i]
        yFixed.append(y[i]+offset)
    else:
        yFixed.append(originalValue)

yFixed = np.array(yFixed)
yFixed -= min(yFixed)

#plt.figure()
#plt.plot(x, y)
#plt.plot(x, yFixed)

y = yFixed

logF = open("diffFixed.log", 'w')

for xVal, yVal in zip(x,y):
    logF.write("%20.10lf%20.10lf\n"%( xVal, yVal ) )

logF.close()


logF = open("diffSmooth.log", 'w')
ySmooth = moving_average(y, 3)
for xVal, yVal in zip(x,ySmooth):
    logF.write("%20.10lf%20.10lf\n"%( xVal, yVal ) )

logF.close()
#plt.plot(x, ySmooth)
#plt.legend(["original", "fixed", "smooth"])