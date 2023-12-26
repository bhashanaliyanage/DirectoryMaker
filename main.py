import csv
import glob
import os
import queue
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, HORIZONTAL, DISABLED, messagebox
from tkinter import ttk

import sv_ttk
from ttkthemes import ThemedTk

# Main Window
root = ThemedTk()
root.title("Bulk Ingestion - Directory Maker v1.2")
root.geometry("500x450")
root.resizable(False, False)
root.configure()
root.set_theme("black")
mainFrame = ttk.Frame(root, style='Card.TFrame', padding=(5, 6, 7, 8))
mainFrame.pack(pady=20)
progressFrame = ttk.Frame(root)
progressFrame.pack()
submitFrame = ttk.Frame(root)
submitFrame.pack()

sv_ttk.set_theme("light")

q = queue.Queue()
error_messages = queue.Queue()
r = tk.IntVar()

# Define a global variable that stores the flag value
global stop_flag
stop_flag = False

# Labels
lblSelectCSV = ttk.Label(mainFrame, text="Select CSV:", padding=20, width=40)
lblSelectFilePath = ttk.Label(mainFrame, text="Select Audio File Location:", padding=20, width=40)
lblSelectImagePath = ttk.Label(mainFrame, text="Select Artwork:", padding=20, width=40)
progressBar = ttk.Progressbar(progressFrame, orient=HORIZONTAL, length=440, mode='determinate', value=0)
lblProgress = ttk.Label(progressFrame, text="0.00%", padding=20)

csv_file: os.PathLike
audio_location: os.PathLike
image_file = None
image_file_location: os.PathLike


def get_csv():
    global csv_file
    global lblSelectCSV
    file_path = filedialog.askopenfilename(title="Select a CSV file")
    csv_file = file_path
    if file_path != "":
        file_name = file_path.split("/")[-1]
        lblSelectCSV.config(text=file_name)
        print(file_name)


def get_audios(name):
    global audio_location
    global lblSelectFilePath
    folder_path = filedialog.askdirectory(title=name)
    audio_location = folder_path
    if folder_path != "":
        last_40 = folder_path[-35:]
        first_3 = folder_path[:3]
        print(first_3)
        lblSelectFilePath.config(text=first_3 + ".../" + last_40)
        # lblSelectFilePath.config(text=folder_path)


def get_image(name):
    global image_file
    global lblSelectImagePath
    image_path = filedialog.askopenfilename(title=name, filetypes=[("Image files", ".jpg .png .gif")])
    image_file = image_path
    if image_path != "":
        last_40 = image_path[-35:]
        first_3 = image_path[:3]
        lblSelectImagePath.config(text=first_3 + ".../" + last_40)


def get_image_location():
    global image_file_location
    folder_path = filedialog.askdirectory(title="Select Artwork Directory")
    image_file_location = folder_path


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


def main_func():
    # check if csv_file is not empty
    if not csv_file:
        print("csv_file is empty")
        btn_select_csv.focus()
        lblSelectCSV.config(text="Select CSV: *required")
        return  # exit the function

    # check if audio_location is not empty
    if not audio_location:
        print("audio_location is empty")
        lblSelectFilePath.config(text="Select Audio File Location: *required")
        return  # exit the function

    print(r.get())

    if r.get() == 1:
        # check if image_file is not empty
        if not image_file:
            print("image_file is empty")
            btn_single_image.config(text="N/A")
            return  # exit the function
    elif r.get() == 2:
        if not image_file_location:
            print("Image File Location Empty")
            btn_multiple_images.config(text="N/A")
            return
    else:
        btn_single_image.config(text="N/A")
        btn_multiple_images.config(text="N/A")
        return

    # Open CSV file and reading
    with open(csv_file) as csv_document:
        disable_buttons()

        read_csv = csv.reader(csv_document, delimiter=',')
        next(read_csv)  # skip header row
        num_rows = 0

        for row in read_csv:
            num_rows += 1
        csv_document.seek(0)
        next(read_csv)  # skip header row

        # Iterating over rows in the CSV
        for i, row in enumerate(read_csv):
            if stop_flag:
                # If it is True, break out of the loop and stop the function
                break
            # UPC
            dir_name = row[3]
            # Catalog Number
            image_name = row[4]

            # Making the directories
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Executed Directory: " + dir_name)
            filename = row[55]
            src_file = os.path.join(audio_location, filename)
            selected_file_name = os.path.basename(src_file)
            dst_file = os.path.join(dir_name, filename)

            if os.path.exists(src_file):
                shutil.copy(src_file, dst_file)
            else:
                print(f"The file {src_file} does not exist.")
                get_audios(selected_file_name)  # Implement This
                src_file = os.path.join(audio_location, filename)
                shutil.copy(src_file, dst_file)

            dir_name_last = os.path.basename(dir_name)
            copy_image(dir_name, dir_name_last, image_file, image_name)
            progress = (i + 1) / num_rows * 100
            print(f"Progress: {progress:.2f}%")
            q.put(progress)
            print("Copied " + filename + " to " + dir_name + "\n")

    enable_buttons()
    print("Execution completed")


