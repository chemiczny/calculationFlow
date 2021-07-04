proc generateRandomFrames { frames2save nf} {
	set randomFrames [ list ]

	while { [ llength $randomFrames ] < $frames2save } {
		lappend randomFrames [ expr int(rand()*$nf)]
		set randomFrames [ lsort -unique $randomFrames ]
	}

	return $randomFrames
}

proc uniqueList {listNotUnique} {
  set new  [ list ]
  foreach item $listNotUnique {
    if {[lsearch $new $item] < 0} {
    # if { $item ni $new }
      lappend new $item
    }
  }
  return $new
}

proc mass2atomicNumber { atomicMass } {
	set mass2atomicNumber [ dict create  1 1  \
		7 3 9 4 11 5 12 6 14 7 16 8 19 9 \
		23 11 24 12 27 13 28 14 31 15 32 16 35 17  \
		39 19   ]

	set integerMass [ expr round($atomicMass)]

	return [ dict get $mass2atomicNumber $integerMass ]

}

proc saveFrameAsCrd { crdFile frame subsystemDict subsystemOrder  } {
	set allSelection [ atomselect top "all" ]

	set atomsNo [ $allSelection num ]
	set residuesNo [ llength [  uniqueList [ $allSelection get residue ] ] ]
	set subsystemsNo [ llength $subsystemOrder ]

	set cell [pbc get -now] 

	set currentSubsystemId 1
	set currentAtomId 1

	set crdFile [  open $crdFile w  ]

	puts $crdFile "!==============================================================================="
	puts $crdFile [ format " %d %d     %d ! # of atoms, residues and subsystems." $atomsNo $residuesNo $subsystemsNo ]
	puts $crdFile "!==============================================================================="
	puts $crdFile "Symmetry     1"
	puts $crdFile [ format "ORTHORHOMBIC         %.10f    %.10f    %.10f" [ lindex $cell 0 0 ] [ lindex $cell 0 1 ] [ lindex $cell 0 2 ] ]
	puts $crdFile "!==============================================================================="


	foreach subsystemName $subsystemOrder {
		set subsystemSele [ dict get $subsystemDict $subsystemName ]

		set currentAtomId [ writeSubsystem $crdFile $subsystemSele $currentSubsystemId $subsystemName $currentAtomId $frame  ]

		incr currentSubsystemId
	}


	close $crdFile

}

proc writeSubsystem { crdFile subsystemSele currentSubsystemId subsystemName currentAtomId  frame  } {
	set currentResidueId 1

	puts $crdFile [ format "Subsystem    %d %s" $currentSubsystemId $subsystemName ]

	set allSele [ atomselect top $subsystemSele ]
	# puts "przed"
	set allResidues [ lsort -unique -integer [ $allSele get residue ] ]
	# puts "po"
	set residueNo [ llength $allResidues ]

	puts $crdFile [ format "  %d ! # of residues." $residueNo ]
	puts $crdFile "!==============================================================================="

	

	foreach residue $allResidues {

		# puts "poczatek"
		set residueSelect [ atomselect top "residue $residue" frame $frame ]
		# puts "po pierwszym selecie"
		set resname [ lindex [ $residueSelect get resname ] 0 ]
		set atomsNo [ $residueSelect num ]


		# puts "tutaj0"
		puts $crdFile [ format "Residue    %d  %s" $currentResidueId $resname ]
		# puts "tutaj1"
		puts $crdFile [ format "%d ! # of atoms." $atomsNo ]
		# puts "tutaj"
		set names [ $residueSelect get name ]
		set xCoords [ $residueSelect get x  ]
		set yCoords [ $residueSelect get y  ]
		set zCoords [ $residueSelect get z  ]
		set masses [ $residueSelect get mass ]

		foreach name $names x $xCoords y $yCoords z $zCoords mass $masses {

			set atomicnumber [ mass2atomicNumber $mass ]
			puts $crdFile [ format "    %5d %3s    %3d    %3.10f   %3.10f   %3.10f" $currentAtomId $name $atomicnumber $x $y $z  ]

			incr currentAtomId
		}

		incr currentResidueId

		if { $currentResidueId <= $residueNo } {
			puts $crdFile "!-------------------------------------------------------------------------------"
		}
		
	}

	puts $crdFile "!==============================================================================="
	return $currentAtomId
}

