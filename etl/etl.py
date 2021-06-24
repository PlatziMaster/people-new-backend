import lxml.html as html
import requests
import os
import base64
import json
from pymongo import MongoClient
from requests.api import get

WIKI_BASE_URL = 'https://en.wikipedia.org/wiki/'

def parse_wiki_bio(artist: str) -> str:
    try:
        response = requests.get(f'{WIKI_BASE_URL}{artist.replace(" ", "_").title()}')
        if response.status_code == 200:
            famous = response.content.decode('utf-8')
            parsed = html.fromstring(famous)
            try:
                bio = str(parsed.xpath('normalize-space(//p[preceding-sibling::table[@class="infobox biography vcard"] and following-sibling::div[@class="toc"]])'))
                return bio
            except IndexError:
                return 
    except ValueError as ve:
        print(ve)


def query_artist(artist: str) -> dict:
    url = f'https://api.celebrityninjas.com/v1/search?name={artist.title()}'
    api_key = os.environ['apikey']
    headers = {'x-api-key': api_key}
    print(headers)
    resp = requests.get(url=url, headers=headers)
    if resp.status_code == 200 and resp.json() != []:
            return resp.json()[0]
    return {'message': 'The query did not return any results'}


def join_artist_with_bio(bio: str, artist: dict) -> dict:
    artist['bio'] = bio
    return artist

# Spotify API For music portion
def auth() -> str:
    client_id = os.environ['client_id_sp']
    client_secret = os.environ['client_secret_sp']
    # Check the testResponse Json for further reference
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}
    message = f'{client_id}:{client_secret}'

    # Base 64 encode
    messageBytes = message.encode('ascii')
    base64bytes = base64.b64encode(messageBytes)
    base64Message = base64bytes.decode('ascii')
    headers['Authorization'] = f'Basic {base64Message}'
    data['grant_type'] = "client_credentials"
    result = requests.post(url, headers=headers, data=data)
    token = result.json()['access_token']
    return token


BASE_SPOTIFY_URL = 'https://api.spotify.com/v1'


