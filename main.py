import os
import csv
import queue
import shutil
import threading
from tkinter import filedialog
from tkinter import *

# Main Window
root = Tk()
# root.withdraw()

q = queue.Queue()

# Labels
lblSelectCSV = Label(root, text="Select CSV:", padx=10, pady=10)
lblSelectFilePath = Label(root, text="Select File Location:", padx=10, pady=10)
lblSelectImagePath = Label(root, text="Select Image:", padx=10, pady=10)
lblProgress = Label(root, text="", padx=10, pady=10)

csv_file = None
audio_location = None
image_file = None


def get_csv():
    global csv_file
    global lblSelectCSV
    file_path = filedialog.askopenfilename(title="Select a CSV file")
    csv_file = file_path
    if file_path != "":
        lblSelectCSV.config(text=file_path)


def get_audios():
    global audio_location
    global lblSelectFilePath
    folder_path = filedialog.askdirectory(title="Browse for audios")
    audio_location = folder_path
    if folder_path != "":
        lblSelectFilePath.config(text=folder_path)


def get_image():
    global image_file
    global lblSelectImagePath
    image_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", ".jpg .png .gif")])
    image_file = image_path
    if image_path != "":
        lblSelectImagePath.config(text=image_path)


def update_gui():
    if not q.empty():
        progress = q.get()
        lblProgress.config(text=f"Progress: {progress:.2f}%")
    root.after(100, update_gui)


def mfunc():
    global csv_file
    global audio_location
    global image_file

    # Open CSV file and reading
    with open(csv_file) as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        next(read_csv)  # skip header row
        num_rows = 0

        for row in read_csv:
            num_rows += 1
        csvfile.seek(0)
        next(read_csv)  # skip header row

        # Iterating over rows in the CSV
        for i, row in enumerate(read_csv):
            dir_name = row[3]

            # Making the directories
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Executed Directory: " + dir_name)
            filename = row[55]
            src_file = os.path.join(audio_location, filename)
            dst_file = os.path.join(dir_name, filename)
            shutil.copy(src_file, dst_file)
            shutil.copy(image_file, dir_name)
            progress = (i + 1) / num_rows * 100
            print(f"Progress: {progress:.2f}%")
            q.put(progress)
            print("Copied " + filename + " to " + dir_name + "\n")

    print("Execution completed")


def start_main():
    global t
    t = threading.Thread(target=mfunc)
    t.start()
    update_gui()


# Buttons
btnSelectCSV = Button(root, text="Browse", padx=50, command=get_csv)
btnSelectFilePath = Button(root, text="Browse", padx=50, command=get_audios)
btnSelectImagePath = Button(root, text="Browse", padx=50, command=get_image)
btnProceed = Button(root, text="Proceed", padx=50, command=start_main)

# Arranging UI Elements to main window
lblSelectCSV.grid(row=0, column=0)
lblSelectFilePath.grid(row=1, column=0)
lblSelectImagePath.grid(row=2, column=0)
btnSelectCSV.grid(row=0, column=1)
btnSelectFilePath.grid(row=1, column=1)
btnSelectImagePath.grid(row=2, column=1)
btnProceed.grid(row=3, column=0)
lblProgress.grid(row=3, column=1)

root.mainloop()
