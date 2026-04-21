// Frontend logic with optional real audio playback
let songs = [];
let currentSongIndex = -1;
let currentAudio = null;
let pendingSeekPercent = null; // store requested seek percent until metadata is loaded

const ICON_FOLDER = "icon/";
const PLAY_ICON_SRC = ICON_FOLDER + "play.svg";
const PAUSE_ICON_SRC = ICON_FOLDER + "pause.svg";
const MUSIC_ICON_SRC = ICON_FOLDER + "music.svg";

async function getSongs() {
    try {
        const res = await fetch('/api/songs');
        if (!res.ok) throw new Error(res.statusText);
        return await res.json();
    } catch (e) {
        console.error('Failed to fetch songs from backend:', e);
        return [];
    }
}

// Helper: slugify text to create filename-friendly keys
function slugify(text) {
    return (text || '').toString().toLowerCase()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^a-z0-9\-]/g, '')    // Remove invalid chars
        .replace(/\-+/g, '-')           // Collapse dashes
        .replace(/^-+|-+$/g, '');        // Trim dashes
}

// Check whether a given image URL exists (HEAD request)
async function imageExists(url) {
    try {
        const res = await fetch(url, { method: 'HEAD' });
        return res.ok;
    } catch (e) {
        return false;
    }
}

// Populate the artists and albums UI sections using songs data
async function populateArtistsAndAlbums(songsList) {
    if (!songsList || songsList.length === 0) return;
    const artistsRow = document.querySelector('.artists-row');
    const albumsGrid = document.querySelector('.albums-grid');
    if (!artistsRow || !albumsGrid) return;

    // Build unique artist list and album list (limit to 12 each)
    const artistsMap = new Map();
    const albumsMap = new Map();
    for (const s of songsList) {
        const artist = (s.artist || 'Unknown Artist').trim();
        const title = (s.title || s.song || 'Unknown Title').trim();
        if (!artistsMap.has(artist)) artistsMap.set(artist, s);
        if (!albumsMap.has(title)) albumsMap.set(title, s);
        if (artistsMap.size >= 12 && albumsMap.size >= 12) break;
    }

    // Helper to resolve an image for an entity (artist or album)
    async function resolveImage(kind, name) {
        const slug = slugify(name);
        const variants = [`.jpg`, `.png`, `.jpeg`];
        for (const ext of variants) {
            const candidate = `images/${kind}/${slug}${ext}`;
            if (await imageExists(candidate)) return candidate;
        }
        // fallback to icon folder
        return MUSIC_ICON_SRC;
    }

    // Populate artists
    artistsRow.innerHTML = '';
    for (const [artist, sample] of Array.from(artistsMap.entries()).slice(0, 12)) {
        const el = document.createElement('div');
        el.className = 'artist-card';
        const imgWrapper = document.createElement('div');
        imgWrapper.className = 'artist-avatar';
        const imgEl = document.createElement('img');
        imgEl.alt = artist;
        imgEl.className = 'artist-img';
        // optimistic placeholder while resolving
        imgEl.src = MUSIC_ICON_SRC;
        imgWrapper.appendChild(imgEl);
        const nameEl = document.createElement('div'); nameEl.className = 'artist-name'; nameEl.textContent = artist;
        const subEl = document.createElement('div'); subEl.className = 'artist-sub'; subEl.textContent = 'Artist';
        el.appendChild(imgWrapper); el.appendChild(nameEl); el.appendChild(subEl);
        artistsRow.appendChild(el);

        // Resolve and set image (async)
        resolveImage('artists', artist).then(url => { imgEl.src = url; }).catch(() => {});
    }

    // Populate albums
    albumsGrid.innerHTML = '';
    for (const [title, sample] of Array.from(albumsMap.entries()).slice(0, 12)) {
        const el = document.createElement('div'); el.className = 'album-card';
        const art = document.createElement('div'); art.className = 'album-art';
        const img = document.createElement('img'); img.className = 'album-img'; img.alt = title; img.src = MUSIC_ICON_SRC;
        art.appendChild(img);
        const tt = document.createElement('div'); tt.className = 'album-title'; tt.textContent = title;
        el.appendChild(art); el.appendChild(tt);
        albumsGrid.appendChild(el);

        resolveImage('albums', title).then(url => { img.src = url; }).catch(() => {});
    }
}

