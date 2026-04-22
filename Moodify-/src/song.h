#ifndef SONG_H
#define SONG_H

#include <string>
#include <iostream>

class Song {
public:
    int id;
    std::string title;
    std::string artist;
    std::string mood;
    std::string genre;
    int tempo;
    int popularity;

    Song() {}
    Song(int i, const std::string &t, const std::string &a, const std::string &m,
         const std::string &g, int temp, int pop)
        : id(i), title(t), artist(a), mood(m), genre(g), tempo(temp), popularity(pop) {}

    void display() const {
        std::cout << title << " by " << artist << " (" << mood << ", " << genre << ")\n";
    }
};

#endif
