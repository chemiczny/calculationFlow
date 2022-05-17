include "panadero.f90"
program de_mierda
	use dynamo
	use panadero
	implicit none

	integer :: i, j
	logical, dimension(:), allocatable :: acs, flg
	real( kind=dp ), dimension(:), allocatable :: x
	character( len=256 )               :: si


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

	
	call my_sele( flg )
	flg = flg .and. .not. acs 

	call energy_initialize
	call energy_non_bonding_options( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )

	use_hessian_numerical = .false.
	use_hessian_recalc = 1000
	use_hessian_method = "BOFILL"

	call energy

	call setup_optimization( &
		core_atoms         = acs, &
		envi_atoms         = flg, &
		step_number        = 1000, &
		gradient_tolerance = 0.5_dp, &
		print_frequency    = 1, &
		trajectory         = "snapshot.dcd" )

	allocate( x(1:3*count(acs)) )
	j = -3
	do i = 1, natoms
		if( acs(i) ) then
			j = j + 3
			x(j+1:j+3) = atmcrd(1:3,i)
		end if
	end do

	call baker_search( &
		fcalc              = egh_calc, &
		x                  = x, &
		print_frequency    = 1, &
		step_number        = 1000, &
		maximum_step       = 0.1_dp, &
		locate_saddle      = .{ts_search}., &
		gradient_tolerance = 1.0_dp )
		
	j = -3
	do i = 1, natoms
		if( acs(i) ) then
			j = j + 3
			atmcrd(1:3,i) = x(j+1:j+3)
		end if
	end do

	call cleanup_optimization

	call coordinates_write ( "{coordsOut}" )

	call atoms_fix( .not. ( flg .or. acs  ) ) !here
	call gradient
	j = next_unit()
	open( unit = j, file = "forces.dump", action = "write", form = "formatted" )
	do i = 1, natoms
	    write( j, "(4f20.10)") atmder(1:3,i), sqrt(sum(atmder(1:3,i)*atmder(1:3,i))/3._dp)
	end do
	close( j )

	call atoms_fix( .not. acs )
	use_hessian_recalc = 1
	call hessian
	open( unit = j, file = "hessian.dump", action = "write", form = "unformatted" )
	write( j ) atmhes
	close( j )
	call project_rotation_translation( atmhes, .true. )
	call normal_mode_frequencies( atmhes )
	do i = 1, 10
		call normal_mode_view( i, afact = 4._dp )
	end do

	deallocate( x, acs, flg )

	call dynamo_footer
end
include "{flexiblePart}"
