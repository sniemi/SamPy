PRO BETALIGHT_MOSCA,name

;**************************************************************************
;***                                                                    ***
;***            QUALITY MONITORING FOR MOSCA                            ***
;***                                                                    ***
;**************************************************************************

;                Silva Järvinen 7.6.2004


; Questions related to this program can be send anytime to:
; silva.jarvinen@iki.fi

; HISTORY : 1 Sept 2005 GC
;           Updated to handle MEF & new file naming
;           7 May 2007 RC/GCC
;           After change to IDL6.1 need to add line `CD,GETENV('PWD')' to get
;           current directory, for some reason?
;
;           4 Jan 2008
;           Changed database server from geena to eeva  c.f. pms
;           8 Jan 2008
;           Changed database name from qc to QC
;
;"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Get the filenames of the files wanted for inspection ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
start	= SYSTIME(/SECONDS)

 PRINT,'Computing things from MOSCA unbinned images'

;NOTE!!!!
;If FITS header keywords are changed, check all places where SXPAR is used.
;When going to MEF change READFITS to MRDFITS. 
;For more info look in IDL doc_library,'mrdfits'.
;Probably also other changes has to be done.
;AND TEST!!!

 CD,GETENV('PWD')

 IF NOT KEYWORD_SET(name) THEN BEGIN

	name	= DIALOG_PICKFILE(/READ,FILTER='*.fits')

	IF name EQ '' THEN BEGIN
		PRINT,' '
		PRINT,' No file selected! Exiting. '
		PRINT,' '
		;GOTO, loppu
	ENDIF

 ENDIF

;need to be changed because of extra `MO' characters in filename
name    = STRMID(name,14,15,/REVERSE_OFFSET)
dat	    = STRMID(name,2,4)		; date of first file
a	    = FIX(STRMID(name,6,4)) ; number of first file
ext	    = STRMID(name,10)		; extension (.fits)
nimages = 4				    ; number of images
names	= STRARR(4)			; names of all images


FOR j = 0 , nimages - 1 DO BEGIN

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

	names[j]	= 'MO'+dt+num+ext

  ENDIF

ENDFOR


;;;;;;;;;;;;;;;;;;;;;;
; Defining variables ;
;;;;;;;;;;;;;;;;;;;;;;

images  = UINTARR(100,100,4,4) ;xsize,ysize,images,chips
subf1	= FLTARR(4,100,10,10)  ; 4 chips, 100 subsubsecs, xsize, ysize
subf2	= FLTARR(4,100,10,10)  
subb1	= FLTARR(4,100,10,10)
subb2	= FLTARR(4,100,10,10)
stats	= FLTARR(4,4,5)
deltaf	= FLTARR(4,100,10,10)
deltab	= FLTARR(4,100,10,10)
stdvdf	= FLTARR(4,100)
stdvdb	= FLTARR(4,100)
scounts	= FLTARR(2,4,100)
sbias	= FLTARR(2,4,100)
sgain	= FLTARR(4,100)
sron	= FLTARR(4,100)
counts	= FLTARR(4)
cerr	= FLTARR(4)
bias	= FLTARR(4)
berr	= FLTARR(4)
gain	= FLTARR(4)
gerr	= FLTARR(4)
ron	= FLTARR(4)
rerr	= FLTARR(4)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Read Images and their headers  ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

print,'start reading of MEF images'

f1mef1 = MRDFITS(names[0],1,/SILENT, /UNSIGNED)
f1mef2 = MRDFITS(names[0],2,/SILENT, /UNSIGNED)
f1mef3 = MRDFITS(names[0],3,/SILENT, /UNSIGNED)
f1mef4 = MRDFITS(names[0],4,/SILENT, /UNSIGNED)
                        
f2mef1 = MRDFITS(names[1],1,/SILENT, /UNSIGNED)
f2mef2 = MRDFITS(names[1],2,/SILENT, /UNSIGNED)
f2mef3 = MRDFITS(names[1],3,/SILENT, /UNSIGNED)
f2mef4 = MRDFITS(names[1],4,/SILENT, /UNSIGNED)
                            
