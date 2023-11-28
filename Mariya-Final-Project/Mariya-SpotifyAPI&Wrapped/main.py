from dotenv import load_dotenv
import os
from tkinter import Tk, ttk, Label, Entry, Button, messagebox
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

class SpotifyApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Dashboard")

        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

        self.sp = self.authenticate_spotify()

        self.create_tabs()

    def authenticate_spotify(self):
        auth_manager = SpotifyOAuth(
            self.client_id,
            self.client_secret,
            redirect_uri = "http://localhost:8889/callback",
            scope="user-read-private user-read-email user-top-read user-library-read",
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    
    def create_tabs(self):
        tab_control = ttk.Notebook(self)

        # Tab for Spotify Wrappedrmation
        user_info_tab = ttk.Frame(tab_control)
        tab_control.add(user_info_tab, text="Spotify Wrapped")
        self.create_user_info_widgets(user_info_tab)

        # Tab for Artist Search and Check Out New Release
        artist_search_tab = ttk.Frame(tab_control)
        tab_control.add(artist_search_tab, text="Artist Search & Releases")
        self.create_artist_search_widgets(artist_search_tab)

        tab_control.pack(expand=1, fill="both")


    def create_user_info_widgets(self, parent):
        Label(parent, text="Your Wrapped is here").pack(pady=10)

        Button(parent, text="Get Your top songs", command=self.get_top_songs).pack(pady=10)

        Button(parent, text="Get Your top artists", command=self.get_top_artists).pack(pady=10)

    def create_artist_search_widgets(self, parent):
        Label(parent, text="Enter artist name:").grid(row=0, column=0, pady=10)

        self.artist_entry = Entry(parent)
        self.artist_entry.grid(row=0, column=1, pady=10)

        Button(parent, text="Search", command=self.search_and_display).grid(row=0, column=2, pady=10)

        Button(parent, text="Check Out New Release", command=self.display_new_releases).grid(row=2, column=2, pady=10)

    def get_top_songs(self):
        if self.sp.auth_manager.get_access_token() is not None:
            user_top_songs = self.sp.current_user_top_tracks(
                limit=10,
                offset=0,
                time_range="medium_term"
            )

            message = "Your top songs were:\n"
            for i, track in enumerate(user_top_songs['items'], start=1):
                message += f"{i}. {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}\n"

            messagebox.showinfo("Your top songs were", message)
        else:
            messagebox.showwarning("Warning", "Token not found, please log in.")

    def get_top_artists(self):
        if self.sp.auth_manager.get_access_token() is not None:
            user_top_artists = self.sp.current_user_top_artists(
                limit=10,
                offset=0,
                time_range="medium_term"
            )

            message = "Your top artist was:\n"
            for i, artist in enumerate(user_top_artists['items'], start=1):
                message += f"{i}. {artist['name']}\n"

            messagebox.showinfo("Your top artist were", message)
        else:
            messagebox.showwarning("Warning", "Token not found, please log in.")

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

    def get_new_releases(self):
        new_releases = self.sp.new_releases(country='US', limit=5)
        return new_releases['albums']['items']

if __name__ == "__main__":
    app = SpotifyApp()
    app.mainloop()
 

