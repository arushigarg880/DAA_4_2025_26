#!/usr/bin/env python3
"""
Lightweight backend using Python standard library.
- Serves static files from project root
- GET /api/songs -> returns JSON list parsed from data/songs.csv
- POST /api/generate -> accepts JSON {"mood": "happy", "limit": 10} and returns filtered list

Run: python backend.py
"""
import http.server
import socketserver
import json
import csv
import urllib
import os
from http import HTTPStatus
import subprocess
import shlex

PORT = 8000
ROOT = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT, 'data', 'songs.csv')

class Handler(http.server.SimpleHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/songs'):
            self.handle_api_songs()
            return
        # otherwise serve static files
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith('/api/generate'):
            self.handle_api_generate()
            return
        # fallback
        self.send_response(HTTPStatus.NOT_FOUND)
        self._set_cors_headers()
        self.end_headers()

    def handle_api_songs(self):
        songs = []
        try:
            with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # convert numeric fields
                    for key in ['id', 'tempo', 'popularity']:
                        if key in row and row[key].isdigit():
                            row[key] = int(row[key])
                    songs.append(row)
            # Attempt to auto-detect local audio files (relative "songs/" folder)
            songs_dir = os.path.join(ROOT, 'songs')
            available_files = []
            if os.path.isdir(songs_dir):
                for fname in os.listdir(songs_dir):
                    lower = fname.lower()
                    if lower.endswith('.mp3') or lower.endswith('.wav') or lower.endswith('.ogg'):
                        available_files.append(fname)

            def slugify(s):
                return ''.join(c if c.isalnum() else '_' for c in s.lower()).strip('_')

            for s in songs:
                # if CSV already contains a file column, keep it
                if s.get('file'):
                    continue
                found = None
                # try id.mp3
                try:
                    sid = str(s.get('id'))
                    candidate = sid + '.mp3'
                    if candidate in available_files:
                        found = os.path.join('songs', candidate).replace('\\', '/')
                except Exception:
                    pass
                if not found:
                    # try title-based slug
                    title = s.get('title') or s.get('song') or ''
                    slug = slugify(title)
                    for ext in ('.mp3', '.wav', '.ogg'):
                        c = slug + ext
                        if c in available_files:
                            found = os.path.join('songs', c).replace('\\', '/')
                            break
                if not found:
                    # try raw title file name (spaces preserved) fallback
                    title = s.get('title') or s.get('song') or ''
                    for ext in ('.mp3', '.wav', '.ogg'):
                        c = (title + ext)
                        if c in available_files:
                            found = os.path.join('songs', c).replace('\\', '/')
                            break
                if found:
                    s['file'] = found
            payload = songs
            self.send_response(HTTPStatus.OK)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        except Exception as e:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

    def handle_api_generate(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length) if length > 0 else b''
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            data = {}
        mood = data.get('mood')
        genre = data.get('genre')
        limit = int(data.get('limit', 10))

        # First try to call external C++ binary `moodify.exe` if present.
        # Expected behavior (best-effort): moodify.exe --mood <mood> --limit <n>
        # and print JSON array to stdout. If it fails, fallback to CSV filtering.
        result = None
        exe_path = os.path.join(ROOT, 'moodify.exe')
        if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
            try:
                args = [exe_path]
                if mood:
                    args += ['--mood', str(mood)]
                if genre:
                    args += ['--genre', str(genre)]
                args += ['--limit', str(limit)]
                # Run binary and capture stdout
                proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT, timeout=15)
                if proc.returncode == 0 and proc.stdout:
                    try:
                        parsed = json.loads(proc.stdout)
                        result = parsed
                    except Exception:
                        # not JSON; try to parse as CSV-like (lines: id,title,artist,...)
                        lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
                        parsed = []
                        for ln in lines:
                            # attempt to split by comma and map to CSV headers if possible
                            parts = [p.strip() for p in ln.split(',')]
                            if len(parts) >= 3:
                                row = {'title': parts[1], 'artist': parts[2]}
                                parsed.append(row)
                        if parsed:
                            result = parsed
                else:
                    # binary error — log stderr; we'll fallback
                    print('moodify.exe failed:', proc.returncode, proc.stderr)
            except Exception as e:
                print('Failed to run moodify.exe:', e)

        if result is None:
            # Fallback: use CSV file and simple filtering
            songs = []
            try:
                with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        for key in ['id', 'tempo', 'popularity']:
                            if key in row and row[key].isdigit():
                                row[key] = int(row[key])
                        # keep relative file path if present
                        songs.append(row)
            except Exception as e:
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return

            filtered = songs
            if mood:
                filtered = [s for s in filtered if s.get('mood', '').lower() == mood.lower()]
            if genre:
                filtered = [s for s in filtered if s.get('genre', '').lower() == genre.lower()]

            filtered.sort(key=lambda s: int(s.get('popularity', 0)) if s.get('popularity') is not None else 0, reverse=True)
            result = filtered[:limit]

        # Ensure result is JSON serializable
        try:
            # Attempt to auto-detect local audio files for generated results
            try:
                songs_dir = os.path.join(ROOT, 'songs')
                available_files = []
                if os.path.isdir(songs_dir):
                    for fname in os.listdir(songs_dir):
                        lower = fname.lower()
                        if lower.endswith('.mp3') or lower.endswith('.wav') or lower.endswith('.ogg'):
                            available_files.append(fname)

                def slugify(s):
                    return ''.join(c if c.isalnum() else '_' for c in (s or '').lower()).strip('_')

                for s in result:
                    if s.get('file'):
                        continue
                    found = None
                    try:
                        sid = str(s.get('id'))
                        candidate = sid + '.mp3'
                        if candidate in available_files:
                            found = os.path.join('songs', candidate).replace('\\', '/')
                    except Exception:
                        pass
                    if not found:
                        title = s.get('title') or s.get('song') or ''
                        slug = slugify(title)
                        for ext in ('.mp3', '.wav', '.ogg'):
                            c = slug + ext
                            if c in available_files:
                                found = os.path.join('songs', c).replace('\\', '/')
                                break
                    if not found:
                        title = s.get('title') or s.get('song') or ''
                        for ext in ('.mp3', '.wav', '.ogg'):
                            c = (title + ext)
                            if c in available_files:
                                found = os.path.join('songs', c).replace('\\', '/')
                                break
                    if found:
                        s['file'] = found
            except Exception:
                # non-fatal: if detection fails, continue to send result anyway
                pass
            self.send_response(HTTPStatus.OK)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


if __name__ == '__main__':
    os.chdir(ROOT)
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print("Server is running. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nShutting down')
        finally:
            httpd.server_close()
