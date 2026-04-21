CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -I./src

SRC = src
OBJS = $(SRC)/main.o

all: run

build:
	$(CXX) $(CXXFLAGS) $(SRC)/*.cpp -o moodify

run: build
	./moodify

clean:
	rm -f $(SRC)/*.o moodify
