#include <iostream>
#include <string>
#include "datastore.h"
#include "graph_builder.h"
#include "playlist_generator.h"
#include "search_engine.h"

using namespace std;

int main() {
    cout << "🎵 Welcome to MOODIFY — Mood-Based Playlist Generator 🎵\n" << endl;

    // 1) Load data (expects: project_root/data/songs.csv)
    DataStore ds;
    ds.loadSongs("data/songs.csv"); 
    // use data/songs.csv (not ../data/)
    cout << "Songs loaded: " << ds.songs.size() << endl;
    if (ds.songs.empty()) {
        cerr << "No songs loaded. Please ensure data/songs.csv exists and has valid rows." << endl;
        // continue anyway so program doesn't crash; user can still create file and rerun
    }

    // 2) Build graph
    GraphBuilder gb(ds.songs);

    // 3) Setup generator and search engine
    PlaylistGenerator pg(gb.graph, &ds);
    SearchEngine se(ds.songs);

    while (true) {
        cout << "\n1. Generate Playlist by Mood" << endl;
        cout << "2. Search Song by Title (prefix)" << endl;
        cout << "3. Exit" << endl;
        cout << "Choice: ";

        int choice;
        if (!(cin >> choice)) {
            cin.clear();
            cin.ignore(10000, '\n');
            cout << "Invalid input. Enter 1, 2 or 3." << endl;
            continue;
        }
        cin.ignore(10000, '\n'); // clear newline

        if (choice == 1) {
            cout << "Enter mood (exact match, e.g., happy, sad, romantic): ";
            string mood;
            getline(cin, mood);
            // normalize simple whitespace
            if (mood.size() && mood.back() == '\r') mood.pop_back();

            auto playlist = pg.generatePlaylist(mood, 10);
            if (playlist.empty()) {
                cout << "No songs found for mood '" << mood << "'. Try different mood or check data file." << endl;
            } else {
                cout << "\nGenerated Playlist (" << playlist.size() << " songs):\n";
                for (auto &s : playlist) s.display();
            }
        }
        else if (choice == 2) {
            cout << "Enter song title prefix (case-insensitive): ";
            string prefix;
            getline(cin, prefix);
            if (prefix.size() && prefix.back() == '\r') prefix.pop_back();

            auto results = se.searchByPrefix(prefix);
            if (results.empty()) {
                cout << "No matches found for prefix '" << prefix << "'." << endl;
            } else {
                cout << "\nSearch results (" << results.size() << "):\n";
                for (auto &s : results) s.display();
            }
        }
        else if (choice == 3) {
            cout << "Goodbye! 🎧" << endl;
            break;
        }
        else {
            cout << "Invalid choice. Enter 1, 2, or 3." << endl;
        }
    }

    return 0;
}
