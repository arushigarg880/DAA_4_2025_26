#!/usr/bin/env python3
"""
One-shot test script that exercises all Moodify functionality once and exits
"""
import socketserver
import os
import webbrowser
import threading
import time
import sys

PORT = 8000
ROOT = os.path.abspath(os.path.dirname(__file__))


def main():
    """Start the server and keep it running until the user has loaded the page.

    Behavior:
    - Start the HTTP server (using the project's `Handler` from `backend.py`).
    - Open the browser to the root URL.
    - Wait until a GET request for `/` (the main page) is received.
    - After the page is loaded, keep the server running until the user presses Enter.
    """
    print("\nStarting Moodify server...")
    print(f"Server will be available at http://localhost:{PORT}")

    os.chdir(ROOT)

    # Import Handler here to avoid circular import at module import time
    from backend import Handler

    page_loaded = threading.Event()

    # Create a small wrapper handler that signals when the root page is requested
    class PageDetectHandler(Handler):
        def do_GET(self):
            # Mark page as loaded when the root path or index is requested
            try:
                path = self.path.split('?', 1)[0]
            except Exception:
                path = self.path
            if path == '/' or path.endswith('index.html'):
                page_loaded.set()
            return super().do_GET()

    httpd = socketserver.TCPServer(('', PORT), PageDetectHandler)

    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    try:
        # Open the webpage for the user
        webbrowser.open(f'http://localhost:{PORT}')

        print("\nWaiting for you to load the page in your browser...")
        # Wait indefinitely until the page is requested
        page_loaded.wait()

        print("\nPage load detected. The server will remain running until you stop it.")
        print("When you're done, return here and press Enter to shut the server down.")
        input()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("\nShutting down server...")
        try:
            httpd.shutdown()
        except Exception:
            pass
        httpd.server_close()
        print("Server shutdown complete.")
        sys.exit(0)


if __name__ == '__main__':
    main()