function displaySongs(list) {
    const songUL = document.querySelector('.song-list ul');
    songUL.innerHTML = '';
    if (!list || list.length === 0) {
        songUL.innerHTML = `<li class="no-results-found">No results found.</li>`;
        return;
    }

    list.forEach((s, idx) => {
        const title = s.title || s.song || 'Unknown Title';
        const artist = s.artist || 'Unknown Artist';
        const li = document.createElement('li');
        li.className = 'music-card-list-item';
        li.setAttribute('data-index', idx);
        const playable = !!s.file;
        li.innerHTML = `
            <div class="music-card-in-list">
                <div class="music-icon">
                    <img class="invert" src="${MUSIC_ICON_SRC}" alt="Music icon">
                </div>
                <div class="song-info-list">
                    <h4 class="song-title-list">${title}</h4>
                    <p class="artist-name-list">${artist}</p>
                </div>
                <div class="controls-list">
                    <img class="play-pause-list-button ${playable ? '' : 'disabled'} invert" src="${playable ? PLAY_ICON_SRC : MUSIC_ICON_SRC}" alt="Play">
                </div>
            </div>
        `;
        songUL.appendChild(li);

        li.addEventListener('click', (ev) => {
            const idx = parseInt(li.getAttribute('data-index'));
            const btn = ev.target.closest('.play-pause-list-button');
            const trackPlayable = !!(s.file);
            if (!trackPlayable) {
                // clearly inform the user that this track isn't available locally
                showPlaybackError('This track has no local audio file. Add the file to the songs/ folder or set the file column in data/songs.csv');
                return;
            }
            if (btn) {
                if (currentSongIndex === idx) {
                    // toggle play/pause
                    if (currentAudio) {
                        if (currentAudio.paused) currentAudio.play(); else currentAudio.pause();
                        updateMainPlayIcon();
                    } else {
                        playMusic(idx);
                    }
                } else {
                    playMusic(idx);
                }
            } else {
                playMusic(idx);
            }
        });
    });
}

function updateMainPlayIcon() {
    const main = document.querySelector('#play');
    if (!main) return;
    if (currentAudio && !currentAudio.paused) main.src = PAUSE_ICON_SRC; else main.src = PLAY_ICON_SRC;
}

function clearCurrentAudio() {
    if (currentAudio) {
        try { currentAudio.pause(); } catch (e) {}
        currentAudio = null;
    }
    document.querySelector('.song-info').textContent = '';
    document.querySelector('.song-info').style.display = 'none';
    document.querySelector('.song-time-left').textContent = '00:00';
    document.querySelector('.song-time-right').textContent = '00:00';
    document.querySelector('.seekbar-progress').style.width = '0%';
    document.querySelector('.seekbar-circle').style.left = '0%';
    document.querySelectorAll('.play-pause-list-button').forEach(i => i.src = PLAY_ICON_SRC);
    updateMainPlayIcon();
    // clear any shown playback error
    const errEl = document.querySelector('.playback-error');
    if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
}

function playMusic(index) {
    if (index < 0 || index >= songs.length) return;

    const track = songs[index];
    const title = track.title || track.song || 'Unknown Title';
    const artist = track.artist || 'Unknown Artist';

    // If track has a `file` path, play actual audio; otherwise simulated UI only
    clearCurrentAudio();
    currentSongIndex = index;
    document.querySelector('.song-info').textContent = `${title} - ${artist}`;
    document.querySelector('.song-info').style.display = 'block';

    const listBtn = document.querySelector(`.music-card-list-item[data-index="${index}"] .play-pause-list-button`);
    if (listBtn) listBtn.src = PAUSE_ICON_SRC;

    if (track.file) {
        // file can be a relative path like songs/track.mp3
        currentAudio = new Audio(track.file);
        // clear any pending seek for previous track
        pendingSeekPercent = null;
        // show friendly loading state
        const errEl = document.querySelector('.playback-error');
        if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
        // when metadata loads, enable seeking and apply any pending seek
        currentAudio.addEventListener('loadedmetadata', () => {
            try {
                const dur = currentAudio.duration || 0;
                document.querySelector('.song-time-right').textContent = formatTime(dur);
                if (pendingSeekPercent !== null && !isNaN(dur) && dur > 0) {
                    currentAudio.currentTime = Math.min(dur * pendingSeekPercent, dur);
                    pendingSeekPercent = null;
                }
                // update seekbar visuals immediately
                if (!isNaN(dur) && dur > 0) {
                    const percent = (currentAudio.currentTime / dur) * 100;
                    document.querySelector('.seekbar-progress').style.width = percent + '%';
                    document.querySelector('.seekbar-circle').style.left = percent + '%';
                }
            } catch (e) {
                // ignore
            }
        });
        // error handler for playback issues (missing file, CORS, permission)
        currentAudio.addEventListener('error', (ev) => {
            console.warn('Audio element error', ev);
            showPlaybackError('Playback failed: file missing, blocked by CORS, or not accessible.');
            // reset icons/state
            const btn = document.querySelector(`.music-card-list-item[data-index="${currentSongIndex}"] .play-pause-list-button`);
            if (btn) btn.src = PLAY_ICON_SRC;
            clearCurrentAudio();
        });
        currentAudio.addEventListener('timeupdate', () => {
            document.querySelector('.song-time-left').textContent = formatTime(currentAudio.currentTime);
            document.querySelector('.song-time-right').textContent = formatTime(currentAudio.duration || 0);
            if (currentAudio.duration > 0) {
                const percent = (currentAudio.currentTime / currentAudio.duration) * 100;
                document.querySelector('.seekbar-progress').style.width = percent + '%';
                document.querySelector('.seekbar-circle').style.left = percent + '%';
            }
        });
        currentAudio.addEventListener('ended', () => {
            const btn = document.querySelector(`.music-card-list-item[data-index="${currentSongIndex}"] .play-pause-list-button`);
            if (btn) btn.src = PLAY_ICON_SRC;
            clearCurrentAudio();
            playNextSong();
        });
        currentAudio.play().catch(e => {
            console.warn('Playback failed (promise reject):', e);
            showPlaybackError('Playback blocked by browser (autoplay policy or permission). Click a track to start playback.');
            // ensure UI shows play icon
            const btn = document.querySelector(`.music-card-list-item[data-index="${currentSongIndex}"] .play-pause-list-button`);
            if (btn) btn.src = PLAY_ICON_SRC;
            clearCurrentAudio();
        });
    } else {
        // simulated playback: only update main icon
        updateMainPlayIcon();
    }
    updateMainPlayIcon();
}

