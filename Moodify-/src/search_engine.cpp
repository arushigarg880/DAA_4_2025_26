#include "search_engine.h"
#include <algorithm>
#include <cctype>

static std::string toLower(const std::string &in) {
    std::string s = in;
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c){ return std::tolower(c); });
    return s;
}

SearchEngine::SearchEngine(const std::vector<Song>& s) : songs(s) {}

std::vector<Song> SearchEngine::searchByPrefix(const std::string& prefix) {
    std::vector<Song> result;
    if (prefix.empty()) return result;

    std::string p = toLower(prefix);
    for (const auto &song : songs) {
        std::string titleLower = toLower(song.title);
        if (titleLower.rfind(p, 0) == 0) { // prefix match
            result.push_back(song);
        }
    }
    return result;
}
