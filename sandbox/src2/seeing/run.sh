#!/bin/tcsh
set bindir = '/home/postprocess/seeing_mon/src.v2'
foreach d ( /raid1/data/notcam/NCrc* /raid1/data/notcam/NCrd* /raid1/data/notcam/NCre* /raid1/data/notcam/NCrf*)
  if ( -d $d ) then
    pushd $d
      echo "working in $d ..."
      #foreach f (*.fits)
        $bindir/seeing.py $d/*.fits
      #end
    popd
  endif
end
