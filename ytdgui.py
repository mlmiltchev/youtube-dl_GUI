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
        # Create config.ini if it doesn't exist
        self.createDefaultConfig()

        # Setup for the program to use config.ini variables
        self.originalCwd = os.getcwd()
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")

        # Variables
        self.optionAudio = tk.BooleanVar(master, config["Options"]["audioonly"])
        self.defaultPath = tk.StringVar(master, config["Options"]["path"])

        self.ytdlOptions = {"quiet": True}

        # Setting up the window
        # Title
        master.title("MTTF's YouTube Downloader")

        # Size, Resizeable, and Centered
        self.width = 325
        self.height = 150

        self.screenWidth = master.winfo_screenwidth()
        self.screenHeight = master.winfo_screenheight()

        self.x = (self.screenWidth / 2) - (self.width / 2)
        self.y = (self.screenHeight / 2) - (self.height / 2)

        master.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x, self.y))

        master.resizable(width=False, height=False)

        # Icon
        if os.path.isfile("moon.ico"):
            master.iconbitmap(default="moon.ico")

        # Menu Bar
        menuBar = tk.Menu(master, bg="grey")
        menuBar.add_command(label="Basic", command=self.basicPress)
        menuBar.add_command(label="Average", command=self.basicPress)
        menuBar.add_command(label="Advanced", command=self.basicPress)
        menuBar.add_command(label="About", command=self.aboutPress)
        master.config(menu=menuBar)

        # Main Frame
        self.mainFrame = tk.Frame(master)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)

        # Entries
        self.linkEntryLabel = tk.Label(self.mainFrame, text="YouTube URL")
        self.linkEntry = tk.Entry(self.mainFrame)
        self.saveEntryLabel = tk.Label(self.mainFrame, text="Save Location")
        self.saveEntry = tk.Entry(self.mainFrame, textvariable=self.defaultPath)
        self.chooseCwdButton = tk.Button(self.mainFrame, text="Browse...", command=self.browsePress)

        self.linkEntryLabel.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")
        self.linkEntry.grid(row=1, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        self.saveEntryLabel.grid(row=2, column=0, padx=5, pady=(5, 0), sticky="w")
        self.saveEntry.grid(row=3, column=0, columnspan=2, padx=5, pady=0, sticky="we")
        self.chooseCwdButton.grid(row=3, column=2, padx=5, pady=0, sticky="we")

        # Options
        self.audioCheck = tk.Checkbutton(self.mainFrame, text="Audio Only", variable=self.optionAudio)
        self.audioCheck.grid(row=4, column=0, padx=5, pady=(5, 0), sticky="w")

        # Download Button
        self.downloadButton = tk.Button(self.mainFrame, text="Download", command=self.downloadPress)
        self.downloadButton.grid(row=4, column=2, padx=5, pady=(5, 0), sticky="e")

        # Status Bar
        self.statusBar = StatusBar(master)
        self.statusBar.set("Waiting...")
        self.statusBar.pack(side="bottom", fill="x")

    # Browse button function. Choose directory.
    def browsePress(self):
        path = tk.filedialog.askdirectory()
        if path != "":
            self.defaultPath.set(path)

    # Download button function. Download video with options.
    def downloadPress(self):
        t = threading.Thread(target=self.downloadAction)
        t.start()

    # Only to be called from downloadPress()
    def downloadAction(self):
        # Updates status bar -> updates config file -> updates ytdlOptions -> downloads video/audio -> update status bar
        self.statusBar.set("Downloading...")
        self.updateAllConfigFile()
        self.updateOptionDictionary()
        with youtube_dl.YoutubeDL(self.ytdlOptions) as ytdler:
            ytdler.download([self.linkEntry.get()])
        self.statusBar.set("Done!")
        time.sleep(10)
        self.statusBar.set("Waiting...")

    # Switch modes
    def basicPress(self):
        pass

    def averagePress(self):
        pass

    def advancedPress(self):
        pass

    def aboutPress(self):
        webbrowser.open(r"https://github.com/meantimetofailure/youtube-dl_GUI")

    # Updates ytdlOptions.
    def updateOptionDictionary(self):
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")
        # path and filename option
        self.ytdlOptions["outtmpl"] = config["Options"]["path"] + config["Options"]["nameformat"]

        # Audio Only Option
        if self.optionAudio.get():  # If 'Audio Only' is Checked
            self.ytdlOptions["format"] = "bestaudio[ext=m4a]/best"
            self.ytdlOptions["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                                  "preferredcodec": "mp3",
                                                  "preferredquality": "192"}]
        else:
            self.ytdlOptions["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
            if "postprocessors" in self.ytdlOptions.keys():
                del self.ytdlOptions["postprocessors"]

    # Create default config file if it doesn't exist
    def createDefaultConfig(self):
        if os.path.isfile(os.getcwd() + "\config.ini"):
            pass
        else:
            config = configparser.RawConfigParser()
            config["Options"] = {"path": os.getcwd(),
                                 "nameformat": "\%(title)s.%(ext)s",
                                 "audioonly": False,
                                 }

            with open("config.ini", "w") as configfile:
                config.write(configfile)

    # Update all settings in config.ini
    def updateAllConfigFile(self):
        self.updateConfigFile("Options", "path", self.defaultPath.get())
        self.updateConfigFile("Options", "audioonly", str(self.optionAudio.get()))

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

