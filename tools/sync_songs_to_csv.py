"""Scan songs/ and update data/songs.csv `file` column for matching tracks.
Matching rules (attempted in order):
 - id-based: songs/<id>.<ext>
 - slugified title: songs/<slug>.<ext> (lowercase, non-alnum -> underscore)
 - exact filename: songs/<title>.<ext>

Usage:
  python tools/sync_songs_to_csv.py

This will create a backup 'data/songs.csv.bak' before writing changes.
"""

import os
import csv
import shutil
import sys
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(ROOT, 'data', 'songs.csv')
SONGS_DIR = os.path.join(ROOT, 'songs')

EXTS = ['.mp3', '.wav', '.ogg', '.m4a']


def slugify(s):
    if not s:
        return ''
    # lower, replace non-alnum with underscore, collapse underscores
    s = s.lower()
    s = re.sub(r'[^a-z0-9]', '_', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


def scan_songs_dir():
    files = {}
    if not os.path.isdir(SONGS_DIR):
        return files
    for f in os.listdir(SONGS_DIR):
        lower = f.lower()
        for ext in EXTS:
            if lower.endswith(ext):
                files[f] = True
                break
    return files


def read_csv():
    if not os.path.isfile(CSV_PATH):
        print('CSV not found at', CSV_PATH)
        sys.exit(1)
    with open(CSV_PATH, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        header = reader.fieldnames[:] if reader.fieldnames else []
    return header, rows


def write_csv(header, rows):
    bak = CSV_PATH + '.bak'
    shutil.copy2(CSV_PATH, bak)
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print('Wrote CSV and saved backup to', bak)


def find_match_for_row(row, available_files):
    # if row already has a file and it exists, leave it
    filecol = row.get('file')
    if filecol:
        # normalize path
        candidate = filecol.replace('\\', '/').strip()
        if candidate and os.path.isfile(os.path.join(ROOT, candidate)):
            return candidate
    # try id-based
    sid = str(row.get('id') or '').strip()
    if sid:
        for ext in EXTS:
            name = sid + ext
            if name in available_files:
                return os.path.join('songs', name).replace('\\', '/')
    # try slugified title
    title = row.get('title') or row.get('song') or ''
    slug = slugify(title)
    if slug:
        for ext in EXTS:
            cand = slug + ext
            if cand in available_files:
                return os.path.join('songs', cand).replace('\\', '/')
    # try exact filename
    title_clean = title.strip()
    if title_clean:
        for ext in EXTS:
            cand = title_clean + ext
            if cand in available_files:
                return os.path.join('songs', cand).replace('\\', '/')
    # fuzzy: check if all title tokens appear in filename (loose match)
    title_tokens = [t for t in re.findall(r"[a-z0-9]+", (title or '').lower())]
    if title_tokens:
        for fname in available_files:
            lower = fname.lower()
            matched = True
            for tk in title_tokens:
                if tk not in lower:
                    matched = False
                    break
            if matched:
                return os.path.join('songs', fname).replace('\\', '/')
    return ''


def main():
    print('Scanning songs directory...')
    available = scan_songs_dir()
    if not available:
        print('No audio files found in', SONGS_DIR)
    else:
        print('Found', len(available), 'audio files')

    header, rows = read_csv()
    if 'file' not in (header or []):
        header.append('file')
        for r in rows:
            r['file'] = r.get('file', '')

    changed = False
    for r in rows:
        match = find_match_for_row(r, available)
        if match and (r.get('file') or '').strip() != match:
            print('Setting file for id', r.get('id'), '->', match)
            r['file'] = match
            changed = True

    if changed:
        write_csv(header, rows)
    else:
        print('No changes needed; CSV already up-to-date')


if __name__ == '__main__':
    main()
