#Main code in which user input and Gui is handled

from tasks import download_video
from tkinter import *
import threading

def start_download():
    video_url = url_entry.get()
    quality_choice = quality_var.get()
    status_label.config(text="Download started...")
    
    def task():
        result = download_video.delay(video_url, quality_choice)
        while not result.ready():
            root.update()
        
        status_label.config(text=result.get())
        
    threading.Thread(target=task).start()
        
#GUI setup
root = Tk() 
root.title("🎥V-Down | Video Downloader")
root.geometry("400x250")

Label(root, text="Enter Video URL:").pack(pady=5)
url_entry = Entry(root, width=50)
url_entry.pack(pady=5)

Label(root, text="Select Quality:").pack(pady=5)    
quality_var = StringVar(value='1')
for text, value in [("Best Quality (1080p or higher)", '1'),
                    ("720p", '2'),
                    ("480p", '3'),
                    ("360p", '4')]:
    Radiobutton(root, text=text, variable=quality_var, value=value).pack(anchor='w')
    
Button(root, text="Download", command=start_download).pack(pady=10)
status_label = Label(root, text="")
status_label.pack(pady=10)

root.mainloop()