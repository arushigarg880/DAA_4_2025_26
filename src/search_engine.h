#ifndef SEARCH_ENGINE_H
#define SEARCH_ENGINE_H

#include "song.h"
#include <vector>
#include <string>

class SearchEngine {
public:
    // Constructor accepts vector of songs (by value or const ref)
    SearchEngine(const std::vector<Song>& s);

    // Return matching songs (case-insensitive prefix)
    std::vector<Song> searchByPrefix(const std::string& prefix);

private:
    std::vector<Song> songs;
};

#endif
