"""Helper: copy an audio file into songs/<id>.<ext> and update data/songs.csv
Usage:
  python tools/add_song.py /path/to/source.mp3 123
This will copy to songs/123.mp3 and set the `file` column for id=123 to songs/123.mp3 (creating the column if missing).
"""
import sys
import os
import shutil
import csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SONGS_DIR = os.path.join(ROOT, 'songs')
CSV_PATH = os.path.join(ROOT, 'data', 'songs.csv')


def ensure_songs_dir():
    os.makedirs(SONGS_DIR, exist_ok=True)


def copy_file(src, id_str):
    if not os.path.isfile(src):
        raise FileNotFoundError(src)
    _, ext = os.path.splitext(src)
    ext = ext.lower()
    if ext not in ('.mp3', '.wav', '.ogg', '.m4a'):
        print('Warning: uncommon extension', ext)
    dest = os.path.join(SONGS_DIR, f"{id_str}{ext}")
    shutil.copy2(src, dest)
    return os.path.relpath(dest, ROOT).replace('\\', '/')


def update_csv(id_str, relpath):
    # Read CSV, ensure header has 'file', update row with matching id
    rows = []
    header = None
    changed = False
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames[:] if reader.fieldnames else []
        for r in reader:
            rows.append(r)

    if 'file' not in header:
        header.append('file')
        for r in rows:
            r['file'] = r.get('file', '')

    found = False
    for r in rows:
        if str(r.get('id')) == str(id_str):
            r['file'] = relpath
            found = True
            changed = True
            break
    if not found:
        # append a new row with minimal fields
        new = {k: '' for k in header}
        new['id'] = str(id_str)
        new['file'] = relpath
        rows.append(new)
        changed = True

    if changed:
        # write back safely
        backup = CSV_PATH + '.bak'
        shutil.copy2(CSV_PATH, backup)
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    return changed


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python tools/add_song.py <source-file> <id>')
        sys.exit(2)
    src = sys.argv[1]
    id_str = sys.argv[2]
    try:
        ensure_songs_dir()
        rel = copy_file(src, id_str)
        ok = update_csv(id_str, rel)
        print(f'Copied to {rel}. CSV updated: {ok}')
    except Exception as e:
        print('Error:', e)
        sys.exit(1)
