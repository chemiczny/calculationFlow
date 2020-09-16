
cat <<eof > md_npt.in
  MD production run at 300K (constant pressure langevin; 1.0 ns)
 &cntrl
   nstlim=500000, dt=0.002,
   nscm=1000, iwrap=1,
   ntpr=500, ntwr=500, ntwx=500,
   ntx=5, irest=1, 
   tempi=303.0, temp0=303.0, ntt=3, gamma_ln=1.0, ig=-1,
   ntb=2, pres0=1.0, ntp=1, taup=2.0,
   ntc=2, ntf=2, cut=8.0,
   ntr=0,
 &end
eof

for i in {ns}
do
        j=$(( $i + 1 ))
        $PMEMD_RUN -O -i md_npt.in -c {mdDir}/md_rst_$i.nc -p {topology} -o {mdDir}/md$j.out -x {mdDir}/md$j.nc -r {mdDir}/md_rst_$j.nc 
        rm -f mdinfo
done


