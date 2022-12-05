from tkinter import *
#from tkinter import PhotoImage, Canvas, Scrollbar
from datetime import datetime
from os.path import getmtime, join, isfile, getsize
from PIL import Image
import os

class Row:
    def __init__(self, name, row, path) -> None:
        self.container = Frame(filesFrame, width=685, height=30)
        self.container.grid(row=row, column=0, pady=1)
        self.container.grid_propagate(False)
        self.container.grid_rowconfigure(0, weight=1)

        self.iconLabel = Label(self.container, text=None, image=self.icon)
        self.iconLabel.photo = self.icon
        self.iconLabel.place(x=13, rely=0.5, anchor=CENTER)

        self.nameLabel = Label(self.container, text=name, width=150, height=30, anchor="w", fg="black")
        self.nameLabel.place(x=30, y=0)

        self.size = getsize(join(path, name))

        if self.size < 1000: self.size = str(round(self.size, 1)) + "B"
        elif self.size < 100000: self.size = str(round(self.size/1000, 1)) + "KB"
        elif self.size < 10000000: self.size = str(round(self.size/1000000, 1)) + "MB"
        else: self.size = str(round(self.size/1000000000, 1)) + "GB"

        self.sizeLabel = Label(self.container, text=self.size, height=30)
        self.sizeLabel.place(x=200, y=0)

        self.typeLabel = Label(self.container, text=self.type, height=30)
        self.typeLabel.place(x=400, y=0)

        self.lastModLabel = Label(self.container, anchor="w", height=30, text=str(datetime.fromtimestamp(getmtime(join(path, name)))).split(".")[0])
        self.lastModLabel.place(x=550, y=0)

    def delete(self):
        self.container.grid_forget()

class File(Row):
    def __init__(self, name, row, path) -> None:
        self.icon = PhotoImage(file="file.png").subsample(12)
        self.type = name.split(".")[-1]
        super().__init__(name, row, path)

# class File(Row):
#     def __init__(self, name, row, path) -> None:
#         im = Image.open("file.png")
#         im.resize((20, 40), Image.Resampling.LANCZOS)
#         self.icon = Image(im)
#         super().__init__(name, row, path)    

class Directory(Row):
    def __init__(self, name, row, path) -> None:
        self.icon = PhotoImage(file="folder.png").subsample(12)
        self.type = "directory"
        super().__init__(name, row, path)

def on_config(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def scroll(event):
    if event.num == 4:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")


tk = Tk()
tk.geometry("700x300")
canvas = Canvas(tk, bg="#2b2b2b", width=685, height=300, bd=0, highlightthickness=0, relief='ridge')
canvas.pack(side=LEFT)

tk.attributes("-zoomed", True)
sb = Scrollbar(tk, command=canvas.yview)
sb.pack(side=LEFT, fill="y")
tk.attributes("-zoomed", False)

print(sb.winfo_height())
canvas.configure(yscrollcommand=sb.set)
canvas.bind("<Configure>", on_config)
tk.bind_all("<Button-4>", scroll)
tk.bind_all("<Button-5>", scroll)
filesFrame = Frame(canvas)
canvas.create_window((0,0), window=filesFrame, anchor='nw')


row = 1
files = [file for file in os.listdir("/home/james/gui_chat/") if isfile(join("/home/james/gui_chat/", file))]
files.sort()
dirs = [directory for directory in os.listdir("/home/james/gui_chat/") if not isfile(join("/home/james/gui_chat/", directory))]
dirs.sort()
for directory in dirs:
    if directory[0] != ".":
        Directory(directory, row, "/home/james/gui_chat/")
        row += 1
for file in files:
    if file[0] != ".":
        File(file, row, "/home/james/gui_chat/")
        row += 1
tk.mainloop()
