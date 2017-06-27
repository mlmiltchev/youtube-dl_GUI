import configparser
import os
import tkinter as tk
import tkinter.filedialog
import youtube_dl
import threading
import time
import webbrowser

# Separate StatusBar class for code clarity
class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief="sunken", anchor="w")
        self.label.pack(fill="x")

    def set(self, sFormat, *args):
        self.label.config(text=sFormat % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

# Main GUI class
class GUI:
    # Constructor
    def __init__(self, master):
        self.master = master
        # Create config.ini if it doesn't exist
        self.createDefaultConfig()

        # Setup for the program to use config.ini variables
        self.originalCwd = os.getcwd()
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")

        # Variables
        self.optionAudio = tk.BooleanVar(master, config["Options"]["audioonly"])
        self.optionHTTP = tk.BooleanVar(master, config["Options"]["usehttp"])
        self.optionBypass = tk.BooleanVar(master, config["Options"]["bypassgeo"])

        self.defaultOutput = tk.StringVar(master, config["Options"]["nameformat"])
        self.defaultPath = tk.StringVar(master, config["Options"]["path"])

        self.defaultUsername = tk.StringVar(master, config["Options"]["username"])
        self.defaultPassword = tk.StringVar(master, config["Options"]["password"])

        self.ytdlOptions = {"quiet": False}

        # Setting up the window
        # Title
        master.title("MTTF's YouTube Downloader")

        # Disable resizing
        master.resizable(width=False, height=False)

        # Icon
        if os.path.isfile("moon.ico"):
            master.iconbitmap(default="moon.ico")

        # Menu Bar
        menuBar = tk.Menu(master, bg="grey")
        menuBar.add_command(label="Basic", command=self.basicPress)
        menuBar.add_command(label="Advanced", command=self.advancedPress)
        menuBar.add_command(label="About", command=self.aboutPress)
        master.config(menu=menuBar)

        # Main Frame
        self.mainFrame = tk.Frame(master)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)

        # Layout
        self.basicPress()

        # Status Bar
        self.statusBar = StatusBar(master)
        self.statusBar.set("Waiting...")
        self.statusBar.pack(side="bottom", fill="x")

    # Basic menu button
    def basicPress(self):
        self.mainFrame.destroy()

        # Set Window Size
        self.master.geometry("325x150")

        # Main Frame
        self.mainFrame = tk.Frame(self.master)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)

        # Entries
        linkEntryLabel = tk.Label(self.mainFrame, text="YouTube URL")
        self.linkEntry = tk.Entry(self.mainFrame)
        saveEntryLabel = tk.Label(self.mainFrame, text="Save Location")
        saveEntry = tk.Entry(self.mainFrame, textvariable=self.defaultPath)

        linkEntryLabel.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")
        self.linkEntry.grid(row=1, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        saveEntryLabel.grid(row=2, column=0, padx=5, pady=(5, 0), sticky="w")
        saveEntry.grid(row=3, column=0, columnspan=2, padx=5, pady=0, sticky="we")

        # Buttons
        chooseCwdButton = tk.Button(self.mainFrame, text="Browse...", command=self.browsePress)
        downloadButton = tk.Button(self.mainFrame, text="Download", command=self.downloadPress)

        chooseCwdButton.grid(row=3, column=2, padx=5, pady=0, sticky="we")
        downloadButton.grid(row=10, column=2, padx=5, pady=(5, 0), sticky="e")

        # Options
        audioCheck = tk.Checkbutton(self.mainFrame, text="Audio Only", variable=self.optionAudio)
        audioCheck.grid(row=10, column=0, padx=5, pady=(5, 0), sticky="w")

    # Advanced menu button
    def advancedPress(self):
        # Set window size
        self.master.geometry("325x710")

        # Entires
        outputLabel = tk.Label(self.mainFrame, text="Output Template")
        outputEntry = tk.Entry(self.mainFrame, textvariable=self.defaultOutput)
        usernameLabel = tk.Label(self.mainFrame, text="Username/Email")
        usernameEntry = tk.Entry(self.mainFrame, textvariable=self.defaultUsername)
        passwordLabel = tk.Label(self.mainFrame, text="Password")
        passwordEntry = tk.Entry(self.mainFrame, textvariable=self.defaultPassword, show="*")

        outputLabel.grid(row=4, column=0, padx=5, pady=(5, 0), sticky="w")
        outputEntry.grid(row=5, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        usernameLabel.grid(row=6, column=0, padx=5, pady=(5, 0), sticky="w")
        usernameEntry.grid(row=7, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        passwordLabel.grid(row=8, column=0, padx=5, pady=(5, 0), sticky="w")
        passwordEntry.grid(row=9, column=0, columnspan=3, padx=5, pady=0, sticky="we")

        # Options
        httpCheck = tk.Checkbutton(self.mainFrame, text="Use HTTP", variable=self.optionHTTP)
        httpCheck.grid(row=10, column=1, padx=5, pady=(5, 0), sticky="w")
        bypassCheck = tk.Checkbutton(self.mainFrame, text="Bypass Geo Restriction (experimental)", variable=self.optionBypass)
        bypassCheck.grid(row=11, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="w")

        # Console output text widget
        consoleOutput = tk.Text(self.mainFrame, bg="grey15", fg="grey90", state="disabled")
        consoleOutput.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

    # About menu button
    def aboutPress(self):
        webbrowser.open(r"https://github.com/meantimetofailure/youtube-dl_GUI")

    # Browse button functionality. Choose directory.
    def browsePress(self):
        path = tk.filedialog.askdirectory()
        if path != "":
            self.defaultPath.set(path)

    # Download button functionality. Download video with options.
    def downloadPress(self):
        t = threading.Thread(target=self.downloadAction)
        t.start()

    # Only to be called from downloadPress()
    def downloadAction(self):
        # Updates status bar -> updates config file -> updates ytdlOptions -> downloads video/audio -> update status bar
        self.statusBar.set("Updating config.ini...")
        self.updateAllConfigFile()
        self.updateOptionDictionary()
        self.statusBar.set("Downloading...")
        with youtube_dl.YoutubeDL(self.ytdlOptions) as ytdler:
            try:
                ytdler.download([self.linkEntry.get()])
                self.statusBar.set("Done!")
            except youtube_dl.utils.YoutubeDLError:
                self.statusBar.set("Something went wrong! Download failed!")
        time.sleep(10)
        self.statusBar.set("Waiting...")

    # Update all settings in config.ini
    def updateAllConfigFile(self):
        self.updateConfigFile("Options", "path", self.defaultPath.get())
        self.updateConfigFile("Options", "nameformat", self.defaultOutput.get())
        self.updateConfigFile("Options", "audioonly", str(self.optionAudio.get()))
        self.updateConfigFile("Options", "usehttp", str(self.optionHTTP.get()))
        self.updateConfigFile("Options", "bypassgeo", str(self.optionBypass.get()))
        self.updateConfigFile("Options", "username", str(self.defaultUsername.get()))

    # Updates ytdlOptions.
    def updateOptionDictionary(self):
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")
        # path and filename option
        self.ytdlOptions["outtmpl"] = config["Options"]["path"] + "\\" + config["Options"]["nameformat"]

        # Audio Only
        if self.optionAudio.get():  # If 'Audio Only' is Checked
            self.ytdlOptions["format"] = "bestaudio[ext=m4a]/best"
            self.ytdlOptions["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                                  "preferredcodec": "mp3",
                                                  "preferredquality": "192"}]
        else:  # If 'Audio Only' is Unchecked
            if "postprocessors" in self.ytdlOptions.keys():
                del self.ytdlOptions["postprocessors"]
            self.ytdlOptions["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"

        # Use HTTP
        self.ytdlOptions["prefer_insecure"] = self.optionHTTP.get()

        # Bypass Geo Restiction (experimental)
        self.ytdlOptions["geo_bypass"] = self.optionBypass.get()

        # Username + Password
        if not self.defaultUsername.get() == "":  # If a username is present
            if not self.defaultPassword.get() == "":  # If a password is present
                self.ytdlOptions["username"] = self.defaultUsername.get()
                self.ytdlOptions["password"] = self.defaultPassword.get()

    # Create default config file if it doesn't exist
    def createDefaultConfig(self):
        if os.path.isfile(os.getcwd() + "\config.ini"):
            pass
        else:
            config = configparser.RawConfigParser()
            config["Options"] = {"path": os.getcwd(),
                                 "nameformat": "%(title)s.%(ext)s",
                                 "audioonly": False,
                                 "usehttp": False,
                                 "bypassgeo": False,
                                 "username": "",
                                 "password": ""
                                 }

            with open("config.ini", "w") as configfile:
                config.write(configfile)

    # Update one setting in config.ini
    # Only used in updateConfigFile()
    def updateConfigFile(self, heading, variable, result):
        # heading = the heading in the configuration file e.g. [Options]
        # variable = the variable under the heading e.g. path
        # result = what is stored in the variable e.g. C:\Hello_World\Example
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")
        config[heading][variable] = result

        with open(self.originalCwd + "\config.ini", "w") as configfile:
            config.write(configfile)

if __name__ == '__main__':
    root = tk.Tk()
    window = GUI(root)
    root.mainloop()

