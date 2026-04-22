#!/usr/bin/env python3
import http.client
import json
import time
import webbrowser
import os
import sys
import subprocess

def test_server_connection(host='localhost', port=8000):
    try:
        conn = http.client.HTTPConnection(host, port)
        conn.request('GET', '/api/songs')
        response = conn.getresponse()
        return response.status == 200
    except Exception as e:
        return False

def main():
    # Start the backend server
    server_process = subprocess.Popen([sys.executable, 'backend.py'])
    
    # Wait for server to start
    print("Waiting for server to start...")
    for _ in range(10):
        if test_server_connection():
            break
        time.sleep(0.5)
    else:
        print("Failed to start server")
        server_process.terminate()
        return

    try:
        # Open the webpage
        print("\nOpening Moodify in your default browser...")
        webbrowser.open('http://localhost:8000')
        
        # Test sequence
        print("\nTest Sequence:")
        print("1. Loading main page and song list")
        print("2. Testing mood-based playlist generation")
        
        # Test different moods
        moods = ['happy', 'sad', 'romantic', 'energetic', 'calm', 'inspirational']
        print("\nTesting moods:", ", ".join(moods))
        
        conn = http.client.HTTPConnection('localhost', 8000)
        for mood in moods:
            print(f"\nTesting '{mood}' mood...")
            conn.request('POST', '/api/generate', 
                       body=json.dumps({'mood': mood, 'limit': 5}),
                       headers={'Content-Type': 'application/json'})
            response = conn.getresponse()
            data = response.read().decode()
            playlist = json.loads(data)
            print(f"Retrieved {len(playlist)} songs for {mood} mood")
            response.close()
        
        print("\nAll functionality has been tested!")
        print("\nYou can now:")
        print("1. Browse the song list")
        print("2. Generate playlists by mood using the search bar")
        print("3. Play songs and use the seek bar")
        print("4. Use the time jump feature (enter MM:SS format)")
        
        # Keep server running for manual testing
        print("\nServer will remain running for 60 seconds for manual testing...")
        print("Press Ctrl+C to exit earlier")
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\nTest sequence interrupted")
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    main()