function showPlaybackError(msg, timeout = 6000) {
    const errEl = document.querySelector('.playback-error');
    if (!errEl) return;
    errEl.textContent = msg;
    errEl.style.display = 'block';
    // clear after timeout
    if (timeout > 0) {
        setTimeout(() => {
            try { errEl.style.display = 'none'; errEl.textContent = ''; } catch (e) {}
        }, timeout);
    }
}

// Utility: format seconds as MM:SS (defensive - handles NaN/undefined)
function formatTime(sec) {
    const s = Number(sec) || 0;
    if (!isFinite(s) || s <= 0) return '00:00';
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    return String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
}

function playNextSong() {
    if (songs.length === 0) return;
    const next = (currentSongIndex + 1) % songs.length;
    playMusic(next);
}

function playPreviousSong() {
    if (songs.length === 0) return;
    const prev = (currentSongIndex - 1 + songs.length) % songs.length;
    playMusic(prev);
}

async function generatePlaylist(mood, limit = 10) {
    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood: mood || '', limit })
        });
        if (!res.ok) throw new Error(res.statusText);
        const results = await res.json();
        songs = results;
        displaySongs(songs);
        // reset audio state
        clearCurrentAudio();
    } catch (e) {
        console.error('Failed to generate playlist:', e);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    songs = await getSongs();
    displaySongs(songs);
    // populate artists and albums sections (images will be resolved if available)
    populateArtistsAndAlbums(songs);

    const mainPlay = document.querySelector('#play');
    if (mainPlay) {
        mainPlay.addEventListener('click', () => {
            if (currentSongIndex === -1 && songs.length > 0) {
                playMusic(0);
                return;
            }
            if (currentAudio) {
                if (currentAudio.paused) currentAudio.play(); else currentAudio.pause();
            } else {
                // toggle main icon visually
                const main = document.querySelector('#play');
                if (main.src.includes('play.svg')) main.src = PAUSE_ICON_SRC; else main.src = PLAY_ICON_SRC;
            }
            updateMainPlayIcon();
        });
    }

    document.querySelector('#next')?.addEventListener('click', playNextSong);
    document.querySelector('#previous')?.addEventListener('click', playPreviousSong);

    const seekbar = document.querySelector('.seekbar');
    let isDragging = false;

    // Handle click for immediate seeking
    seekbar.addEventListener('click', (e) => {
        if (!currentAudio) return;
        const rect = seekbar.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        let percent = offsetX / rect.width;
        if (percent < 0) percent = 0; if (percent > 1) percent = 1;
        if (!isNaN(currentAudio.duration) && currentAudio.duration > 0) {
            currentAudio.currentTime = currentAudio.duration * percent;
        } else {
            pendingSeekPercent = percent;
            showPlaybackError('Seeking will occur when the track metadata finishes loading', 2000);
        }
    });

    // Handle drag seeking
    seekbar.addEventListener('mousedown', (e) => {
        isDragging = true;
        seekbar.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging || !currentAudio) return;
        const rect = seekbar.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        let percent = offsetX / rect.width;
        if (percent < 0) percent = 0; if (percent > 1) percent = 1;
        
        // Update the seekbar visually while dragging
        const progress = seekbar.querySelector('.seekbar-progress');
        if (progress) {
            progress.style.width = `${percent * 100}%`;
        }
    });

    document.addEventListener('mouseup', (e) => {
        if (!isDragging || !currentAudio) {
            isDragging = false;
            seekbar.style.cursor = 'pointer';
            return;
        }
        
        const rect = seekbar.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        let percent = offsetX / rect.width;
        if (percent < 0) percent = 0; if (percent > 1) percent = 1;
        
        if (!isNaN(currentAudio.duration) && currentAudio.duration > 0) {
            currentAudio.currentTime = currentAudio.duration * percent;
        }
        
        isDragging = false;
        seekbar.style.cursor = 'pointer';
    });

    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('input', (ev) => {
        const term = ev.target.value.toLowerCase().trim();
        if (term === '') displaySongs(songs);
        else {
            const filtered = songs.filter(s => (s.title || '').toLowerCase().includes(term) || (s.artist || '').toLowerCase().includes(term));
            displaySongs(filtered);
        }
    });

    document.querySelector('#generate-btn')?.addEventListener('click', () => {
        const q = document.querySelector('.search-input').value.trim();
        // use input as mood if provided
        generatePlaylist(q || null, 12);
    });


});
