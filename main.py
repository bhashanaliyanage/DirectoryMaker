import csv
import os
import queue
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, HORIZONTAL, DISABLED, messagebox
from tkinter import ttk, font
import tkinter.simpledialog

import sv_ttk
from ttkthemes import ThemedTk

# Main Window
root = ThemedTk()
root.title("Bulk Ingestion - Directory Maker v1.2")
root.geometry("500x350")
root.resizable(False, False)
root.configure()
root.set_theme("black")
mainFrame = ttk.Frame(root, style='Card.TFrame', padding=(5, 6, 7, 8))
mainFrame.pack(pady=20)
progressFrame = ttk.Frame(root)
progressFrame.pack()
submitFrame = ttk.Frame(root)
submitFrame.pack()


# File Picker
class FilePickerWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.frame_main = ttk.Frame(self)
        self.location = ttk.Entry(self.frame_main)
        self.frame_main.pack(fill=tk.BOTH, expand=True)
        self.location.pack()


sv_ttk.set_theme("light")

q = queue.Queue()
error_messages = queue.Queue()

# Define a global variable that stores the flag value
global stop_flag
# Initialize it to False
stop_flag = False

print(font.families())

# Labels
lblSelectCSV = ttk.Label(mainFrame, text="Select CSV:", padding=20, width=40)
lblSelectFilePath = ttk.Label(mainFrame, text="Select Audio File Location:", padding=20, width=40)
lblSelectImagePath = ttk.Label(mainFrame, text="Select Artwork:", padding=20, width=40)
progressBar = ttk.Progressbar(progressFrame, orient=HORIZONTAL, length=440, mode='determinate', value=0)
lblProgress = ttk.Label(progressFrame, text="0.00%", padding=20)

csv_file = None
audio_location = None
image_file = None


def get_csv():
    global csv_file
    global lblSelectCSV
    file_path = filedialog.askopenfilename(title="Select a CSV file")
    csv_file = file_path
    if file_path != "":
        file_name = file_path.split("/")[-1]
        lblSelectCSV.config(text=file_name)
        print(file_name)


def get_audios():
    global audio_location
    global lblSelectFilePath
    folder_path = filedialog.askdirectory(title="Browse for audios")
    audio_location = folder_path
    if folder_path != "":
        last_40 = folder_path[-35:]
        first_3 = folder_path[:3]
        print(first_3)
        lblSelectFilePath.config(text=first_3 + ".../" + last_40)
        # lblSelectFilePath.config(text=folder_path)


def get_image():
    global image_file
    global lblSelectImagePath
    image_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", ".jpg .png .gif")])
    image_file = image_path
    if image_path != "":
        last_40 = image_path[-35:]
        first_3 = image_path[:3]
        lblSelectImagePath.config(text=first_3 + ".../" + last_40)


def get_missing_file():
    pass
    # global image_file
    # global lblSelectImagePath
    # image_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", ".jpg .png .gif")])
    # image_file = image_path
    # if image_path != "":
    #     last_40 = image_path[-35:]
    #     first_3 = image_path[:3]
    #     lblSelectImagePath.config(text=first_3 + ".../" + last_40)


def update_gui():
    if not q.empty():
        progress = q.get()
        progressBar.config(value=progress)
        # lblProgress.config(text=f"Progress: {progress:.2f}%")
    root.after(100, update_gui)


def check_error_messages():
    while not error_messages.empty():
        error_message = error_messages.get()
        messagebox.showerror(title='Error', message=error_message)
    root.after(100, check_error_messages)


def mfunc():
    global csv_file
    global audio_location
    global image_file

    # check if csv_file is not empty
    if not csv_file:
        print("csv_file is empty")
        btnSelectCSV.focus()
        lblSelectCSV.config(text="Select CSV: *required")
        return  # exit the function

    # check if audio_location is not empty
    if not audio_location:
        print("audio_location is empty")
        lblSelectFilePath.config(text="Select Audio File Location: *required")
        return  # exit the function

    # check if image_file is not empty
    if not image_file:
        print("image_file is empty")
        lblSelectImagePath.config(text="Select Artwork: *required")
        return  # exit the function

    # Open CSV file and reading
    with open(csv_file) as csvfile:
        btnSelectCSV.config(state=tk.DISABLED)
        btnSelectFilePath.config(state=tk.DISABLED)
        btnSelectImagePath.config(state=tk.DISABLED)
        btnProceed.config(state=tk.DISABLED)
        btnStop.config(state=tk.ACTIVE)
        read_csv = csv.reader(csvfile, delimiter=',')
        next(read_csv)  # skip header row
        num_rows = 0

        for row in read_csv:
            num_rows += 1
        csvfile.seek(0)
        next(read_csv)  # skip header row

        # Iterating over rows in the CSV
        for i, row in enumerate(read_csv):
            if stop_flag:
                # If it is True, break out of the loop and stop the function
                break
            dir_name = row[3]

            # Making the directories
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Executed Directory: " + dir_name)
            filename = row[55]
            src_file = os.path.join(audio_location, filename)
            dst_file = os.path.join(dir_name, filename)

            if os.path.exists(src_file):
                shutil.copy(src_file, dst_file)
            else:
                print(f"The file {src_file} does not exist.")
                get_missing_file()  # Implement This

            dir_name_last = os.path.basename(dir_name)
            image_file_new = os.path.join(dir_name, dir_name_last + os.path.splitext(image_file)[1])
            shutil.copy(image_file, image_file_new)
            print(image_file + " | " + dir_name)
            progress = (i + 1) / num_rows * 100
            print(f"Progress: {progress:.2f}%")
            q.put(progress)
            print("Copied " + filename + " to " + dir_name + "\n")

    btnSelectCSV.config(state=tk.ACTIVE)
    btnSelectFilePath.config(state=tk.ACTIVE)
    btnSelectImagePath.config(state=tk.ACTIVE)
    btnProceed.config(state=tk.ACTIVE)
    btnStop.config(state=tk.DISABLED)
    print("Execution completed")


def start_main():
    global t
    t = threading.Thread(target=mfunc)
    t.start()
    update_gui()
    check_error_messages()


def stop_main():
    # Define a global variable that stores the flag value
    global stop_flag
    # Set it to True when the user clicks the stop button
    stop_flag = True


# Buttons
btnSelectCSV = ttk.Button(mainFrame, text="Browse", command=get_csv, padding=10)
btnSelectFilePath = ttk.Button(mainFrame, text="Browse", command=get_audios, padding=10)
btnSelectImagePath = ttk.Button(mainFrame, text="Browse", command=get_image, padding=10)
btnProceed = ttk.Button(submitFrame, text="Proceed", style='Accent.TButton', command=start_main, padding=10)
btnStop = ttk.Button(submitFrame, text="Stop", command=stop_main, padding=10, state=DISABLED)

# Arranging UI Elements to main window
lblSelectCSV.grid(row=0, column=0, sticky="w")
lblSelectFilePath.grid(row=1, column=0, sticky="w")
lblSelectImagePath.grid(row=2, column=0, sticky="w")
btnSelectCSV.grid(row=0, column=1)
btnSelectFilePath.grid(row=1, column=1)
btnSelectImagePath.grid(row=2, column=1)
btnProceed.grid(row=3, column=0)
btnStop.grid(row=3, column=1, padx=10)
progressBar.grid(pady=30)

root.mainloop()
