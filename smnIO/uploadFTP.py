"""
This module contains functions related to FTP file transfer protocol.

:Author: Sami-Matias Niemi
:contact: smn2@mssl.ucl.ac.uk

:version: 0.1
"""
import ftplib, os, glob


def upload(ftp, file):
    """
    Upload files to a server using FTP protocol.
    """
    ext = os.path.splitext(file)[1]
    if ext in (".txt", ".htm", ".html"):
        ftp.storlines("STOR " + file, open(file))
    else:
        ftp.storbinary("STOR " + file, open(file, "rb"), 1024)


if __name__ == '__main__':
    #find files
    uploads = glob.glob('*.fits.tar.gz')
    uploads.sort()

    #open connection
    ftp = ftplib.FTP('ftpix.iap.fr')
    ftp.login('VISSIM','!!!VISsim')

    #get existing files, note however, that this does
    #not check the file size, so files that were
    #uploaded only partially will not be uploaded
    #again.
    existing = ftp.retrlines('LIST')

    #upload not existing files
    i = 0
    for file in uploads:
        if not file in existing:
            print 'Uploading %s' % file
            upload(ftp, file)
            i += 1

    print '%i files were uploaded...' %i