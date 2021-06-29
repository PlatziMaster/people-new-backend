import lxml.html as html
import requests
import os
import base64
import json
import re
from pymongo import MongoClient
from requests.api import get
import uuid

WIKI_BASE_URL = 'https://en.wikipedia.org/wiki/'

def parse_wiki_bio(artist: str) -> str:
    try:
        response = requests.get(f'{WIKI_BASE_URL}{artist.replace(" ", "_").title()}')
        if response.status_code == 200:
            famous = response.content.decode('utf-8')
            parsed = html.fromstring(famous)
            try:
                bio = parsed.xpath('normalize-space(//p[preceding-sibling::table[@class="infobox biography vcard"] and following-sibling::div[@class="toc"]])')
                replaced_bio = re.sub(r'\[.*?\]', '', bio)
                return replaced_bio
            except IndexError:
                return 
    except ValueError as ve:
        print(ve)


def query_artist(artist: str) -> dict:
    url = f'https://api.celebrityninjas.com/v1/search?name={artist}&limit=1'
    api_key = os.environ['apikey']
    headers = {'x-api-key': api_key}
    resp = requests.get(url=url, headers=headers)
    if resp.status_code == 200 and resp.json() != []:
            return resp.json()[0]
    return {'message': 'The query did not return any results'}


def join_artist_with_bio(bio: str, celebrity: dict) -> dict:
    celebrity['bio'] = bio
    return celebrity


# Spotify API For music portion
def spotify_auth() -> str:
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
    token = spotify_auth()
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
        uid = str(uuid.uuid4())
        response_object['Id'] = uid      
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


def check_artist_health(artist_with_bio: dict, mongo_collection) -> None:
    if 'message' in artist_with_bio.keys():
        return
    mongo_collection.insert_one(artist_with_bio)
    print('Celebrity inserted')


