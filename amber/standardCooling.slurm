
cat <<eof > cooling.in
equilibrate structure (constant volume langevin; cool solvent over 100 ps)
 &cntrl
   nstlim=50000, dt=0.002,
   nscm=1000, iwrap=1,
   ntpr=500, ntwr=500, ntwx=500,
   ntx=5, irest=1,
   tempi=300.0, temp0=0.0, ntt=3, gamma_ln=0.05, ig=-1,
   ntb=2, pres0=1.0, ntp=1, taup=2.0,
   ntc=2, ntf=2, cut=8.0,
   ntr=0
  &end
eof

mpirun -np {processors} pmemd.MPI -O -i cooling.in -c {coordsIn} -p {topology} -o cooling.out -ref {coordsIn} -r {coordsOut} 
rm -f mdinfo
