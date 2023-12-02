from dotenv import load_dotenv
import os
from tkinter import Tk, Toplevel, ttk, Label, Button, scrolledtext, Entry, messagebox
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import webbrowser
import tkinter as tk

load_dotenv()

class SpotifyCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.server.callback_received.set()
        self.server.callback_received.clear()

        response = b"<html><body><h1>Authentication successful. You can close this window/tab.</h1></body></html>"
        self.wfile.write(response)

class SpotifyCallbackServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.callback_received = threading.Event()

    def wait_for_callback(self):
        self.callback_received.wait()

    def shutdown(self):
        super().shutdown()
        self.callback_received.set()

class SpotifyApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Dashboard")

        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

        self.sp = None
        self.login_window = None

        self.create_login_page()

    def create_login_page(self):
        self.login_window = Toplevel(self)
        self.login_window.title("Login with Spotify")

        Label(self.login_window, text="Please log in with your Spotify account").pack(pady=10)

        login_button = Button(self.login_window, text="Login with Spotify", command=self.authenticate_spotify)
        login_button.pack(pady=10)

    def authenticate_spotify(self):
        auth_manager = SpotifyOAuth(
            self.client_id,
            self.client_secret,
            redirect_uri="http://localhost:8889/callback",
            scope="user-read-private user-read-email user-top-read user-library-read",
        )

        server = SpotifyCallbackServer(('localhost', 8889), SpotifyCallbackHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        try:
            auth_url = auth_manager.get_authorize_url()
            webbrowser.open(auth_url)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening authentication page: {str(e)}")
            return

        server.wait_for_callback()

        try:
            auth_manager.get_access_token(server.shutdown)
            messagebox.showinfo("Success", "Authentication successful! You can close this window/tab.")
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.login_window.withdraw()
            self.create_tabs()
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving access token: {str(e)}")

    def create_tabs(self):
        tab_control = ttk.Notebook(self)

        # Tab for Spotify Wrapped information
        wrapped_tab = ttk.Frame(tab_control)
        tab_control.add(wrapped_tab, text="Spotify Wrapped")
        self.create_wrapped_widgets(wrapped_tab)

        # Tab for Artist Search and Check Out New Release
        artist_tab = ttk.Frame(tab_control)
        tab_control.add(artist_tab, text="Artist Search & Releases")
        self.create_artist_widgets(artist_tab)

        tab_control.pack(expand=1, fill="both")

    def create_wrapped_widgets(self, parent):
        Label(parent, text="Your Wrapped is here").pack(pady=10)

        Button(parent, text="Get Your Spotify Wrapped", command=self.get_spotify_wrapped).pack(pady=10)

        self.spotify_wrapped_display = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=40, height=10)
        self.spotify_wrapped_display.pack(pady=10)

    def get_spotify_wrapped(self):
        if self.sp and self.sp.auth_manager.get_access_token() is not None:
            wrapped_data = self.get_spotify_wrapped_data()
            self.spotify_wrapped_display.delete(1.0, tk.END)
            self.spotify_wrapped_display.insert(tk.END, wrapped_data)
        else:
            messagebox.showwarning("Warning", "Token not found, please log in.")

    def get_spotify_wrapped_data(self):
        try:
            user_top_tracks = self.sp.current_user_top_tracks(limit=10, time_range="short_term")
            wrapped_data = "Your Spotify Wrapped Data:\n\n"
            for i, track in enumerate(user_top_tracks['items'], start=1):
                wrapped_data += f"{i}. {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}\n"
            return wrapped_data
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving Spotify Wrapped data: {str(e)}")
            return ""
    def create_wrapped_widgets(self, parent):
        Label(parent, text="Your Wrapped is here").pack(pady=10)

        # Add a button for getting both top tracks and top artists
        Button(parent, text="Get Your Spotify Wrapped", command=self.get_spotify_wrapped).pack(pady=10)

        self.spotify_wrapped_display = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=40, height=10)
        self.spotify_wrapped_display.pack(pady=10)

    def get_spotify_wrapped(self):
        if self.sp and self.sp.auth_manager.get_access_token() is not None:
            wrapped_data = self.get_spotify_wrapped_data()
            self.spotify_wrapped_display.delete(1.0, tk.END)
            self.spotify_wrapped_display.insert(tk.END, wrapped_data)
        else:
            messagebox.showwarning("Warning", "Token not found, please log in.")

    def get_spotify_wrapped_data(self):
        try:
            user_top_tracks = self.sp.current_user_top_tracks(limit=10, time_range="short_term")
            user_top_artists = self.sp.current_user_top_artists(limit=10, time_range="short_term")

            wrapped_data = "Your Spotify Wrapped Data:\n\nTop Tracks:\n"
            for i, track in enumerate(user_top_tracks['items'], start=1):
                wrapped_data += f"{i}. {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}\n"

            wrapped_data += "\nTop Artists:\n"
            for i, artist in enumerate(user_top_artists['items'], start=1):
                wrapped_data += f"{i}. {artist['name']}\n"

            return wrapped_data
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving Spotify Wrapped data: {str(e)}")
            return ""

    def create_artist_widgets(self, parent):
        Label(parent, text="Enter artist name:").grid(row=0, column=0, pady=10)

        self.artist_entry = Entry(parent)
        self.artist_entry.grid(row=0, column=1, pady=10)

        Button(parent, text="Search", command=self.search_and_display).grid(row=0, column=2, pady=10)

        Button(parent, text="Check Out New Release", command=self.display_new_releases).grid(row=2, column=2, pady=10)

    def search_and_display(self):
        artist_name = self.artist_entry.get()
        result = self.search_for_artist(artist_name)

        if result:
            artist_id = result["id"]
            songs = self.get_songs_by_artist(artist_id)
            if songs:
                self.display_songs(songs)
            else:
                messagebox.showinfo("No Songs", f"No songs found for {artist_name}.")
        else:
            messagebox.showinfo("No Results", f"No results found for {artist_name}.")

    def display_songs(self, songs):
        song_list = "\n".join([f"{idx + 1}. {song['name']}" for idx, song in enumerate(songs)])
        messagebox.showinfo("Songs", f"Songs:\n{song_list}")

    def search_for_artist(self, artist_name):
        try:
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            artists = results['artists']['items']
            return artists[0] if artists else None
        except Exception as e:
            messagebox.showerror("Error", f"Error searching for artist: {str(e)}")
            return None

    def get_songs_by_artist(self, artist_id):
        top_tracks = self.sp.artist_top_tracks(artist_id, country='US')
        return top_tracks['tracks']

    def display_new_releases(self):
        new_releases = self.get_new_releases()
        if new_releases:
            releases = "\n".join([f"- {release['name']}" for release in new_releases])
            messagebox.showinfo("Check Out New Release", f"Check Out New Release:\n{releases}")

    def get_new_releases(self):
        new_releases = self.sp.new_releases(country='US', limit=5)
        return new_releases['albums']['items']

if __name__ == "__main__":
    app = SpotifyApp()
    app.mainloop()
