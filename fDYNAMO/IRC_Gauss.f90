program fistro
	use dynamo
	implicit none

	integer                                      :: i, j, k, fd, it1, it2
	integer                                      :: acs_n, acs_n3, acs_nh
	logical, dimension(:), allocatable           :: acs, prv
	logical                                      :: flg
	real( kind=dp )                              :: max_rms, cur_rms, tmp, g_nrm
	real( kind=dp )                              :: lamb, l1, l2
	integer, dimension(:), allocatable           :: acs_i
	real( kind=dp ), dimension(:,:), allocatable :: evec
	real( kind=dp ), dimension(:), allocatable   :: eval, x_cur, g_cur, vec, mw, x_ref
	type( dcd_type )                             :: dcd

	integer, parameter :: it1_max = 200
	integer, parameter :: it2_max = 1500
	
	real( kind=dp ), parameter ::  large = 1000000._dp
	real( kind=dp ), parameter :: minstp = 0.02_dp
	real( kind=dp ), parameter ::    stp = 250._dp
	real( kind=dp ), parameter ::  l_tol = 0.00000001_dp

	real( kind=dp ), parameter :: dsp = 0.05_dp
	real( kind=dp ), parameter :: dir = {IRC_dir}._dp


	call dynamo_header

	call mm_file_process( "borra", "{forcefield}" )
	call mm_system_construct( "borra", "{sequence}" )
	call coordinates_read ( "{coordsIn}" )

	use_hessian_recalc = 1000
	use_hessian_numerical = .false.
	use_hessian_method = "BOFILL"

	allocate( acs(1:natoms), prv(1:natoms) )

	call my_sele_qmnb( prv )
	prv = .not. prv

	call atoms_fix( prv )

	call dcd_initialize( dcd )
	call dcd_activate_write( &
		file    = "dcd", &
		dcd     = dcd, &
		type    = "CORD", &
		natoms  = natoms, &
		nfixed  = nfixed, &
		nframes = 1500, &
		qfix    = atmfix )
       
        {qmSele}

        acs_n = count( acs )
	acs_n3 = 3 * acs_n
	acs_nh = acs_n3 * ( acs_n3 + 1 ) / 2
	allocate( acs_i(1:acs_n), mw(1:acs_n3) )
	j = 0
	do i = 1, natoms
		if( acs(i) ) then
			j = j + 1
			acs_i(j) = i
			k = 3 * ( j - 1 )
			mw(k+1:k+3) = 1._dp / sqrt( atmmas(i) )
		end if
	end do
        
        call abinitio_setup( acs )
	call energy_initialize
	call energy_non_bonding_options ( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.5_dp, &
		minimum_image = .true. )

	call energy

	allocate( eval(1:acs_n3), evec(1:acs_n3,1:acs_n3) )
	allocate( x_cur(1:acs_n3), g_cur(1:acs_n3), vec(1:acs_n3), x_ref(1:acs_n3) )

	call atoms_fix( .not. acs )
	call hessian
	k = 0
	do i = 1, acs_n3
		do j = 1, i
			k = k + 1
			atmhes(k) = atmhes(k) * mw(i) * mw(j)
		end do
	end do
	do i = 1, acs_n
		j = 3 * ( i - 1 )
		x_cur(j+1:j+3) = atmcrd(1:3,acs_i(i)) / mw(j+1)
	end do
	call project_hrt( acs_n3, x_cur, mw, atmhes )
	call symmetric_upper( atmhes, eval, evec )
	write(*,"(8f10.2)") eval
	write(*,"(a20,2f20.10)") ">>>  RP:", 0.0_dp, etotal

	call atoms_fix( prv )
	call gradient
	max_rms = .0_dp
	cur_rms = .0_dp
	do i = 1, natoms
		tmp = sum( atmder(1:3,i) ** 2 )
		cur_rms = cur_rms + tmp
		if( tmp > max_rms ) max_rms = tmp
	end do
	cur_rms = sqrt( cur_rms / real( 3 * nfree, kind = dp ) )
	max_rms = sqrt( max_rms / 3._dp )
	write(*,"(a20,2f20.10)") ">>> RMS:", cur_rms, max_rms
	call dcd_write( dcd, atmcrd, boxl )
	do i = 1, acs_n
		j = 3 * ( i - 1 )
		x_ref(j+1:j+3) = atmcrd(1:3,acs_i(i)) / mw(j+1)
	end do

	x_cur(1:acs_n3) = evec(1:acs_n3,1) / sqrt( sum( evec(1:acs_n3,1) * evec(1:acs_n3,1) ) ) * dsp * dir
	do i = 1, acs_n
		j = 3 * ( i - 1 )
		atmcrd(1:3,acs_i(i)) = atmcrd(1:3,acs_i(i)) + x_cur(j+1:j+3) * mw(j+1)
	end do

	call atoms_fix( prv .or. acs )
	call optimize_lbfgsb( &
		print_frequency    = 100, &
		gradient_tolerance = 0.4_dp, &
		step_number        = 1500 )

	call atoms_fix( prv )
	call gradient
	max_rms = .0_dp
	cur_rms = .0_dp
	do i = 1, natoms
		tmp = sum( atmder(1:3,i) ** 2 )
		cur_rms = cur_rms + tmp
		if( tmp > max_rms ) max_rms = tmp
	end do
	cur_rms = sqrt( cur_rms / real( 3 * nfree, kind = dp ) )
	max_rms = sqrt( max_rms / 3._dp )
	write(*,"(a20,2f20.10)") ">>> RMS:", cur_rms, max_rms
	call dcd_write( dcd, atmcrd, boxl )
	write(*,"(a20,2f20.10)") ">>>  RP:", sqrt( sum( x_cur ** 2 ) ), etotal

	it1 = 1
	do while( ( it1 < it1_max ) .and. &
			( ( cur_rms > 1.49_dp .or. max_rms > 2.23_dp ) .or. it1 < 10 ) )

		do i = 1, acs_n
			j = 3 * ( i - 1 )
			g_cur(j+1:j+3) = atmder(1:3,acs_i(i)) * mw(j+1)
			x_cur(j+1:j+3) = atmcrd(1:3,acs_i(i)) / mw(j+1)
		end do
		call project_grt( acs_n3, x_cur, mw, g_cur )
		call atoms_fix( .not. acs )
		call hessian( .false. )
		k = 0
		do i = 1, acs_n3
			do j = 1, i
				k = k + 1
				atmhes(k) = atmhes(k) * mw(i) * mw(j)
			end do
		end do
		call project_hrt( acs_n3, x_cur, mw, atmhes )
		call symmetric_upper( atmhes, eval, evec )
		g_nrm = sqrt( dot_product( g_cur, g_cur ) )
		g_cur = g_cur / g_nrm
		 eval = eval / g_nrm
		write(*,"(8f10.2)") eval
		do i = 1, acs_n3
			vec(i) = sum( evec(1:acs_n3,i) * g_cur(1:acs_n3) )
		end do
		lamb = .0_dp
		if( eval(1) < 0.0_dp ) then
			lamb = eval(1) - stp
			l1 = eval(1)
			l2 = - large
		end if

		it2 = 1
		flg = .true.
		do while( it2 < it2_max .and. flg )
			tmp = .0_dp
			do i = 1, acs_n3
				tmp = tmp + vec(i) * vec(i) / ( lamb - eval(i) )
			end do
			flg = dabs( lamb - tmp ) > l_tol
			if( flg ) then
				if( eval(1) > 0.0_dp ) then
					lamb = tmp
				else
					if( tmp < lamb ) l1 = lamb
					if( tmp > lamb ) l2 = lamb
					if( l2 > - large ) then
						lamb = 0.5_dp * ( l1 + l2 )
					else if( l2 == - large ) then
						lamb = lamb - stp
					end if
				end if
			end if
			it2 = it2 + 1
		end do
		write(*,"(2i6,g16.8)") it1, it2, lamb
		x_cur = matmul( evec, vec / ( lamb - eval ) )
		tmp = sqrt( dot_product( x_cur, x_cur ) )
		if( tmp > dsp ) x_cur = dsp / tmp * x_cur
		do i = 1, acs_n
			j = 3 * ( i - 1 )
			atmcrd(1:3,acs_i(i)) = atmcrd(1:3,acs_i(i)) + x_cur(j+1:j+3) * mw(j+1)
			x_cur(j+1:j+3) = atmcrd(1:3,acs_i(i)) / mw(j+1)
		end do

		call atoms_fix( prv .or. acs )
		call optimize_lbfgsb( &
			print_frequency    = 100, &
			gradient_tolerance = 0.4_dp, &
			step_number        = 1500 )

		call atoms_fix( prv )
		call gradient
		max_rms = .0_dp
		cur_rms = .0_dp
		do i = 1, natoms
			tmp = sum( atmder(1:3,i) ** 2 )
			cur_rms = cur_rms + tmp
			if( tmp > max_rms ) max_rms = tmp
		end do
		cur_rms = sqrt( cur_rms / real( 3 * nfree, kind = dp ) )
		max_rms = sqrt( max_rms / 3._dp )
		write(*,"(a20,2f20.10)") ">>> RMS:", cur_rms, max_rms
		write(*,"(a20,2f20.10)") ">>>  RP:", sqrt( sum( ( x_cur - x_ref ) ** 2 ) ), etotal
		call dcd_write( dcd, atmcrd, boxl )

		it1 = it1 + 1
	end do

	call flush( dcd%unit )
	close( dcd%unit )
	call coordinates_write( "{coordsOut}" )

	deallocate( eval, evec )
	deallocate( x_cur, g_cur, vec, mw, x_ref )
	deallocate( acs, prv )
	call dynamo_footer
end
include "{flexiblePart}"
include 'mep_project.f90'
include "with_gaussian.f90"