b1mef1 = MRDFITS(names[2],1,/SILENT, /UNSIGNED)
b1mef2 = MRDFITS(names[2],2,/SILENT, /UNSIGNED)
b1mef3 = MRDFITS(names[2],3,/SILENT, /UNSIGNED)
b1mef4 = MRDFITS(names[2],4,/SILENT, /UNSIGNED)
                            
b2mef1 = MRDFITS(names[3],1,/SILENT, /UNSIGNED)
b2mef2 = MRDFITS(names[3],2,/SILENT, /UNSIGNED)
b2mef3 = MRDFITS(names[3],3,/SILENT, /UNSIGNED)
b2mef4 = MRDFITS(names[3],4,/SILENT, /UNSIGNED)

;Get the primary fits header and put in hf1 (to be compatible)
naxis_dims = MRDFITS(names[0],0,hf1,/SILENT, /UNSIGNED)

print,'end reading of MEF images'

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Test that images are of same size ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

a   = SIZE(f1mef1)
b   = SIZE(f2mef1)
c   = SIZE(b1mef1)
d   = SIZE(b2mef1)

IF TOTAL(a EQ b AND a EQ c AND a EQ d) EQ 5 THEN BEGIN

	PRINT,''
	PRINT,' Images sizes match OK '
	PRINT,''

ENDIF ELSE BEGIN

	PRINT,''
	PRINT,' Images not of same size! Aborted! '
	PRINT,''
	;GOTO,loppu

END


;;;;;;;;;;;;;;;;;;;;;;
; Taking subsections ;
;;;;;;;;;;;;;;;;;;;;;;

;W15, top right
images[*,*,0,0] = f1mef1[1900:1999,1900:1999]
images[*,*,1,0] = f2mef1[1900:1999,1900:1999]
images[*,*,2,0] = b1mef1[1900:1999,1900:1999]
images[*,*,3,0] = b2mef1[1900:1999,1900:1999]
;17, top left
images[*,*,0,1] = f1mef2[50:149,1900:1999]
images[*,*,1,1] = f2mef2[50:149,1900:1999]
images[*,*,2,1] = b1mef2[50:149,1900:1999]
images[*,*,3,1] = b2mef2[50:149,1900:1999]
;W19, bottom left
images[*,*,0,2] = f1mef4[50:149,50:149]
images[*,*,1,2] = f2mef4[50:149,50:149]
images[*,*,2,2] = b1mef4[50:149,50:149]
images[*,*,3,2] = b2mef4[50:149,50:149]
;W20, bottom right
images[*,*,0,3] = f1mef3[1900:1999,50:149]
images[*,*,1,3] = f2mef3[1900:1999,50:149]
images[*,*,2,3] = b1mef3[1900:1999,50:149]
images[*,*,3,3] = b2mef3[1900:1999,50:149]


;order below 0,1,2,3 (=W15,W17,W19,W20)
;selected area is 100x100 pixels in each quadrant