def set_spotify_header_request() -> dict:
    token = auth()
    return {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def get_album_details(albumId: str) -> dict:
    headers = set_spotify_header_request()
    params={'market': 'ES'}
    album = requests.get(url=f'{BASE_SPOTIFY_URL}/albums/{albumId}?market=ES', headers=headers)
    if album.status_code == 200:
        album_json = album.json()
        total_duration = 0
        response_object = {
            'Album_name': album_json['name'],
            'Total_tracks': album_json['total_tracks'],
            'Tracks_ids': []
        }
        for item in album_json['tracks']['items']:
            total_duration += item['duration_ms']
            response_object['Tracks_ids'].append({'id': item['id'], 'song_name': item['name']})

        response_object['Total_duration_in_minutes']= (total_duration/1000)//60
            
        return response_object

"""
Data structure of the response object in get_album_details
{
    'Name': 'AlbumName',
    'Total_tracks': integer,
    'Track_ids': [
        {
            'id': 'uuid from spotify',
            'song_name': 'the song name'
        },
    ],
    'Total_duration_in_minutes': float,
}
"""

def get_artist_albums_ids(artistId: str) -> list:
    headers = set_spotify_header_request()
    albums = requests.get(url=f'{BASE_SPOTIFY_URL}/artists/{artistId}/albums?include_groups=album&market=ES&limit=50&offset=0', headers=headers)
    if albums.status_code == 200:
        albums_json = albums.json()
        albums_ids = []
        for album in albums_json['items']:
            albums_ids.append(album['id'])
        return albums_ids


def get_song_features(tracklist: list) -> dict:
    valences = []
    for id, name, album_name in tracklist:
        headers = set_spotify_header_request()
        response = requests.get(url=f'{BASE_SPOTIFY_URL}/audio-features/{id}', headers=headers)
        if response.status_code == 200:
            r = response.json()
            valences.append({'id': id, 'song_name': name, 'valence': r['valence'], 'album_name': album_name})

    # Sorted takes a list of dictionaries as an argument and allows to make a new 'list' based on the key
    valences_sorted = sorted(valences, key=lambda x :x['valence'])
    return {
        'Happiest': valences_sorted[len(valences_sorted)-1],
        'Saddest': valences_sorted[0]
    }


def create_artist_and_its_albums(list_of_albums: list, artist_name:str ) -> dict:
    """
        artist = {
            'ArtistName': 'Muse',
            'Albums_and_songs': '[
                {
                    
                }
            ]'
            'Analysis': {}
        }
    """
    artist = {}
    albums_details = []
    for id in list_of_albums:
        albums_details.append(get_album_details(id))
    
    artist['Artist_name'] = artist_name
    artist['Albums_and_songs'] = albums_details
    artist['Total_albums'] = len(albums_details)

    analysis_list = []
    for item in albums_details:
        for song in item['Tracks_ids']:
            analysis_list.append((song['id'], song['song_name'], item['Album_name']))
    
    analysis = get_song_features(analysis_list)
    artist['Analysis'] = analysis

    return artist


def etl():
    client = MongoClient(f"mongodb+srv://capstoneuser:{os.environ['mongopwd']}@capstone2cluster.bri6g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client.capstoneproject2
    collection = db.songsArtists

    print('Getting albums')
    muse_albums = get_artist_albums_ids('12Chz98pHFMPJEknJQMWvI')
    coldplay_albums = get_artist_albums_ids('4gzpq5DPGxSnKTe4SA8HAU')
    madona_albums = get_artist_albums_ids('6tbjWDEIzxoDsBA1FuhfPW')
    britney_spears_albums = get_artist_albums_ids('26dSoYclwsYLMAKD3tpOr4')
    billie_eilish_albums = get_artist_albums_ids('6qqNVTkY8uBg9cP3Jd7DAH')
    breaking_benjamin_albums = get_artist_albums_ids('5BtHciL0e0zOP7prIHn3pP')
    imagine_dragons_albums = get_artist_albums_ids('53XhwfbYqKCa1cC15pYq2q')
    rise_against_albums = get_artist_albums_ids('6Wr3hh341P84m3EI8qdn9O')
    imperious_albums = get_artist_albums_ids('5iO0Y7Q3X5KQx4OkRT0LHZ')
    neck_deep_albums = get_artist_albums_ids('2TM0qnbJH4QPhGMCdPt7fH')

    print('Getting albums details and inserting into database')
    muse = create_artist_and_its_albums(muse_albums, 'Muse')
    collection.insert_one(muse)
    print('Artist inserted')

    coldplay = create_artist_and_its_albums(coldplay_albums, 'Coldplay')
    collection.insert_one(coldplay)
    print('Artist inserted')
    
    madona = create_artist_and_its_albums(madona_albums, 'Madonna')
    collection.insert_one(madona)
    print('Artist inserted')

    britney = create_artist_and_its_albums(britney_spears_albums, 'Britney Spears')
    collection.insert_one(britney)
    print('Artist inserted')

    billie = create_artist_and_its_albums(billie_eilish_albums, 'Billie Eilish')
    collection.insert_one(billie)
    print('Artist inserted')

    breaking_benjamin = create_artist_and_its_albums(breaking_benjamin_albums, 'Breaking benjamin')
    collection.insert_one(breaking_benjamin)
    print('Artist inserted')

    imagine_dragons = create_artist_and_its_albums(imagine_dragons_albums, 'Imagine dragons')
    collection.insert_one(imagine_dragons)
    print('Artist inserted')

    rise_against = create_artist_and_its_albums(rise_against_albums, 'Rise Against')
    collection.insert_one(rise_against)

    imperious = create_artist_and_its_albums(imperious_albums, 'Imperious')
    collection.insert_one(imperious)

    neck_deep = create_artist_and_its_albums(neck_deep_albums, 'Neck deep')
    collection.insert_one(neck_deep)


etl()

# artist = 'Matthew Belamy'
# bio = parse_wiki_bio(artist)
# details = query_artist(artist)
# print(join_artist_with_bio(bio, details))