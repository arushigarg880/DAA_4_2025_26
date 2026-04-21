#ifndef PLAYLIST_GENERATOR_H
#define PLAYLIST_GENERATOR_H

#include "song.h"
#include "datastore.h"
#include <unordered_map>
#include <vector>
#include <string>

class PlaylistGenerator {
public:
    PlaylistGenerator(std::unordered_map<int, std::vector<std::pair<int, double>>>& g, DataStore* ds);
    std::vector<Song> generatePlaylist(const std::string& mood, int count);

private:
    std::unordered_map<int, std::vector<std::pair<int, double>>>& graph;
    DataStore* datastore;
};

#endif