proc getBonds { sele } {
	set indexes [ $sele get index ]
	set bonds [ $sele getbonds ]

	set uniqueBonds [ list ]

	foreach ind $indexes bonded $bonds {

		foreach ind2 $bonded {
			lappend uniqueBonds [ lsort [ list $ind $ind2 ] ]
		}
		
	}

	return [ lsort -unique $uniqueBonds ]

}

proc writeForceField { ffFilename sele } {
	set ffFile [ open $ffFilename w]

	set resname [ lindex [ $sele get resname ] 0 ]

	puts $ffFile "!-------------------------------------------------------------------------------"
	puts $ffFile "Residue $resname"
	puts $ffFile "!-------------------------------------------------------------------------------"

	set atomsNo [ $sele num ]
	set bonds [ getBonds $sele ]
	set bondsNo [ llength $bonds ]

	puts $ffFile "! # Atoms, bonds and impropers. "
	puts $ffFile "$atomsNo $bondsNo 0"

	set names [ $sele get name ]
	set types [ $sele get type ]
	set charges [ $sele get charge ]

	foreach name $names type $types charge $charges {
		puts $ffFile "$name $type $charge"
	}

	puts $ffFile ""

	foreach bond $bonds {
		set index1 [ lindex $bond 0 ]
		set index2 [ lindex $bond 1 ]

		set name1 [  [ atomselect top "index $index1" ] get name ]
		set name2 [  [ atomselect top "index $index2" ] get name ]

		puts $ffFile "$name1 $name2"
	}


	close $ffFile
}

proc writeSequence { seqFile subsystemDict subsystemOrder } {
	set seqFile [ open $seqFile w ]

	set sequenceLen [ llength $subsystemOrder ]

	puts $seqFile "Sequence"
	puts $seqFile "    $sequenceLen"

	puts $seqFile ""

	foreach subsystemKey $subsystemOrder {
		puts $seqFile "Subsystem $subsystemKey"

		set subsystemSele [ atomselect top [ dict get $subsystemDict $subsystemKey ] ]
		set allResidues [ uniqueList [ $subsystemSele get residue ] ]
		set residuesNo [ llength $allResidues ]

		puts $seqFile "   $residuesNo"

		set resInLineCounter 0
		foreach res $allResidues {
			set resSele [ atomselect top "residue $res" ]
			set resname [ lindex [ $resSele get resname] 0 ]

			puts -nonewline $seqFile "$resname ; "
			incr resInLineCounter

			if { $resInLineCounter > 12 } {
				puts $seqFile ""
				set resInLineCounter 0
			}
		}

		puts $seqFile ""
		puts $seqFile "End"
		puts $seqFile ""

	}

	puts $seqFile "END"
	close $seqFile
}
package require pbctools

mol new {acmb_keto_wat.prmtop} type {parm7} first 0 last -1 step 1 waitfor 1
mol addfile {cooled.nc} type {netcdf} first 0 last -1 step 1 waitfor 1 0

pbc wrap -center com -centersel "resname MOL" -compound residue -all
set cell [pbc get -now] 

[ atomselect top "residue 0" ] set resname NGLU
[ atomselect top "residue 557" ] set resname CLYS

[ atomselect top "resname FAD" ] set name { O3' H3T C1' H1' C2' H2' C3' H3' C4' H4' C5' H5'1 H5'2 O4' O2' H2T N6 H61 \
 H62 C6 C5 N7 C8 H8 N9 C4 N3 C2 H2 N1 O5A PA OA1 OA2 OP PB OB1 OB2 O5B C1 H11 H12 C2Y H2X O2 HO2 C3 H3 O3 HO3 C4X H4 O4 \
  HO4 C5X H51 H52 N1X C2X O2X N3X H3X C4Y O4X N10 C10A C4A N5 C5A C9A C9 H9 C8X C7 C6X H6 C7M H7M1 H7M2 H7M3 C8M H8M1 H8M2 H8M3 }

set subsDict [ dict create A "protein" MOL "resname MOL" FAD "resname FAD" WAT "water" IONS {resname "Cl\-"  "Na\+" "CL\-"  "NA\+" } ]
set subsOrder [ list A MOL FAD WAT IONS ]

saveFrameAsCrd "test.crd" 1 $subsDict $subsOrder
writeSequence "test.seq" $subsDict $subsOrder
writeForceField "test.DNA" [ atomselect top "resname MOL" ]

exit
