program fistr
	use dynamo
	implicit none

	integer                            :: i, j, my_random, rnk
	logical, dimension(:), allocatable :: flg, acs
	character( len=256 )               :: si, sj
	real( kind=dp ), dimension(1:2)    :: cof

	call dynamo_header
        call abinitio_init

	call encode_integer( i, si, "(i4)" )

	call mm_file_process( "borra", "{forcefield}" )
	call mm_system_construct( "borra", "{sequence}" )
	call coordinates_read ( "{coordsIn}"  )

	allocate( flg(1:natoms), acs(1:natoms) )

        {qmSele}

	call abinitio_setup( acs )

	flg = .false.
	call my_sele_qmnb( flg )
	call atoms_fix( .not. flg )
	flg = flg .and. .not. acs

	call energy_initialize
	call energy_non_bonding_options ( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )
	skip_abinitio = .false.
        call energy

	deallocate( flg, acs )
	call abinitio_exit
	call dynamo_footer

end
include "with_gaussian.f90"
include "{flexiblePart}"