FOR j=0,3 DO BEGIN	; loop inside one subsec 100x100

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Dividing selected subsection into smaller boxes ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; This is done to get better statistic to find out properties of the CCDs

	cx1	= [0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90, $
		   0,10,20,30,40,50,60,70,80,90]

	cx2	= cx1+9

	cy1	= [0,0,0,0,0,0,0,0,0,0, $
		   10,10,10,10,10,10,10,10,10,10, $
		   20,20,20,20,20,20,20,20,20,20, $
		   30,30,30,30,30,30,30,30,30,30, $
		   40,40,40,40,40,40,40,40,40,40, $
		   50,50,50,50,50,50,50,50,50,50, $
		   60,60,60,60,60,60,60,60,60,60, $
		   70,70,70,70,70,70,70,70,70,70, $
		   80,80,80,80,80,80,80,80,80,80, $
		   90,90,90,90,90,90,90,90,90,90]

	cy2	= cy1+9

	FOR k=0,N_ELEMENTS(cx1)-1 DO BEGIN

		subf1[j,k,*,*]	= images[cx1[k]:cx2[k],cy1[k]:cy2[k],0,j]
		subf2[j,k,*,*]	= images[cx1[k]:cx2[k],cy1[k]:cy2[k],1,j]
		subb1[j,k,*,*]	= images[cx1[k]:cx2[k],cy1[k]:cy2[k],2,j]
		subb2[j,k,*,*]	= images[cx1[k]:cx2[k],cy1[k]:cy2[k],3,j]

	ENDFOR


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Measure some easy statistical properties ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; From 100x100 pixel box for each image

	stats(0,j,0)	= MIN(images[*,*,0,j])
	stats(1,j,0)	= MIN(images[*,*,1,j])
	stats(2,j,0)	= MIN(images[*,*,2,j])
	stats(3,j,0)	= MIN(images[*,*,3,j])
	stats(0,j,1)	= MAX(images[*,*,0,j])
	stats(1,j,1)	= MAX(images[*,*,1,j])
	stats(2,j,1)	= MAX(images[*,*,2,j])
	stats(3,j,1)	= MAX(images[*,*,3,j])
	stats(0,j,2)	= SIGCLIP_STDEV(images[*,*,0,j])
	stats(1,j,2)	= SIGCLIP_STDEV(images[*,*,1,j])
	stats(2,j,2)	= SIGCLIP_STDEV(images[*,*,2,j])
	stats(3,j,2)	= SIGCLIP_STDEV(images[*,*,3,j])
	stats(0,j,3)	= MEAN(images[*,*,0,j])
	stats(1,j,3)	= MEAN(images[*,*,1,j])
	stats(2,j,3)	= MEAN(images[*,*,2,j])
	stats(3,j,3)	= MEAN(images[*,*,3,j])
	stats(0,j,4)	= MEDIAN(images[*,*,0,j])
	stats(1,j,4)	= MEDIAN(images[*,*,1,j])
	stats(2,j,4)	= MEDIAN(images[*,*,2,j])
	stats(3,j,4)	= MEDIAN(images[*,*,3,j])

ENDFOR	;j

