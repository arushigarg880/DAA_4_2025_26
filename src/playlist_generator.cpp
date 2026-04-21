#include "playlist_generator.h"
#include <algorithm>
#include <cctype>

static std::string toLower(const std::string &in) {
    std::string s = in;
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c){ return std::tolower(c); });
    return s;
}

PlaylistGenerator::PlaylistGenerator(std::unordered_map<int, std::vector<std::pair<int, double>>>& g, DataStore* ds)
    : graph(g), datastore(ds) {}

std::vector<Song> PlaylistGenerator::generatePlaylist(const std::string& mood, int count) {
    std::vector<Song> result;
    std::string moodLower = toLower(mood);

    for (auto& song : datastore->songs) {
        if (toLower(song.mood) == moodLower) {
            result.push_back(song);
        }
        if (result.size() >= (size_t)count) break;
    }
    return result;
}
