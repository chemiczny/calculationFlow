!Program title
program dynai
     use dynamo
     implicit none

!Variables definition
        integer :: i, b1, b2, a1, a2, a3, a4
        logical, dimension(:), allocatable :: acs, flg
	real( kind=dp ), dimension(1:2) :: cof

!Print out the header
        call print_style( .false. )
        call dynamo_header

	call mm_file_process( "borra", "{forcefield}" )
	call mm_system_construct( "borra", "{sequence}" )
	call coordinates_read( "{coordsIn}" )


       allocate( acs(1:natoms), flg(1:natoms) )
       {qmSele}

	call mopac_setup ( &
		method    = '{method}', &
		charge    = {charge}, &
		selection = acs )
	call mopac_scf_options ( iterations = 500000 )

	
	flg = .false.
	call my_sele( flg )
	call atoms_fix( .not. flg ) 

call energy_initialize

!Initialize the non-bonding list cutoff options
call energy_non_bonding_options( &
     list_cutoff   = 18.0_dp, &	
     outer_cutoff  = 16.0_dp, &
     inner_cutoff  = 14.5_dp, &
     minimum_image = .true. )

{definedAtoms}
cof = (/ 1._dp, -1._dp /)

call constraint_initialize

{constraints}

call constraint_define( type = "MULTIPLE_DISTANCE", fc = 5000._dp, &
	eq = {coordScanStart}_dp, &
	weights = cof )

!Calculate the gradientcall gradient
call gradient

!Minimize by conjugate-gradient method
call optimize_conjugate_gradient ( print_frequency = 5, step_number = 100000, gradient_tolerance = {gradientTolerance}_dp )

call optimize_lbfgsb( &
                        print_frequency = 1, &
                        gradient_tolerance = {gradientTolerance}_dp, &
                        step_number = 5000 )


call coordinates_write( "{coordsOut}" )


deallocate( flg )
end  
include 'in20.f90'



