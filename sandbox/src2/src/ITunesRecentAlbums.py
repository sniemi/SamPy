#!/usr/bin/env python
# encoding: utf-8
import sys
import getopt
from appscript import *

help_message = '''
Use this script to create a new playlist in iTunes. 
It reads one playlist, orders tracks by album, then by track # or name.

Parameters (default values):
-v: Verbose output.
-h --help: This help message.
-m --maxAlbums: Maximum number of albums to process. 0 for all. (0)
-s --songsPerAlbum: Number of songs required to define an album. (5)
-p --playlist: Source playlist. ("Recently Added")
-n --newplaylist: Destination playlist. ("Sorted Recently Added")

This is useful when using with a source playlist sorted by date added. 
Essentially you will be sorting by date, album, track.

This does require appscript. If you do not have it, install it with this command:
sudo easy_install appscript
'''

iTunes = app('iTunes.app')
maxAlbums = 0
songsPerAlbum = 5
playlist = "Recently Added"
newPlaylist = "Sorted Recently Added"
verbose = False

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option == "--maxAlbums":
                maxAlbums = value
            if option in ("-s","--songsPerAlbum"):
                songsPerAlbum = value
            if option in ("-p", "--playlist"):
                playlist = value
            if option in ("-n", "--newplaylist"):
                newPlaylist = value
        
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2

def getItunesData(iTunes, playlist, verbose):
    #get songs in recently added playlist
    if iTunes.isrunning:
        #iTunes is running, begin grabbing data
        playlists = iTunes.user_playlists
        if not iTunes.exists(playlists[playlist]):
            #playlist doesn't exist
            print("The playlist you specified, '" + playlist + "', doesn't seem to exist.\nPlease check that it does, and that it is sorted by date.")
        else:
            #we have the playlist, select it
            currentPlaylist = playlists[playlist]
            #get albums 
            allTracks = currentPlaylist.tracks()
        return allTracks

def sortSongs(allTracks, songsPerAlbum, maxAlbums, verbose):
    songData = {}
    songNames = {}
    songCount = {}
    albumOrder = []
    for track in allTracks:
        albumTitle = track.album()
        if albumTitle != '':
            #album title isn't blank
            if albumTitle not in songData.keys():
                #make multi-dimensional dictionary for data
                songData[albumTitle] = {}
                albumOrder.append(albumTitle)
                songNames[albumTitle] = {}
                songCount[albumTitle] = 1
            else:
                songCount[albumTitle] += 1
            trackNumber = track.track_number()
            if trackNumber in songData[albumTitle]: #== 0:
                #if there aren't track numbers, sort by track names
                trackNumber = track.name()
            songData[albumTitle][trackNumber] = track
            songNames[albumTitle][trackNumber] = track.name()
    
    #remove albums
    toDelete = []
    for album in songData.keys():
        if songCount[album] < songsPerAlbum:
            #remove album from list if it doesn't have enough songs
            toDelete.append(album)
    omittedSongs = "Albums omitted (for having too few songs): "
    for album in toDelete:
        omittedSongs += "\nTracks:" + str(songCount[album]) + " - " + album
        omittedSongs += str(songNames[album])
        del songData[album]
        albumOrder.remove(album)
    if verbose:
        #for debug and such
        print omittedSongs
        
    if len(songData.keys()) <= maxAlbums or maxAlbums == 0:
        #show all albums
        length = len(songData.keys())
    else:
        #show only maxAlbums # albums
        length = maxAlbums
    
    sortedSongs = []
    for i in range(length):
        tracks = songData[albumOrder[i]].keys()
        tracks.sort()
        for track in tracks:
            sortedSongs.append(songData[albumOrder[i]][track])
    return sortedSongs
    
def makePlaylist(iTunes, songs, name, oldPlaylist, verbose):
    #make new playlist, or use existing, and insert songs
    playlists = iTunes.user_playlists
    if iTunes.exists(playlists[name]):
        #playlist exists, empty it and fill with new tracks
        playlistTracks = playlists[name].tracks()
        if len(playlistTracks) > 0:
            iTunes.delete(playlists[name].tracks)
    else:
        location = playlists[oldPlaylist].parent()
        iTunes.make(new=k.playlist, at=location, with_properties={k.name: name})
    
    playlist = playlists[name]
    tracks = []
    
    for track in songs:
        iTunes.duplicate(track, to=playlist)
    return True

#actually run stuff
allTracks = getItunesData(iTunes, playlist, verbose)
sortedSongs = sortSongs(allTracks, songsPerAlbum, maxAlbums, verbose)
finished = makePlaylist(iTunes, sortedSongs, newPlaylist, playlist, verbose)
if finished:
    print "Success!"
#iTunes.reveal(currentPlaylist)
if __name__ == "__main__":
    sys.exit(main())