PRO BETALIGHT_STANCAM,name

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Get the filenames of the files wanted for inspection ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; One can find more documentation from betalight_alfosc.pro! ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; HISTORY : GCC 31 July 2006
;           * Updated to handle MEF:
;           * Replaced READFITS(names[0],hf1,/SILENT) with
;                      MRDFITS(names[0],1,/SILENT, /UNSIGNED) etc
;                   &  MRDFITS(names[0],1,hf1,/SILENT, /UNSIGNED) etc
;           * Added    MRDFITS(names[0],0,hf0,/SILENT, /UNSIGNED) to get the
;             primary header info.
;           * Changes DATE to DATE-AVG in JULDAY() call. (not really necessary!)
;           * Replaced SPAWN with GETENV see fault report 519.
;
;           7 May 2007 RC/GCC
;           After change to IDL6.1 need to add line `CD,GETENV('PWD')' to get
;           current directory, for some reason?
;           8 Jan. 2008
;           Changed database server from geena to eeva c.f. pms
;           Renames from betalight_stancamST.pro to betalight_stancam.pro
;           Changed database name from qc to QC
;
;"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

CD,GETENV('PWD')

;SPAWN,'echo $NAMEOFFILE',res,err 
res = GETENV('NAMEOFFILE')


IF res EQ '' THEN BEGIN
 IF NOT KEYWORD_SET(name) THEN BEGIN
	name	= DIALOG_PICKFILE(/READ,FILTER='*.fits')
        IF name EQ '' THEN BEGIN
                PRINT,' '
                PRINT,' No file selected! Exiting. '
                PRINT,' '
                GOTO, loppu
        ENDIF
 ENDIF
ENDIF ELSE name = res

name = STRMID(name,12,13,/REVERSE_OFFSET)
dat	 = STRMID(name,0,4)        ; date of first file
a	 = FIX(STRMID(name,4,4))   ; number of first file
ext	 = STRMID(name,8)          ; extension
nimages	= 4                    ; number of images
names   = STRARR(4)            ; names of all images

FOR j=0, nimages - 1 DO BEGIN
        i       = j + a
  IF j MOD 6 NE 5 THEN BEGIN
        IF i LT 10 THEN BEGIN
                dt	= dat+'000'
                num	= STRMID(STRING(i),7,1)
        ENDIF           
        IF i GE 10 AND i LT 100 THEN BEGIN
                dt	= dat+'00'
                num	= STRMID(STRING(i),6,2)
        ENDIF
        IF i GE 100 AND i LT 1000 THEN BEGIN
                dt	= dat+'0'
		num	= STRMID(STRING(i),5,3)
        ENDIF
        IF i GE 1000 AND i LT 10000 THEN BEGIN
		dt	= dat
		num	= STRMID(STRING(i),4,4)
        ENDIF
	names[j]	= 'ST'+dt+num+ext
  ENDIF
ENDFOR

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Read Images and their headers and reorder ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

print,'start reading of MEF images'

f1 = MRDFITS(names[0],1,/SILENT, /UNSIGNED)
f2 = MRDFITS(names[1],1,/SILENT, /UNSIGNED)
b1 = MRDFITS(names[2],1,/SILENT, /UNSIGNED)
b2 = MRDFITS(names[3],1,/SILENT, /UNSIGNED)

;f1	= READFITS(names[0],hf1,/SILENT)
;f2	= READFITS(names[1],hf2,/SILENT)
;b1	= READFITS(names[2],hb1,/SILENT)
;b2	= READFITS(names[3],hb2,/SILENT)

;Get the secondary fits headers and put in hf1, hf2, hb1, hb2 (to be compatible)
naxis_dims = MRDFITS(names[0],1,hf1,/SILENT, /UNSIGNED)
naxis_dims = MRDFITS(names[1],1,hf2,/SILENT, /UNSIGNED)
naxis_dims = MRDFITS(names[2],1,hb1,/SILENT, /UNSIGNED)
naxis_dims = MRDFITS(names[3],1,hb2,/SILENT, /UNSIGNED)

print,'end reading of MEF images'

; **********************************************************************

images	= UINTARR(SXPAR(hf1,'NAXIS1'),SXPAR(hf1,'NAXIS2'),4)
images[*,*,0]	= f1
images[*,*,1]	= f2
images[*,*,2]	= b1
images[*,*,3]	= b2
order	= REVERSE(SORT([MEAN(f1),MEAN(f2),MEAN(b1),MEAN(b2)]))
f1	= images[*,*,order[0]]
f2	= images[*,*,order[1]]
b1	= images[*,*,order[2]]
b2	= images[*,*,order[3]]
heads	= [ [ hf1 ] , [ hf2 ] , [ hb1 ] , [ hb2 ] ]
hf1	= heads[*,order[0]]
hf2	= heads[*,order[1]]
hb1	= heads[*,order[2]]
hb2	= heads[*,order[3]]   

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Test that images are of same size ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

a	= SIZE(f1)
b	= SIZE(f2)
c	= SIZE(b1)
d	= SIZE(b2)
IF TOTAL(a EQ b AND a EQ c AND a EQ d) EQ 5 THEN BEGIN
	PRINT,' Images the same size '
ENDIF ELSE BEGIN
	PRINT,' Images not of same size! Aborted! '
	GOTO,loppu
END

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Cut edges out of the images ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

side	= MIN(a[1:2])
xbuf	= LONG((a[1]-(side-100))/2.)
ybuf	= LONG((a[2]-(side-100))/2.)

f1	= f1[xbuf:a[1]-xbuf,ybuf:a[2]-ybuf]
f2	= f2[xbuf:a[1]-xbuf,ybuf:a[2]-ybuf]
b1	= b1[xbuf:a[1]-xbuf,ybuf:a[2]-ybuf]
b2	= b2[xbuf:a[1]-xbuf,ybuf:a[2]-ybuf]

a       = SIZE(f1)
side    = MIN(a[1:2])

bsize	= 16.
nareas	= LONG(side/bsize)
c1	= LONG((side-bsize*nareas)/2.)
c2	= side-1
c3	= LONG((side-bsize*nareas)/2.)
c4	= side-1

cf1	= f1(c1:c2,c3:c4)
cf2	= f2(c1:c2,c3:c4)
cb1	= b1(c1:c2,c3:c4)
cb2	= b2(c1:c2,c3:c4)

a       = SIZE(cf1)
aa	= a(1)
bb	= a(2)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Measure some easy statistical properties ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

images=[[cf1],[cf2],[cb1],[cb2]]           ; kind of a cube
stats=fltarr(5,4)
FOR i=0,3 DO BEGIN
	stats(0,i)	= MIN(images(*,i*aa:(i+1)*(bb-1)))
	stats(1,i)	= MAX(images(*,i*aa:(i+1)*(bb-1)))
	stats(2,i)	= SIGCLIP_STDEV(images(*,i*aa:(i+1)*(bb-1)),MEAN=ma,MEDIAN=me)
	stats(3,i)	= ma
	stats(4,i)	= me
ENDFOR
PRINT,' '
PRINT,' Image statistics '
PRINT,'Image','Min','Max','Stdev','Mean','Median',FORMAT='((A14)5(A13))'
FOR i=0,3 DO PRINT,names(i),stats(*,i),FORMAT='((A15)5(F13.2))'
PRINT,' '

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Check difference of bias frames, should be smaller than the stdev ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

biasdiff	= ABS(stats(3,2)-stats(3,3))
IF biasdiff GT stats(2,2) OR biasdiff GT stats(2,3) THEN BEGIN
	PRINT,' '
	PRINT,' Difference of averages of bias frames',biasdiff
	PRINT,' is larger than the standard deviation'
	PRINT,' of either of the bias images         ',stats(2,2),stats(2,3)
	PRINT,' Aborted! '
	PRINT,' '
	GOTO,loppu
ENDIF

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Divide image to areas of 16x16 pix and   ;
; calculate statistics of individual areas ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

cube	= FLTARR(nareas*nareas,5,4)
imsecs	= FLTARR(bsize,bsize,4,nareas*nareas)
FOR i=0,3 DO BEGIN
  l=-1
  FOR j=0,nareas-1 DO BEGIN
	FOR k=0,nareas-1 DO BEGIN
	  l	= l+1
	  eka	= LONG(j*bsize)
	  toka	= LONG((j+1)*(bsize))-1
	  kol	= LONG(k*bsize+i*bb)
	  nel	= LONG((k+1)*(bsize)+(i)*bb)-1
	  cube(l,0,i)	= MIN(images(eka:toka,kol:nel))
	  cube(l,1,i)	= MAX(images(eka:toka,kol:nel))
	  cube(l,2,i)	= SIGCLIP_STDEV(images(eka:toka,kol:nel),MEAN=ma,MEDIAN=me)
	  cube(l,3,i)	= ma
	  cube(l,4,i)	= me
	  imsecs(*,*,i,l)	= images(eka:toka,kol:nel)
	ENDFOR
  ENDFOR
ENDFOR

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Calculate COUNTS, BIAS, RON and GAIN for individual areas ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

gaintbl	= FLTARR(nareas*nareas)
rontbl	= FLTARR(nareas*nareas)
FOR l=0,nareas*nareas - 1 DO BEGIN
  gaintbl(l)	= ((cube(l,3,0)+cube(l,3,1))-(cube(l,3,2)+cube(l,3,3)))/(($
  SIGCLIP_STDEV(imsecs(*,*,0,l)-imsecs(*,*,1,l)))^2-(			$
  SIGCLIP_STDEV(imsecs(*,*,2,l)-imsecs(*,*,3,l)))^2)
  rontbl(l)	= ( SIGCLIP_STDEV(imsecs(*,*,2,l)-imsecs(*,*,3,l)) )/SQRT(2.0)
ENDFOR

;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Print results to screen ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;

gainerr = SIGCLIP_STDEV(gaintbl,MEAN=gain,NREJECT=nr1)
gainerr = gainerr / SQRT(N_ELEMENTS(gaintbl) - nr1)   

ronerr  = SIGCLIP_STDEV(rontbl,MEAN=ron,NREJECT=nr2)
ron     = gain * ron
ronerr  = gain * ronerr / SQRT(N_ELEMENTS(rontbl) - nr2)

counterr= SIGCLIP_STDEV(cube[*,3,0:1],MEAN=counts,NREJECT=nr3)
counterr= counterr / SQRT(N_ELEMENTS(cube[*,3,0:1]) - nr3)

biaserr = SIGCLIP_STDEV(cube[*,3,2:3],MEAN=bias,NREJECT=nr4)
biaserr = biaserr / SQRT(N_ELEMENTS(cube[*,3,2:3]) - nr4)

PRINT,'COUNTS:',counts,' +/- ',counterr,FORMAT='(A9,F9.1,A5,F8.2)'
PRINT,'BIAS:  ',bias,' +/- ',biaserr, FORMAT='(A9,F9.1,A5,F8.2)'
PRINT,'GAIN:  ',gain,' +/- ',gainerr, FORMAT='(A9,F9.4,A5,F8.4)'
PRINT,'RON:   ',ron, ' +/- ',ronerr,  FORMAT='(A9,F9.4,A5,F8.4)'
PRINT,''

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; extract required keywords from the FITS header ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


; Read the primary header to obtain the data information
naxis_dims0 = MRDFITS(names[0],0,hf0,/SILENT, /UNSIGNED)

date	= JULDAY(FIX(STRMID(SXPAR(hf0,'DATE-AVG'),5,2))$
                ,FIX(STRMID(SXPAR(hf0,'DATE-AVG'),8,2))$
                ,FIX(STRMID(SXPAR(hf0,'DATE-AVG'),0,4)),0,0,0)-2400000d0
time	= SXPAR(hf0,'UT')

;date	= JULDAY(FIX(STRMID(SXPAR(hf1,'DATE-AVG'),5,2))$
;                 ,FIX(STRMID(SXPAR(hf1,'DATE-AVG'),8,2))$
;                 ,FIX(SXPAR(hf1,'DATE-AVG')),0,0,0)-2400000d0
;time	= SXPAR(hf1,'UT')

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Spawn mysql command to transfer data to database ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

server		= 'eeva.not.iac.es'
;server		= 'geena.not.iac.es'
user		= 'qc_user'
password	= 'qc_pass'
database	= 'QC'
table		= 'qc_stancam_CCD1'
fields		= $
'counts,counterr,bias,biaserr,gain,gainerr,ron,ronerr,juldate,ut,'+$
'name_flat1,name_flat2,name_bias1,name_bias2'

incmd	= 'mysql -B -e ''select * from '+table+' '' -q -n -D '+database+$
	' -h '+server+' -u '+user+' -p'+password
outcmd	= 'mysql -B -e ''INSERT INTO '+table+' ('+fields+') VALUES (('	$
	+STRING(counts)+'),('+STRING(counterr)+'),('			$
	+STRING(bias)+'),('+STRING(biaserr)+'),('+STRING(gain)+'),('	$
	+STRING(gainerr)+'),('+STRING(ron)+'),('+STRING(ronerr)+'),('	$
	+STRING(date)+'),('+STRING(time)$
        +'),("'+names[0]+'"),("'+names[1]+'"),("'+names[2]+'"),("'+names[3]$
        +'"))'' -q -n -D '+database+	$
	' -h '+server+' -u '+user+' -p'+password

SPAWN,incmd,answer,error,count=cntin
IF ((error[0] EQ '') EQ 0) THEN BEGIN
	PRINT,'There was an error accessing the database:'
	PRINT,error
	GOTO,loppu
ENDIF

trimr	= [0,8,8,8,16,8,24,7,31,8,39,9,49,8,57,8,66,7,74,11]
data	= FLTARR(cntin-1,10)
FOR j=1,cntin-1 DO BEGIN
	FOR i=0,19,2 DO BEGIN
		data[j-1,FIX(i/2.)]=FLOAT(STRMID(STRCOMPRESS(STRTRIM(answer[j],2)),trimr[i],trimr[i+1]))
	ENDFOR
ENDFOR

SPAWN,outcmd,answer,error,count=cntout
IF ((error[0] EQ '') EQ 0) THEN BEGIN
	PRINT,'There was an error accessing the database:'
	PRINT,error
	GOTO,loppu
ENDIF
;goto, loppu
;IF (3.*MEAN(data[*,1]) LT ABS(MEAN(data[*,0])-counts)) THEN		$
;	PRINT,'number of counts differs over 3 sigma from previous!'
;IF (3.*VARIANCE(data[*,1]) LT ABS(MEAN(data[*,1])-counterr)) THEN	$
;	PRINT,'error in number of counts differs too much from previous!'

IF (3.*MEAN(data[*,3]) LT ABS(MEAN(data[*,2])-bias)) THEN		$
	PRINT,'bias differs too much from previous!'
IF (3.*VARIANCE(data[*,3]) LT ABS(MEAN(data[*,3])-biaserr)) THEN	$
	PRINT,'error in bias differs too much from previous!'

IF (3.*MEAN(data[*,5]) LT ABS(MEAN(data[*,4])-gain)) THEN		$
	PRINT,'gain differs too much from previous!'
IF (3.*MEAN(data[*,5]) LT ABS(MEAN(data[*,5])-gainerr)) THEN		$
	PRINT,'error in gain differs too much from previous!'

IF (3.*MEAN(data[*,7]) LT ABS(MEAN(data[*,6])-ron)) THEN		$
	PRINT,'ron differs too much from previous!'
IF (3.*MEAN(data[*,7]) LT ABS(MEAN(data[*,7])-ronerr)) THEN		$
	PRINT,'error in ron differs too much from previous!'

loppu:

END