PRINT,' '
PRINT,' Image statistics '
PRINT,' '
PRINT,'Image','CCD','Min','Max','Stdev','Mean','Median',FORMAT='(A15,A5,5(A10))'
PRINT,names[0],'  W15',stats(0,0,0),stats(0,0,1),stats(0,0,2),stats(0,0,3),stats(0,0,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[0],'  W17',stats(0,1,0),stats(0,1,1),stats(0,1,2),stats(0,1,3),stats(0,1,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[0],'  W19',stats(0,2,0),stats(0,2,1),stats(0,2,2),stats(0,2,3),stats(0,2,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[0],'  W20',stats(0,3,0),stats(0,3,1),stats(0,3,2),stats(0,3,3),stats(0,3,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[1],'  W15',stats(1,0,0),stats(1,0,1),stats(1,0,2),stats(1,0,3),stats(1,0,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[1],'  W17',stats(1,1,0),stats(1,1,1),stats(1,1,2),stats(1,1,3),stats(1,1,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[1],'  W19',stats(1,2,0),stats(1,2,1),stats(1,2,2),stats(1,2,3),stats(1,2,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[1],'  W20',stats(1,3,0),stats(1,3,1),stats(1,3,2),stats(1,3,3),stats(1,3,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[2],'  W15',stats(2,0,0),stats(2,0,1),stats(2,0,2),stats(2,0,3),stats(2,0,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[2],'  W17',stats(2,1,0),stats(2,1,1),stats(2,1,2),stats(2,1,3),stats(2,1,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[2],'  W19',stats(2,2,0),stats(2,2,1),stats(2,2,2),stats(2,2,3),stats(2,2,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[2],'  W20',stats(2,3,0),stats(2,3,1),stats(2,3,2),stats(2,3,3),stats(2,3,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[3],'  W15',stats(3,0,0),stats(3,0,1),stats(3,0,2),stats(3,0,3),stats(3,0,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[3],'  W17',stats(3,1,0),stats(3,1,1),stats(3,1,2),stats(3,1,3),stats(3,1,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[3],'  W19',stats(3,2,0),stats(3,2,1),stats(3,2,2),stats(3,2,3),stats(3,2,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,names[3],'  W20',stats(3,3,0),stats(3,3,1),stats(3,3,2),stats(3,3,3),stats(3,3,4),FORMAT='(A15,A5,5(F10.1))'
PRINT,' '


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Check difference of bias frames, should be smaller than the stdev ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; i.e difference of MEAN values

biasdiff	= FLTARR(4)

FOR i=0,N_ELEMENTS(biasdiff)-1 DO BEGIN

	biasdiff[i]	= ABS(stats[2,i,3]-stats[3,i,3])

ENDFOR

FOR i=0,N_ELEMENTS(biasdiff)-1 DO BEGIN

	IF biasdiff[i] GT stats[2,i,2] OR biasdiff[i] GT stats[3,i,2] THEN BEGIN

	PRINT,' '
	PRINT,' Difference of averages of bias frames is larger than the standard deviation of either of the bias images.'
	PRINT,' Aborted! '
	PRINT,' ' 
	;GOTO,loppu

	ENDIF

ENDFOR 


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Calculate COUNTS, BIAS, RON and GAIN for individual areas ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

FOR k=0,3 DO BEGIN

	FOR l=0,N_ELEMENTS(cx1)-1 DO BEGIN

		scounts[0,k,l]	= MEAN(subf1[k,l,*,*])
		scounts[1,k,l]	= MEAN(subf2[k,l,*,*])
		sbias[0,k,l]	= MEAN(subb1[k,l,*,*])
		sbias[1,k,l]	= MEAN(subb2[k,l,*,*])
		deltaf[k,l,*,*]	= subf1[k,l,*,*]-subf2[k,l,*,*]
		deltab[k,l,*,*]	= subb1[k,l,*,*]-subb2[k,l,*,*]
		stdvdf[k,l]	= SIGCLIP_STDEV(deltaf[k,l,*,*])
		stdvdb[k,l]	= SIGCLIP_STDEV(deltab[k,l,*,*])
		sgain[k,l]	= ((scounts[0,k,l]+scounts[1,k,l])- $
				  (sbias[0,k,l]+sbias[1,k,l]))/ $
				  (stdvdf[k,l]^2-stdvdb[k,l]^2)
		sron[k,l]	= stdvdb[k,l]/SQRT(2.)

	ENDFOR

	cerr[k]		= SIGCLIP_STDEV(scounts[*,k,*],MEAN=temp,NREJECT=nr3)
	counts[k]	= temp
	cerr[k]		= cerr[k]/SQRT(N_ELEMENTS(cx1)-nr3)
	berr[k]		= SIGCLIP_STDEV(sbias[*,k,*],MEAN=temp,NREJECT=nr4)
	bias[k]		= temp
	berr[k]		= berr[k]/SQRT(N_ELEMENTS(cx1)-nr4)
	gerr[k]		= SIGCLIP_STDEV(sgain[k,*],MEAN=temp,NREJECT=nr1)
	gain[k]		= temp
	gerr[k]		= gerr[k]/SQRT(N_ELEMENTS(cx1)-nr1)
	rerr[k]		= SIGCLIP_STDEV(sron[k,*],MEAN=temp,NREJECT=nr2)
	ron[k]		= temp
	ron[k]		= MEAN(gain[k]*ron[k])
	rerr[k]		= gain[k]*rerr[k]/SQRT(N_ELEMENTS(cx1)-nr2)

ENDFOR


;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Print results to screen ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;

PRINT,''
PRINT,'Final results per CCD'
PRINT,''
PRINT,'CCD:','W15',FORMAT='(A6,A8)'
PRINT,'COUNTS:',counts[0], ' +/- ',cerr[0], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'BIAS:  ',bias[0],   ' +/- ',berr[0], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'GAIN:  ',gain[0],   ' +/- ',gerr[0], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,'RON:   ',ron[0],	   ' +/- ',rerr[0], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,''
PRINT,'CCD:','W17',FORMAT='(A6,A8)'
PRINT,'COUNTS:',counts[1], ' +/- ',cerr[1], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'BIAS:  ',bias[1],   ' +/- ',berr[1], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'GAIN:  ',gain[1],   ' +/- ',gerr[1], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,'RON:   ',ron[1],	   ' +/- ',rerr[1], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,''
PRINT,'CCD:','W19',FORMAT='(A6,A8)'
PRINT,'COUNTS:',counts[2], ' +/- ',cerr[2], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'BIAS:  ',bias[2],   ' +/- ',berr[2], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'GAIN:  ',gain[2],   ' +/- ',gerr[2], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,'RON:   ',ron[2],	   ' +/- ',rerr[2], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,''
PRINT,'CCD:','W20',FORMAT='(A6,A8)'
PRINT,'COUNTS:',counts[3], ' +/- ',cerr[3], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'BIAS:  ',bias[3],   ' +/- ',berr[3], FORMAT='(A9,F9.1,A5,F6.2)'
PRINT,'GAIN:  ',gain[3],   ' +/- ',gerr[3], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,'RON:   ',ron[3],	   ' +/- ',rerr[3], FORMAT='(A9,F9.4,A5,F6.4)'
PRINT,''


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; extract required keywords from the FITS header ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

date	= JULDAY(FIX(STRMID(SXPAR(hf1,'DATE'),5,2))$
                 ,FIX(STRMID(SXPAR(hf1,'DATE'),8,2))$
                 ,FIX(SXPAR(hf1,'DATE')),0,0,0)
time	= SXPAR(hf1,'UT')
;## REMOVED
;amp	= SXPAR(hf1,'AMPLM')
;## END
;## ADDED
amp	= SXPAR(hf1,'AMPLMODE')
;## END
gmode	= SXPAR(hf1,'GAINM')


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Spawn mysql command to transfer data to database ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;NOTE!!!!! In field='_' everything between '' must be on one line.
;You can NOT cut into smaller parts with $ 

;server		= 'geena.not.iac.es'
server		= 'eeva.not.iac.es'
user		= 'qc_user'
password	= 'qc_pass'
database	= 'QC'
table		= 'qc_mosca'
fields		= $
'jd,ut,amp,gmode,name_flat1,name_flat2,name_bias1,name_bias2,W15counts,W15cerr,W15bias,W15berr,W15gain,W15gerr,W15ron,W15rerr,W17counts,W17cerr,W17bias,W17berr,W17gain,W17gerr,W17ron,W17rerr,W19counts,W19cerr,W19bias,W19berr,W19gain,W19gerr,W19ron,W19rerr,W20counts,W20cerr,W20bias,W20berr,W20gain,W20gerr,W20ron,W20rerr'

;outcmd	= 'mysql -B -e ''INSERT INTO '+table+' ('+fields+') VALUES (('	$
;	+STRING(date)+'),('+STRING(time)+'),("'+amp+'"),("'+gmode       $
;       +'"),("'+names[0]+'"),("'+names[1]+'"),("'+names[2]+'"),("'+names[3]$
;	+'"),('+STRING(counts[0])+'),('+STRING(cerr[0])+'),(' $
;	+STRING(bias[0])+'),('+STRING(berr[0])+'),(' $
;	+STRING(gain[0])+'),('+STRING(gerr[0])+'),(' $
;	+STRING(ron[0])+'),('+STRING(rerr[0])+'),(' $
;	+STRING(counts[1])+'),('+STRING(cerr[1])+'),(' $
;	+STRING(bias[1])+'),('+STRING(berr[1])+'),(' $
;	+STRING(gain[1])+'),('+STRING(gerr[1])+'),(' $
;	+STRING(ron[1])+'),('+STRING(rerr[1])+'),(' $
;	+STRING(counts[2])+'),('+STRING(cerr[2])+'),(' $
;	+STRING(bias[2])+'),('+STRING(berr[2])+'),(' $
;	+STRING(gain[2])+'),('+STRING(gerr[2])+'),(' $
;	+STRING(ron[2])+'),('+STRING(rerr[2])+'),(' $
;	+STRING(counts[3])+'),('+STRING(cerr[3])+'),(' $
;	+STRING(bias[3])+'),('+STRING(berr[3])+'),(' $
;	+STRING(gain[3])+'),('+STRING(gerr[3])+'),(' $
;	+STRING(ron[3])+'),('+STRING(rerr[3])+'))'' -q -n -D '+database+ $
;	' -h '+server+' -u '+user+' -p'+password

SPAWN,outcmd,answer,error,count=cntout
IF ((error[0] EQ '') EQ 0) THEN BEGIN
	PRINT,'There was an error accessing the database:'
	PRINT,error
	;GOTO,loppu
ENDIF

loppu:

 PRINT,''
 PRINT,'Time used in seconds: ',SYSTIME(/SECONDS)-start

END

