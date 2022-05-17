subroutine project_grt( n, x, w, g )
	implicit none
	integer, intent(in) :: n
	real*8, dimension(1:n), intent(in) :: x, w
	real*8, dimension(1:n), intent(inout) :: g

	real*8, dimension(:,:), allocatable :: gc
	real*8, dimension(1:3) :: mc
	real*8 :: t
	integer :: i, j, k

	allocate( gc(1:n,1:6) )
	mc = 0.0d0
	 t = 0.0d0
	do i = 1, n / 3
		j = 3 * ( i - 1 )
		t = t + ( 1.d0 / w(j+1) ) ** 2
		mc(1:3) = mc(1:3) + x(j+1:j+3) / w(j+1)
	end do
	mc = mc / t
	gc = 0.0d0
	do i = 1, n / 3
		j = 3 * ( i - 1 )
		gc(j+1,1) = 1.d0 / w(j+1)
		gc(j+2,2) = 1.d0 / w(j+2)
		gc(j+3,3) = 1.d0 / w(j+3)
		gc(j+2,4) = -( x(j+3) - mc(3) / w(j+1) )
		gc(j+3,4) =  ( x(j+2) - mc(2) / w(j+1) )
		gc(j+1,5) =  ( x(j+3) - mc(3) / w(j+1) )
		gc(j+3,5) = -( x(j+1) - mc(1) / w(j+1) )
		gc(j+1,6) = -( x(j+2) - mc(2) / w(j+1) )
		gc(j+2,6) =  ( x(j+1) - mc(1) / w(j+1) )
	end do
	do i = 1, 6
		do j = 1, i - 1
			t = dot_product( gc(1:n,i), gc(1:n,j) )
			gc(1:n,i) = gc(1:n,i) - t * gc(1:n,j)
		end do
		t = sqrt( dot_product( gc(1:n,i), gc(1:n,i) ) )
		gc(1:n,i) = gc(1:n,i) / t
	end do
	! G' = G - Tx * G dot Tx - ... - Rx * G dot Rx - ...
	do i = 1, 6
		g(1:n) = g(1:n) - dot_product( gc(1:n,i), g(1:n) ) * gc(1:n,i)
	end do
	deallocate( gc )
end subroutine


subroutine project_hrt( n, x, w, h )
	implicit none
	integer, intent(in) :: n
	real*8, dimension(1:n), intent(in) :: x, w
	real*8, dimension(1:n*(n+1)/2), intent(inout) :: h

	real*8, dimension(:,:), allocatable :: gc, hv
	real*8, dimension(1:6,1:6) :: vhv
	real*8, dimension(1:3) :: mc
	real*8 :: t
	integer :: i, ii, j, jj, k

	allocate( gc(1:n,1:6), hv(1:n,1:6) )
	mc = 0.0d0
	 t = 0.0d0
	do i = 1, n / 3
		j = 3 * ( i - 1 )
		t = t + ( 1.d0 / w(j+1) ) ** 2
		mc(1:3) = mc(1:3) + x(j+1:j+3) / w(j+1)
	end do
	mc = mc / t
	gc = 0.0d0
	do i = 1, n / 3
		j = 3 * ( i - 1 )
		gc(j+1,1) = 1.d0 / w(j+1)
		gc(j+2,2) = 1.d0 / w(j+1)
		gc(j+3,3) = 1.d0 / w(j+1)
		gc(j+2,4) = -( x(j+3) - mc(3) / w(j+1) )
		gc(j+3,4) =  ( x(j+2) - mc(2) / w(j+1) )
		gc(j+1,5) =  ( x(j+3) - mc(3) / w(j+1) )
		gc(j+3,5) = -( x(j+1) - mc(1) / w(j+1) )
		gc(j+1,6) = -( x(j+2) - mc(2) / w(j+1) )
		gc(j+2,6) =  ( x(j+1) - mc(1) / w(j+1) )
	end do
	do i = 1, 6
		do j = 1, i - 1
			t = dot_product( gc(1:n,i), gc(1:n,j) )
			gc(1:n,i) = gc(1:n,i) - t * gc(1:n,j)
		end do
		t = sqrt( dot_product( gc(1:n,i), gc(1:n,i) ) )
		gc(1:n,i) = gc(1:n,i) / t
	end do
	!  P = I - Tx dot Tx - ... - Rx dot Rx - ...
	! H' = P dot H dot P
	do ii = 1, 6
		do i = 1, n
			k = i * ( i - 1 ) / 2
			t = 0.0d0
			do j = 1, i
				k = k + 1
				t = t + h(k) * gc(j,ii)
			end do
			do j = i + 1, n
				k = k + j - 1
				t = t + h(k) * gc(j,ii)
			end do
			hv(i,ii) = t
		end do
		do jj = 1, ii
			vhv(jj,ii) = dot_product( gc(1:n,ii), hv(1:n,jj) )
			vhv(ii,jj) = vhv(jj,ii)
		end do
	end do
	k = 0
	do i = 1, n
		do j = 1, i
			t = 0.0d0
			do ii = 1, 6
				t = t - hv(i,ii) * gc(j,ii) - hv(j,ii) * gc(i,ii)
				do jj = 1, 6
					t = t + gc(j,jj) * vhv(jj,ii) * gc(i,ii)
				end do
			end do
			k = k + 1
			h(k) = h(k) + t
		end do
	end do
	deallocate( gc, hv )
end subroutine
