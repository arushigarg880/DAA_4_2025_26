#ifndef GRAPH_BUILDER_H
#define GRAPH_BUILDER_H

#include "song.h"
#include <unordered_map>
#include <vector>
#include <cmath>

using namespace std;

class GraphBuilder {
public:
    unordered_map<int, vector<pair<int, double>>> graph;
    vector<Song> songs;

    GraphBuilder(const vector<Song>& songs) {
        this->songs = songs;
        buildGraph();
    }

    double similarityScore(const Song& a, const Song& b) {
        double score = 0;
        if (a.mood == b.mood) score += 3;
        if (a.genre == b.genre) score += 2;
        score -= fabs(a.tempo - b.tempo) / 50.0;
        return max(score, 0.0);
    }

    void buildGraph() {
        for (const auto &s1 : songs) {
            for (const auto &s2 : songs) {
                if (s1.id != s2.id) {
                    double sim = similarityScore(s1, s2);
                    if (sim > 0)
                        graph[s1.id].push_back({s2.id, sim});
                }
            }
        }
    }
};

#endif