def etl():
    client = MongoClient(f"mongodb+srv://capstoneuser:{os.environ['mongopwd']}@capstone2cluster.bri6g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client.capstoneproject2
    collection = db.songsArtists

    print('Getting albums')
    # Dropping collection before inserting
    collection.drop()

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

    collection = db.songsArtists

    print('Doing analysis and inserting into database')
    muse = create_artist_and_its_albums(muse_albums, 'Muse')
    muse['Image'] = f'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/MuseBristol_050619-118_%2848035812973%29.jpg/1920px-MuseBristol_050619-118_%2848035812973%29.jpg'
    collection.insert_one(muse)
    print('Artist inserted')

    coldplay = create_artist_and_its_albums(coldplay_albums, 'Coldplay')
    coldplay['Image'] = f'https://i1.wp.com/www.sopitas.com/wp-content/uploads/2020/06/coldplay-canciones-xy.jpg'
    collection.insert_one(coldplay)
    print('Artist inserted')
    
    madona = create_artist_and_its_albums(madona_albums, 'Madonna')
    madona['Image'] = f'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSFBMAqWvZYgc1GdzhdUsduoU3_lqBkll6EPGCHWoacG25zxE90'
    collection.insert_one(madona)
    print('Artist inserted')

    britney = create_artist_and_its_albums(britney_spears_albums, 'Britney Spears')
    britney['Image'] = f'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSdFQDe5hctJraHtbNlCqzsoaRYxsnCkpFeTFvFrOKGVkUcDuYr'
    collection.insert_one(britney)
    print('Artist inserted')

    billie = create_artist_and_its_albums(billie_eilish_albums, 'Billie Eilish')
    billie['Image'] = f'https://static.dw.com/image/52315108_303.jpg'
    collection.insert_one(billie)
    print('Artist inserted')

    breaking_benjamin = create_artist_and_its_albums(breaking_benjamin_albums, 'Breaking benjamin')
    breaking_benjamin['Image'] = f'https://summainferno.com/wp-content/uploads/2019/10/Breaking-Benjamin.jpg'
    collection.insert_one(breaking_benjamin)
    print('Artist inserted')

    imagine_dragons = create_artist_and_its_albums(imagine_dragons_albums, 'Imagine dragons')
    imagine_dragons['Image'] = f'https://www.eluniversal.com.mx/sites/default/files/2019/12/19/imagine_dragons.jpg'
    collection.insert_one(imagine_dragons)
    print('Artist inserted')

    rise_against = create_artist_and_its_albums(rise_against_albums, 'Rise Against')
    rise_against['Image'] = f'https://s3.us-west-2.amazonaws.com/static.ernieball.com/website/images/striking_a_chord/image/full/20.jpg?1594908911'
    collection.insert_one(rise_against)
    print('Artist inserted')

    imperious = create_artist_and_its_albums(imperious_albums, 'Imperious')
    imperious['Image'] = f'https://scontent.fgdl3-1.fna.fbcdn.net/v/t1.6435-9/123771543_1075122889596604_8994035093060246774_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=e3f864&_nc_eui2=AeH03PFeUvU99iqJkQUEZB-C3v-TNw6UHEve_5M3DpQcS8UMGiHbxwO0z-3bjjA9jgM&_nc_ohc=Q9q6lqpN0ikAX--Dnct&_nc_ht=scontent.fgdl3-1.fna&oh=d5b1c0e1efd34362fac92a6aa57699bd&oe=60DEF9D2' 
    collection.insert_one(imperious)
    print('Artist inserted')

    neck_deep = create_artist_and_its_albums(neck_deep_albums, 'Neck deep')
    neck_deep['Image'] = f'https://www.rockzonemag.com/wp-content/uploads/2020/08/NeckDeep_foto-2020_Gullick_Y1A9386.gif'
    collection.insert_one(neck_deep)
    print('Artist inserted')
    print('Finished inserting music artists')

    # Changing collection
    print('Inserting celebrities')
    collection = db.celebrities
    collection.drop()
    collection = db.celebrities
    
    elon = query_artist('elon musk')
    elon_bio = parse_wiki_bio('elon musk')
    joined_elon = join_artist_with_bio(elon_bio, elon)
    joined_elon['Image'] = f'https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.wikipedia.org%2Fwiki%2FElon_Musk&psig=AOvVaw2yJpsErA5USc0r1yadUR9Z&ust=1625017631327000&source=images&cd=vfe&ved=0CAoQjRxqFwoTCNCviMfcu_ECFQAAAAAdAAAAABAD'
    check_artist_health(joined_elon, collection)


    mark_z = query_artist('Mark Zuckerberg')
    mark_z_bio = parse_wiki_bio('Mark Zuckerberg')
    joined_mark = join_artist_with_bio(mark_z_bio, mark_z)
    joined_mark['Image'] = f'https://about.fb.com/es/wp-content/uploads/sites/13/2019/01/mz.jpg?fit=3241%2C2160'
    check_artist_health(joined_mark, collection)

    mark_hamill = query_artist('Mark hamill')
    mark_h_bio = parse_wiki_bio('Mark hamill')
    joined_mark_h = join_artist_with_bio(mark_h_bio, mark_hamill)
    joined_mark_h['Image'] = f'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcT0W1rBFC1zAjS3amBGX6C3diI8zBZOeVW9oIphVXmIM4anleEO'
    check_artist_health(joined_mark_h, collection)

    halle_berry = query_artist('Halle Berry')
    halle_b_bio = parse_wiki_bio('Halle berry')
    joined_halle_b = join_artist_with_bio(halle_b_bio, halle_berry)
    joined_halle_b['Image'] = f'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Halle_Berry_by_Gage_Skidmore_2.jpg/1200px-Halle_Berry_by_Gage_Skidmore_2.jpg'
    check_artist_health(joined_halle_b, collection)

    shakira = query_artist('Shakira')
    shakira_bio = parse_wiki_bio('Shakira')
    joined_shakira = join_artist_with_bio(shakira_bio, shakira)
    joined_shakira['Image'] = f'https://e00-elmundo.uecdn.es/assets/multimedia/imagenes/2021/01/13/16105465107404.jpg'
    check_artist_health(joined_shakira, collection)

    henry = query_artist('Henry Cavill')
    henry_bio = parse_wiki_bio('Henry cavill')
    joined_henry = join_artist_with_bio(henry_bio, henry)
    joined_henry['Image'] = f'https://upload.wikimedia.org/wikipedia/commons/d/dd/Henry_Cavill_by_Gage_Skidmore_2.jpg'
    check_artist_health(joined_henry, collection)

    sofia = query_artist('Sofia Vergara')
    sofia_bio = parse_wiki_bio('Sofia Vergara')
    joined_sofia = join_artist_with_bio(sofia_bio, sofia)
    joined_sofia['Image'] = f'https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.wikipedia.org%2Fwiki%2FSof%25C3%25ADa_Vergara&psig=AOvVaw1blti4619q-meR-otUB9Ty&ust=1625018129776000&source=images&cd=vfe&ved=0CAoQjRxqFwoTCIDp5Lbeu_ECFQAAAAAdAAAAABAD'
    check_artist_health(joined_sofia, collection)

    bill = query_artist('Bill gates')
    bill_bio = parse_wiki_bio('Bill gates')
    joined_bill = join_artist_with_bio(bill_bio, bill)
    joined_bill['Image'] = f'https://upload.wikimedia.org/wikipedia/commons/a/a8/Bill_Gates_2017_%28cropped%29.jpg'
    check_artist_health(joined_bill, collection)

    tom = query_artist('tom holland')
    tom_bio = parse_wiki_bio('Tom Holland')
    joined_tom = join_artist_with_bio(tom_bio, tom)
    joined_tom['Image'] = f'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tom_Holland_by_Gage_Skidmore.jpg/1200px-Tom_Holland_by_Gage_Skidmore.jpg'
    check_artist_health(joined_tom, collection)

    robert = query_artist('Robert Downey Jr')
    robertjr_bio = parse_wiki_bio('Robert Downey Jr.')
    joined_robert = join_artist_with_bio(robertjr_bio, robert)
    joined_robert['Image'] = f'https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/robert-downey-jr-iron-man-casting-1563435293.jpg'
    check_artist_health(joined_robert, collection)

etl()
