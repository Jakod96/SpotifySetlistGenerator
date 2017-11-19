import requests
import json
import spotipy
import spotipy.util as util
#Header for setlist
#Enter your Setlist.fm API key below
header = {'x-api-key': '', 'accept': 'application/json'}
#Header for Spotify
#Enter your spotify username
username = ""
token = util.prompt_for_user_token(
    username,
    scope = 'playlist-modify-private playlist-modify-public',
    #Enter Spotify API ID
    client_id='',
    #Enter Spotify API Secret
    client_secret='',
    #Enter Spotify API Redirect URI
    redirect_uri='http://localhost/'
)



#Create a session token for spotipy
def createSpotifyToken(token):
    try:
        spotify = spotipy.Spotify(auth=token)
    except:
        return "Failed to create spotipy session"
    return spotify

#Get the MusicBrainz ID for the artist
def getArtistID(header):
    artistToFind = raw_input("Please Enter artist name: ")
    #Replace any spaces with %20.
    #TODO : Add correct encoding so it can also manage non ANSI signs
    artist = artistToFind.replace(" ", "%20")
    url = "https://api.setlist.fm/rest/1.0/search/artists?artistName=" + artist + "&p=1&sort=relevance"
    myResponse = requests.get(url, headers=header, verify=True)
    jData = json.loads(myResponse.content)
    for key in jData['artist']:
        return key['mbid']

#Get a setlist
def getSetlist(artistID, header):
    url = "https://api.setlist.fm/rest/1.0/artist/" + artistID + "/setlists"
    myResponse = requests.get(url, headers=header, verify=True)
    jDataSetSetList = json.loads(myResponse.content)
    #TODO : Add method to select more than latest setlist
    if(myResponse.ok):
        for key in jDataSetSetList['setlist']:
            #Get the first setlist that contains more than 0 songs
            #This is to avoid events that don't have a populated setlist
            if len(key.get('sets').get('set')) > 0:
                return key
    else:
        #TODO: Add some real error handling
        return myResponse

#Define what the playlist will be named
def playlistName(Setlist):
    PlaylistName = Setlist['artist']['name'] + \
                   " - " + \
                   Setlist['venue']['city']['name'] + \
                   ' - ' + \
                   Setlist['venue']['name'] + \
                   ' - ' +\
                   Setlist['eventDate']

    return PlaylistName

#Convert the setlist into names that can be used to search in spotify
def trimSetlist(Setlist):
    fSetList = []
    for key in Setlist.get('sets').get('set'):
        for key in key.get('song'):
            fSetList.append(key['name'])
    return fSetList

#Create the playlist
def createPlaylist(PlaylistName, SpotifySession):
    userName = SpotifySession.me()['id']
    currentUserPlaylists = SpotifySession.user_playlists(user=userName)
    for playList in currentUserPlaylists['items']:
        #Check if there is a playlist named the same already
        if playList['name'] == PlaylistName:
            return
    #TODO : Error handling?
    SpotifySession.user_playlist_create(user=userName, public=True, name=PlaylistName)
    return

#Return the playlist ID of the created playlist
def getSpotifyPlaylistID(PlaylistName, SpotifySession):
    userName = SpotifySession.me()['id']
    currentUserPlaylists = SpotifySession.user_playlists(user=userName)
    for playList in currentUserPlaylists['items']:
        #Filter through all playlists until we find one that matches
        if playList['name'] == PlaylistName:
            return playList['id']
    #This should never happen if createPlaylist was ran before and was successful
    return "Failed to find correct playlist"

#Populate the playlist with the setlist songs
def populatePlaylist(spotifyPlaylistID, SpotifySession, TrimmedTracklist):
    userName = SpotifySession.me()['id']
    spotifyTracklist = []
    #TODO: Add better method than searching for one song at the time if Possible. Current method is slow
    for song in TrimmedTracklist:
        spotifyTracklist.append(spotifySession.search(q='track:' + song))
    trackURIs = []
    for track in spotifyTracklist:
        trackURIs.append(track['tracks']['items'][0]['id'])
    #TODO: Error handling?
    spotifySession.user_playlist_add_tracks(user=userName, playlist_id=spotifyPlaylistID, tracks=trackURIs)



#Workflow for creation of playlist and population of playlist
spotifySession = createSpotifyToken(token)
ArtistID = getArtistID( header=header)
setList = getSetlist(artistID=ArtistID, header=header)
Tracklist = trimSetlist(setList)
PlayListName = playlistName(Setlist=setList)
createPlaylist(PlaylistName=PlayListName, SpotifySession=spotifySession)
spotifyPlaylistID = getSpotifyPlaylistID(PlaylistName=PlayListName, SpotifySession=spotifySession)
populatePlaylist(spotifyPlaylistID=spotifyPlaylistID, SpotifySession=spotifySession, TrimmedTracklist=Tracklist)