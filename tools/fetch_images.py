#!/usr/bin/env python3
"""
Fetch artist and album images from Wikipedia / Wikimedia Commons.

Usage:
    python tools/fetch_images.py

This script will:
- Read `data/songs.csv` to collect unique artists and song titles.
- For each artist and album, try to fetch a thumbnail via the Wikipedia REST summary API.
- If that fails, try a Wikimedia Commons search for a bitmap file matching the name.
- Save images to `images/artists/{slug}.{ext}` and `images/albums/{slug}.{ext}`.

Notes:
- This script uses only the Python standard library (urllib) so no extra dependencies.
- Many images are copyrighted. The script fetches images programmatically for local testing only.
"""
import os
import csv
import json
import urllib.parse
import urllib.request
import time

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CSV_PATH = os.path.join(ROOT, 'data', 'songs.csv')
OUT_ARTISTS = os.path.join(ROOT, 'images', 'artists')
OUT_ALBUMS = os.path.join(ROOT, 'images', 'albums')

USER_AGENT = 'MoodifyImageFetcher/1.0 (https://example.com)'

os.makedirs(OUT_ARTISTS, exist_ok=True)
os.makedirs(OUT_ALBUMS, exist_ok=True)


def slugify(text):
    s = (text or '').lower()
    s = s.replace('&', 'and')
    s = ''.join(ch if (ch.isalnum() or ch.isspace() or ch == '-') else '' for ch in s)
    s = '-'.join(s.split())
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-') or 'unknown'


def read_songs():
    artists = []
    albums = []
    if not os.path.exists(CSV_PATH):
        print('No songs.csv found at', CSV_PATH)
        return artists, albums
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            artist = (r.get('artist') or '').strip()
            title = (r.get('title') or r.get('song') or '').strip()
            if artist:
                artists.append(artist)
            if title:
                albums.append(title)
    # unique preserve order
    def unique(seq):
        seen = set(); out = []
        for x in seq:
            if x not in seen:
                seen.add(x); out.append(x)
        return out
    return unique(artists), unique(albums)


def http_get_json(url, params=None, headers=None, timeout=10):
    if params:
        if '?' in url:
            url = url + '&' + urllib.parse.urlencode(params)
        else:
            url = url + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header('User-Agent', USER_AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def download_url(url, out_path):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
            with open(out_path, 'wb') as f:
                f.write(data)
        return True
    except Exception as e:
        print('Download failed for', url, '->', e)
        return False


def try_wikipedia_thumbnail(name):
    # Use Wikipedia REST summary to get a thumbnail if available
    # Example: https://en.wikipedia.org/api/rest_v1/page/summary/A.R._Rahman
    title = name.replace(' ', '_')
    url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}'
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            thumb = data.get('thumbnail') or data.get('originalimage')
            if thumb and thumb.get('source'):
                return thumb.get('source')
    except Exception:
        return None
    return None


def try_commons_search(name):
    # Use Wikimedia Commons API generator=search to find a file and return imageinfo url
    api = 'https://commons.wikimedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': f'{name} filetype:bitmap',
        'gsrlimit': '3',
        'prop': 'imageinfo',
        'iiprop': 'url'
    }
    try:
        data = http_get_json(api, params=params, headers={'User-Agent': USER_AGENT})
        q = data.get('query') or {}
        pages = q.get('pages') or {}
        # pick first imageinfo url
        for pid, info in pages.items():
            ii = info.get('imageinfo')
            if ii and isinstance(ii, list) and ii[0].get('url'):
                return ii[0].get('url')
    except Exception:
        return None
    return None


def fetch_and_save(name, out_dir, kind='artist'):
    slug = slugify(name)
    # try wikipedia
    print(f'[*] Resolving image for {kind}:', name)
    url = try_wikipedia_thumbnail(name)
    if url:
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or '.jpg'
        out_path = os.path.join(out_dir, slug + ext)
        if os.path.exists(out_path):
            print('  exists, skipping:', out_path)
            return out_path
        print('  downloading from wikipedia:', url)
        if download_url(url, out_path):
            return out_path
    # fallback to commons search
    url = try_commons_search(name)
    if url:
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or '.jpg'
        out_path = os.path.join(out_dir, slug + ext)
        if os.path.exists(out_path):
            print('  exists, skipping:', out_path)
            return out_path
        print('  downloading from commons:', url)
        if download_url(url, out_path):
            return out_path
    print('  no image found for', name)
    return None


def main():
    artists, albums = read_songs()
    print('Found', len(artists), 'unique artists and', len(albums), 'unique titles')
    # Limit to reasonable number
    artists = artists[:24]
    albums = albums[:24]

    for a in artists:
        try:
            fetch_and_save(a, OUT_ARTISTS, kind='artist')
            time.sleep(0.5)
        except Exception as e:
            print('Error fetching artist', a, e)

    for al in albums:
        try:
            fetch_and_save(al, OUT_ALBUMS, kind='album')
            time.sleep(0.5)
        except Exception as e:
            print('Error fetching album', al, e)

    print('Done. Images saved into:', OUT_ARTISTS, OUT_ALBUMS)

if __name__ == '__main__':
    main()
