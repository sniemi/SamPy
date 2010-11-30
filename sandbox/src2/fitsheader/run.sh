#!/bin/tcsh
set bindir = '/home/postprocess/fitsheader/src'
cd /raid1/data/alfosc/ 
foreach d ( ALr* )
  if ( -d $d ) then
    pushd $d
      echo "working in $d ..."
      #foreach f (*.fits)
        $bindir/fits.py *.fits
      #end
    popd
  endif
end
