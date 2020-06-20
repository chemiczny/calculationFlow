
cat <<eof > min1_true.in
  minimize water coords
 &cntrl
   imin=1, maxcyc=50000, ncyc=2500, ntb=1, ntr=1,
 &end
 keep complex frozen
  500.0
RES 1 {noSolventNo}
END
END
eof

$PMEMD_RUN -O -i min1_true.in -c {coordsIn} -p {topology} -ref {coordsIn} -o min1_true.out -r min1_true.rst7
rm -f mdinfo


cat <<eof > min2_true.in
  minimize water coords
 &cntrl
   imin=1, maxcyc=50000, ncyc=2500, ntb=1, ntr=1,
 &end
 keep complex frozen
  250.0
RES 1 {noSolventNo}
END
END
eof

$PMEMD_RUN -O -i min2_true.in -c min1_true.rst7 -p {topology} -ref {coordsIn} -o min2_true.out -r min2_true.rst7
rm -f mdinfo


cat <<eof > min3_true.in
  minimize water coords
 &cntrl
   imin=1, maxcyc=10000, ncyc=2500, ntb=1, ntr=1,
 &end
 keep complex frozen
  100.0
RES 1 {noSolventNo} 
END
END
eof

$PMEMD_RUN -O -i min3_true.in -c min2_true.rst7 -p {topology} -ref {coordsIn} -o min3_true.out -r min3_true.rst7
rm -f mdinfo


cat <<eof > min4_true.in
  minimize water coords
 &cntrl
   imin=1, maxcyc=10000, ncyc=2500, ntb=1, ntr=1,
 &end
 keep complex frozen
   10.0
RES 1 {noSolventNo}
END
END
eof

$PMEMD_RUN -O -i min4_true.in -c min3_true.rst7 -p {topology} -ref {coordsIn} -o min4_true.out -r min4_true.rst7
rm -f mdinfo


cat <<eof > min5_true.in
  minimize all
 &cntrl
   imin=1, maxcyc=100000, ncyc=5000, ntb=1, ntr=1,
 &end
 keep complex frozen
    0.0
RES 1 {noSolventNo} 
END
END
eof

$PMEMD_RUN -O -i min5_true.in -c min4_true.rst7 -p {topology} -ref {coordsIn} -o min5_true.out -r min5_true.rst7
rm -f mdinfo
