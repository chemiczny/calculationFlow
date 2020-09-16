
cat <<eof > md_eq_nvt.in
  equilibrate structure (constant volume langevin; heat solvent over 100 ps)
 &cntrl
   nstlim=50000, dt=0.002,
   nscm=1000, iwrap=1,
   ntpr=500, ntwr=5000, ntwx=5000,
   ntx=1, irest=0,
   tempi=0.0, temp0=303.0, ntt=3, gamma_ln=0.1,
   ntb=1,
   ntc=2, ntf=2, cut=8.0,
   ntr=1,
  &end
  restrain backbone of the solute
  1.0
FIND
* * M *
SEARCH
RES 1 {noSolventNo}
END
END
eof

$PMEMD_RUN -O -i md_eq_nvt.in -c {coordsIn} -p {topology} -o eqnvt.out -ref {coordsIn} -r eqnvt_rst.nc -x eqnvt.nc
rm -f mdinfo


cat <<eof > md_eq_npt.in
  equilibrate structure (constant pressure langevin; 100 ps)
 &cntrl
   nstlim=50000, dt=0.002,
   nscm=1000, iwrap=1,
   ntpr=500, ntwr=5000, ntwx=5000,
   ntx=5, irest=1,
   tempi=303.0, temp0=303.0, ntt=3, gamma_ln=1.0, ig=-1,
   ntb=2, ntp=1, pres0=1.0, taup=1.0
  ntc=2, ntf=2, cut=8.0,
  ntr=1,
 &end
 restrain backbone of the solute
 1.0
FIND
* * M *
SEARCH
RES 1 {noSolventNo}
END
END
eof

$PMEMD_RUN -O -i md_eq_npt.in -c eqnvt_rst.nc -p {topology} -o eqnpt.out -ref eqnvt_rst.nc -r eqnpt_rst.nc -x eqnpt.nc
rm -f mdinfo

cp eqnpt_rst.nc md_rst_0.nc


