!Program title
program dynai
     use dynamo
     implicit none

!Variables definition
        integer :: i, b1, b2
        logical, dimension(:), allocatable :: flg

!Print out the header
        call print_style( .false. )
        call dynamo_header


call mm_file_process ( 'borra', 'amberMine.DNA' )
call mm_system_construct ( "borra" , "start.seq")
call coordinates_read( "ok.crd" )


       allocate( flg(1:natoms) )

	
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



!Calculate the gradientcall gradient
call gradient

!Minimize by conjugate-gradient method
!call optimize_lbfgsb ( print_frequency = 5, step_number = 100000, gradient_tolerance = 0.01_dp )

call optimize_lbfgsb( &
		print_frequency = 1, &
		gradient_tolerance = 0.1_dp, &
		step_number = 5000 )


call coordinates_write( "new-mini_ok.crd" )


deallocate( flg )
end  
include 'in20.f90'



