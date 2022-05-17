program de_mierda
	use dynamo
	implicit none
	
	integer :: i, j, k, a1, a2, a3, a4, my_random
	character( len=10 ) :: si, sj
	logical, dimension(:), allocatable :: acs, flg
	real( kind=dp ), dimension(1:2) :: cof

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
	call atoms_fix( .not. ( flg .or. acs  )  )

	call energy_initialize
	call energy_non_bonding_options( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )

	{definedAtoms}
	
	cof = (/ 1._dp, -1._dp /)

	do i = 0, {iterNo}

		call encode_integer( i, si, "(i3)" )

		call constraint_initialize

{constraints}

		call constraint_define( type = "MULTIPLE_DISTANCE", fc = 5000._dp, &
			eq = {coordScanStart}_dp {scanDir} 0.05_dp * real( i, kind=dp ), &
			weights = cof )

		call gradient
		do k = 1, 1000
			if( grms < 40._dp ) cycle
			atmcrd = atmcrd - atmder / dsqrt( sum( atmder ** 2 ) ) * 0.01_dp
			call gradient
		end do
		call coordinates_write( "tmp.sd" )

		call optimize_conjugate_gradient( &
			step_size = 0.01_dp, &
			step_number = 10000, &
			print_frequency = 1, &
			gradient_tolerance = {gradientTolerance}_dp )

		call optimize_lbfgsb( &
			bracket = 2._dp, &
			step_number = 10000, &
			print_frequency = 1, &
			gradient_tolerance = {gradientTolerance}_dp )

		call coordinates_write( "seed.{scanDir}" // trim( si ) )
		write( 900, "(3f20.10)" ) &
			geometry_distance( atmcrd, a1, a2 ) - geometry_distance( atmcrd, a2, a3 ), &
			etotal
		call flush( 900 )


	end do

	deallocate( acs, flg )

	call dynamo_footer
end
include 'in20.f90'

