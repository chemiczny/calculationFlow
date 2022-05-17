program fistro
	use dynamo
	implicit none

	integer                            :: i, a1, a2, a3, my_random
	logical, dimension(:), allocatable :: acs
	character( len=256 )               :: si

	call dynamo_header

	call mm_file_process ( 'borra', '{forcefield}' )
	call mm_system_construct ( 'borra', '{sequence}' )
	call coordinates_read ( "{coordsIn}"  )

	allocate( acs(1:natoms) )
        {qmSele}

        write(*,*) "@", count( acs )
		 
		call mopac_setup ( &
		method    = '{method}', &
		charge    = {charge}, &
		selection = acs )
	call mopac_scf_options ( iterations = 500000 )

	acs = .false.
	call my_sele( acs )
	call atoms_fix( .not. acs )

	call energy_initialize
	call energy_non_bonding_options ( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )


	call energy
	!write(900,"(2f20.10)") geometry_distance( atmcrd, b1, b2 ) - &
	!	geometry_distance( atmcrd, b2, b3 ), eqm
	
	deallocate( acs )
	call dynamo_footer
end
include 'in20.f90'
