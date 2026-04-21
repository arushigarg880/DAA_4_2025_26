Moodify — Lightweight local server

This repository contains a simple frontend (HTML/CSS/JS) and a minimal Python backend that serves the frontend and provides a tiny API to read the song database and generate playlists.

What I added
- `backend.py` — Python standard-library HTTP server with two API endpoints:
  - GET /api/songs — returns JSON list from `data/songs.csv`
  - POST /api/generate — accepts JSON {"mood": "happy", "limit": 10} and returns a filtered playlist
- Small change to `index.html` to add a "Generate" button near the search box
- `script.js` updated to fetch from the backend endpoints and render results (simulated playback — no mp3 files required)

How to run (Windows, no extra pip packages required)
1. Make sure you have Python 3 installed and available in PATH.
2. Open a PowerShell terminal in the project root (`c:\Users\sam51\Downloads\Moodify`).
3. Start the server:

```powershell
python backend.py
```

4. Open your browser to: http://localhost:8000

Notes
- The backend uses only Python's standard library (no Flask/Express required).
- The frontend no longer expects a `songs/` directory of mp3s; instead it pulls song metadata from `data/songs.csv`.
- `POST /api/generate` accepts `mood` (string) and `limit` (int). It filters by mood and sorts by `popularity`.

Audio files and C++ integration
- To enable real audio playback in the frontend, add a `file` column to `data/songs.csv` with a relative path to the audio file (for example: `songs/shape_of_you.mp3`). Example CSV header:

  id,title,artist,mood,genre,tempo,popularity,file

  1,Shape of You,Ed Sheeran,happy,pop,95,9,songs/shape_of_you.mp3

  The frontend will use the `file` value to play audio via the browser's HTMLAudioElement. If `file` is missing for a track, the UI will show the track but simulate playback icons only.

- The backend's `/api/generate` endpoint will now try to call `moodify.exe` (located in the project root) with arguments: `--mood <mood> --limit <n>` and expects JSON on stdout. If `moodify.exe` is missing or fails, the server falls back to CSV-based filtering. This lets you keep your C++ playlist logic and call it from the lightweight Python server without changing your build.

Auto-detection convenience
- You don't have to modify the CSV if you prefer a quick workflow — place audio files in a `songs/` folder under the project root and name them in one of these ways and the server will auto-detect them for you:
  - `id.mp3` where `id` matches the `id` field in the CSV (e.g., `1.mp3`), or
  - a slugified title like `shape_of_you.mp3` (letters/digits kept, non-alphanumeric replaced with `_`), or
  - the exact title name with extension (less preferred, may require exact matching of spacing/case).

  When the server finds a matching file it will add a `file` field to the JSON returned by `GET /api/songs`, so the frontend can immediately play it.

Security note: running executables from a web server can be dangerous if input is not validated; here we only pass sanitized simple parameters (mood/genre/limit) and run locally.

Next steps (optional)
- If you have mp3 files, update CSV rows to include a `file` column with a relative path (e.g., `songs/song.mp3`) and enhance `script.js` to actually play audio.
- Add more filtering criteria (genre, tempo range, etc.) to the generate endpoint.
