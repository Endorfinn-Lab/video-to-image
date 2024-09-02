import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
from skimage.metrics import structural_similarity as ssim

def extract_frames(video_path, output_folder, progress_bar, progress_label, remove_duplicates=False):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Error opening video file.")
        return

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    previous_frame = None

    while True:
        ret, frame = video.read()

        if not ret:
            break

        if remove_duplicates and previous_frame is not None:
            gray_previous = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
            gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            similarity = ssim(gray_previous, gray_current)

            if similarity > 0.95:  # Adjust threshold as needed
                frame_count += 1
                continue

        output_path = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(output_path, frame)

        progress = (frame_count + 1) / total_frames * 100
        progress_bar["value"] = progress
        progress_label.config(text=f"{progress:.2f}%")
        progress_bar.update()

        frame_count += 1
        previous_frame = frame

    video.release()

    subprocess.Popen(f'explorer "{output_folder}"')

    progress_bar.grid_forget()
    progress_label.grid_forget()

    print(f"Extracted {frame_count} frames to {output_folder}")


def browse_video():
    filename = filedialog.askopenfilename(initialdir="/", title="Select a Video File",
                                          filetypes=(("Video Files", "*.mp4 *.avi *.mkv"), ("All Files", "*.*")))
    if filename:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, filename)


def start_extraction():
    video_path = video_path_entry.get()

    video_title = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join("extracted_frames", video_title)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=2, column=0, columnspan=3, pady=5)

    progress_label = tk.Label(root, text="0.00%")
    progress_label.grid(row=3, column=1, pady=5)

    remove_duplicates = remove_duplicates_var.get()

    extract_frames(video_path, output_folder, progress_bar, progress_label, remove_duplicates)


# --- GUI ---
root = tk.Tk()
root.title("Video Frame Extractor")

video_path_label = tk.Label(root, text="Video Path:")
video_path_label.grid(row=0, column=0, padx=5, pady=5)

video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_video)
browse_button.grid(row=0, column=2, padx=5, pady=5)

remove_duplicates_var = tk.BooleanVar(value=False)
remove_duplicates_checkbox = tk.Checkbutton(root, text="Remove Duplicate Frames", variable=remove_duplicates_var)
remove_duplicates_checkbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

start_button = tk.Button(root, text="Start Extraction", command=start_extraction)
start_button.grid(row=1, column=2, padx=5, pady=5)

root.mainloop()