def copy_image(dir_name, dir_name_last, src_image, image_name):
    if r.get() == 1:
        image_file_new = os.path.join(dir_name, dir_name_last + os.path.splitext(src_image)[1])
        shutil.copy(src_image, image_file_new)
        print(src_image + " | " + dir_name)
    if r.get() == 2:
        image_file_new = glob.glob(os.path.join(image_file_location, f"{image_name}.*"))
        if len(image_file_new) > 0:
            print(f"{image_name} exists in {image_file_location}.")
            extension = os.path.splitext(image_file_new[0])[1]
            shutil.copy(image_file_new[0], os.path.join(dir_name, dir_name_last + extension))
        else:
            print(f"{image_name} does not exist in {image_file_location}.")
            get_image(image_name)
            image_file_new = os.path.join(dir_name, dir_name_last + os.path.splitext(image_file)[1])
            shutil.copy(image_file, image_file_new)
            print(image_file + " | " + dir_name)


def enable_buttons():
    btn_select_csv.config(state=tk.ACTIVE)
    btn_select_file_path.config(state=tk.ACTIVE)
    btn_single_image.config(state=tk.ACTIVE)
    btn_proceed.config(state=tk.ACTIVE)
    btn_stop.config(state=tk.DISABLED)


def disable_buttons():
    btn_select_csv.config(state=tk.DISABLED)
    btn_select_file_path.config(state=tk.DISABLED)
    btn_single_image.config(state=tk.DISABLED)
    btn_proceed.config(state=tk.DISABLED)
    btn_stop.config(state=tk.ACTIVE)


def start_main():
    global t
    t = threading.Thread(target=main_func)
    t.start()
    update_gui()
    check_error_messages()


def stop_main():
    # Define a global variable that stores the flag value
    global stop_flag
    # Set it to True when the user clicks the stop button
    stop_flag = True


# Buttons
btn_select_csv = ttk.Button(mainFrame, text="Browse", command=get_csv, padding=10)
btn_select_file_path = ttk.Button(mainFrame, text="Browse", command=lambda: get_audios("Browse for Audios"), padding=10)
btn_single_image = ttk.Button(mainFrame, text="Browse", command=lambda: get_image("Browse for Image"), padding=10,
                              state=DISABLED)
btn_multiple_images = ttk.Button(mainFrame, text="Browse", command=get_image_location, padding=10, state=DISABLED)
btn_proceed = ttk.Button(submitFrame, text="Proceed", style='Accent.TButton', command=start_main, padding=10)
btn_stop = ttk.Button(submitFrame, text="Stop", command=stop_main, padding=10, state=DISABLED)


def rb_clicked(value):
    btn_single_image.config(state=tk.DISABLED)
    btn_multiple_images.config(state=tk.DISABLED)
    if value == 1:
        btn_single_image.config(state=tk.ACTIVE)
    else:
        btn_multiple_images.config(state=tk.ACTIVE)


# Radio Buttons
rb_single = ttk.Radiobutton(mainFrame, text="Single Image", variable=r, value=1, padding=20,
                            command=lambda: rb_clicked(r.get()))
rb_multiple = ttk.Radiobutton(mainFrame, text="Multiple Images", variable=r, value=2, padding=20,
                              command=lambda: rb_clicked(r.get()))

# Arranging UI Elements to main window
lblSelectCSV.grid(row=0, column=0, sticky="w")
lblSelectFilePath.grid(row=1, column=0, sticky="w")
rb_single.grid(row=2, column=0, sticky="w")
rb_multiple.grid(row=3, column=0, sticky="w")

btn_select_csv.grid(row=0, column=1)
btn_select_file_path.grid(row=1, column=1)
btn_single_image.grid(row=2, column=1)
btn_multiple_images.grid(row=3, column=1)

btn_proceed.grid(row=3, column=0)
btn_stop.grid(row=3, column=1, padx=10)
progressBar.grid(pady=30)

root.mainloop()
