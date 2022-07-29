program fistro
	use dynamo
	implicit none

	integer                            :: i, a1, a2, a3, a4, my_random
	logical, dimension(:), allocatable :: flg, acs
	character( len=256 )               :: si
	real( kind=dp ), dimension(1:2)    :: cof

	call dynamo_header

	call mm_file_process ( "borra", "{forcefield}" )
	call mm_system_construct ( "borra", "{sequence}" )
	call coordinates_read ( "{coordsIn}" )

	allocate(acs(1:natoms),  flg(1:natoms) )

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
	call energy_non_bonding_options ( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )

	{definedAtoms}

	cof = (/ 1._dp, -1._dp /)

	call constraint_initialize

{constraints}

	call constraint_define( type = "MULTIPLE_DISTANCE", & 
	fc = 2500._dp, &
	eq = {coordScanStart}_dp, &
 	weights = cof, &
	file = "pmf.dat"  )
	
	call gradient

	call random_initialize( i + my_random() )
	!call velocity_assign( 303._dp, .false. )
	call velocity_read("velocities.in")

	call dynamics_options( &
		time_step       = 0.0005_dp, &
		print_frequency = 100, &
		coordinate_file = "pmf.trj", &
		save_frequency = 100, &
		steps           = {pmfSteps} )
	call constraint_writing_start
	call langevin_verlet_dynamics( 303._dp, 100._dp )
	call constraint_writing_stop

	call coordinates_write( "{coordsOut}" )
	call velocity_write("velocities.out")

	deallocate( flg )
end
include 'in20.f90'
