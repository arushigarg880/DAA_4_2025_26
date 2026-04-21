#ifndef DATASTORE_H
#define DATASTORE_H

#include "song.h"
#include <vector>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

class DataStore {
public:
    vector<Song> songs;
    unordered_map<int, Song> songMap;
    unordered_map<string, vector<Song>> moodMap;
    unordered_map<string, vector<Song>> genreMap;

    // default path expects songs.csv in project_root/data/songs.csv
    void loadSongs(const string& filename = "data/songs.csv") {
        ifstream file(filename);
        if (!file.is_open()) {
            cerr << "Error: Could not open file " << filename << endl;
            return;
        }

        string line;
        // assume first line is header - if not, you can remove this getline
        getline(file, line);

        int lineNo = 1;
        while (getline(file, line)) {
            lineNo++;
            if(line.empty()) continue;
            stringstream ss(line);
            string id_s, title, artist, mood, genre, tempo_s, popularity_s;

            // CSV columns: id,title,artist,mood,genre,tempo,popularity
            if (!getline(ss, id_s, ',')) continue;
            if (!getline(ss, title, ',')) continue;
            if (!getline(ss, artist, ',')) continue;
            if (!getline(ss, mood, ',')) continue;
            if (!getline(ss, genre, ',')) continue;
            if (!getline(ss, tempo_s, ',')) continue;
            if (!getline(ss, popularity_s, ',')) {
                // maybe no trailing comma - try to extract rest
                string rest;
                if (getline(ss, rest)) popularity_s = rest;
            }

            try {
                int id = stoi(id_s);
                int tempo = stoi(tempo_s);
                int popularity = stoi(popularity_s);
                Song s(id, title, artist, mood, genre, tempo, popularity);
                songs.push_back(s);
                songMap[s.id] = s;
                moodMap[mood].push_back(s);
                genreMap[genre].push_back(s);
            } catch (...) {
                cerr << "Warning: skipping malformed line " << lineNo << endl;
            }
        }

        file.close();
    }
};

#endif
