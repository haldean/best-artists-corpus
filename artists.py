'''
Reads relevant artist data and writes it to disk.

This (a) saves time and (b) saves Wikipedia and (c) keeps last.fm from getting
mad at me.
'''

import BeautifulSoup as bs
import os
import re
import requests
import sys
import urllib

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

ARTIST_FILE = 'top-artists.txt'
PAGE_DIRECTORY = 'artists'
WIKI_LINK = re.compile('^http[s]?://en\.wikipedia\.org')
HEADERS = {
    'User-agent': 'bayespop (bayespop@haldean.org)',
    }

def top_n_artists(n):
  url = (
      'http://ws.audioscrobbler.com/2.0/'
      '?method=chart.gettopartists&format=json'
      '&api_key=a75e76ff295edd4bad99b84951f03d14'
      '&limit=%d' % n)
  resp = requests.get(url, headers=HEADERS)
  with open(ARTIST_FILE, 'w') as f:
    for artist in (a['name'] for a in resp.json['artists']['artist']):
      f.write(('%s\n' % artist).encode('utf-8'))
  print('Write %d top artists to %s' % (n, ARTIST_FILE))

def find_artist_url(artist_name):
  normalized = urllib.quote(artist_name, '')
  url = 'http://www.musicbrainz.org/ws/2/artist/?query=artist:"%s"&limit=10' % normalized
  print('  Searching MusicBrainz at URL %s' % url)
  resp = requests.get(url, headers=HEADERS)
  tree = ET.fromstring(resp.text.encode('utf-8'))[0]

  artist_node = tree[0]
  # prefer exact matches
  for node in tree:
    if node[0].text == artist_name:
      artist_node = node
      continue

  mb_id = artist_node.attrib['id']
  print('  Found MusicBrainz ID %s' % mb_id)

  the_ugly = requests.get(
      'http://musicbrainz.org/artist/%s' % mb_id, headers=HEADERS)
  for link in bs.BeautifulSoup(the_ugly.text, parseOnlyThese=bs.SoupStrainer('a')):
    if link.has_key('href') and WIKI_LINK.match(link['href']):
      if 'discography' not in link['href']:
        return link['href']
  raise Exception(
      'MusicBrainz does not have a wikipedia page for %s' % artist_name)

def wikipedia_title_from_url(url):
  return url.split('/')[-1]

def get_artist_page(artist_name, allow_band_append=True):
  print('Get page for %s' % artist_name)
  url = find_artist_url(artist_name)

  title = wikipedia_title_from_url(url)
  print('  Found Wikipedia page %s' % title)
  
  url = (
      'http://en.wikipedia.org/w/api.php?'
      'action=query&format=json&redirects&export'
      '&titles=%s' % title)
  resp = requests.get(url, headers=HEADERS)
  return resp.json['query']['export']['*']

def artist_page_path(artist_name):
  return os.path.abspath(
      os.path.join(
        os.path.dirname(sys.argv[0]),
        PAGE_DIRECTORY,
        artist_name.replace(' ', '_'))) + '.html'

def cache_all_artists():
  with open(ARTIST_FILE, 'r') as f:
    for line in f:
      artist = line.decode('utf-8').strip()
      path = artist_page_path(artist)
      if os.path.exists(path):
        continue

      page_contents = get_artist_page(artist)
      with open(path, 'w') as artist_f:
        artist_f.write(page_contents.encode('utf-8'))
        print('  Wrote cache file %s' % path)

def main():
  if len(sys.argv) < 2:
    print('Must supply either "top n" or "cache"')
    return

  if sys.argv[1] == 'top':
    if len(sys.argv) != 3:
      print('Must supply number of artists (max 1000) to download.')
      return
    top_n_artists(int(sys.argv[2]))

  elif sys.argv[1] == 'cache':
    cache_all_artists()

if __name__ == '__main__':
  main()
