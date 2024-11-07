import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog, font
from pydub import AudioSegment, playback
import pygame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # To handle main logo png file

# Initialize pygame's mixer for audio playback to accompany grapph
try:
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.8)  # Set to a moderate volume level
except Exception as e:
    print(f"Error initializing pygame.mixer: {e}") #In case error occurs

# Set up tkinter window - Seperate page w/ buttons and graphic
root = tk.Tk()
root.title("Project Beatviz - Reactive Audio Oscillogram")

# Set to Monsterrat Font
custom_font = font.Font(family="Montserrat", size=10, weight="bold")

# Create a frame for the logo
logo_frame = tk.Frame(root)
logo_frame.pack(pady=10)  # Pad around it & centre

# Load and display the logo
try:
    logo_image = Image.open("Project Beatviz.png") 
    logo_image = logo_image.resize((200, 100), Image.LANCZOS)  
    #Frame Correctly
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(logo_frame, image=logo_photo)
    logo_label.image = logo_photo  
    logo_label.pack()
except Exception as e:
    print(f"Error loading logo: {e}")

# Set up matplotlib figure for the oscillogram
fig, ax = plt.subplots(figsize=(10, 4))

# Global variables
current_data = None
current_sr = None
is_playing = False

def plot_oscillogram(data, sr):
    """Initial plot setup for the oscillogram."""
    global current_data, current_sr
    current_data = data
    current_sr = sr
    ax.clear()
    ax.plot(np.linspace(0, len(data) / sr, num=len(data)), data, color="cornflowerblue")

    # Set axis limits
    ax.set_xlim(0, len(data) / sr)
    ax.set_ylim(-max(abs(data)), max(abs(data)))

    # Set x and y axis labels
    ax.set_xlabel("Time (s)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Amplitude", fontsize=12, fontweight='bold')

    fig.canvas.draw()

def update_visualizer():
    """Updates the visualizer to synchronize with audio playback."""
    global is_playing, current_data, current_sr

    if is_playing and current_data is not None:
        playback_position = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
        samples_to_display = int(playback_position * current_sr)

        # Sliding waves 
        window_size = current_sr // 2  # Half-second window
        start = max(0, samples_to_display - window_size)
        end = start + window_size

        ax.clear()
        ax.plot(np.linspace(start / current_sr, end / current_sr, num=end - start), 
                current_data[start:end], color="cornflowerblue")
        # Contrasts background, logo & text

        # Set limits to the axis'
        ax.set_xlim(start / current_sr, end / current_sr)
        ax.set_ylim(-max(abs(current_data)), max(abs(current_data)))

        # Set x and y axis labels
        ax.set_xlabel("Time (s)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Amplitude (hz)", fontsize=12, fontweight='bold')

        fig.canvas.draw()

        # Stop updating if playback is done
        if not pygame.mixer.music.get_busy():
            is_playing = False

    root.after(50, update_visualizer)  # Update every 50 ms

def load_audio_file():
    """Load an audio file, display the oscillogram, and start synchronized playback."""
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if file_path:
        audio, sr = process_audio(file_path)
        plot_oscillogram(audio, sr)

        # Attempt playback with pygame first
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            global is_playing
            is_playing = True
        except Exception as e:
            print(f"Pygame playback failed: {e}. Trying alternative playback.")
            playback.play(audio)  # Alternative if pygame playback fails

def play_example_track():
    """Play an example audio track and display the oscillogram."""
    file_path = "R&B Example.wav"
    audio, sr = process_audio(file_path)
    plot_oscillogram(audio, sr)

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        global is_playing
        is_playing = True
    except Exception as e:
        print(f"Pygame playback failed: {e}. Trying alternative playback.")
        playback.play(audio)

def process_audio(file_path):
    """Processes the audio file for plotting the oscillogram."""
    audio_segment = AudioSegment.from_file(file_path)
    samples = np.array(audio_segment.get_array_of_samples())
    sr = audio_segment.frame_rate
    return samples, sr

# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Select a track button
select_button = tk.Button(button_frame, text="Choose Track", command=load_audio_file, font=custom_font)
select_button.pack(side=tk.LEFT, padx=5)

# Play example track button
example_button = tk.Button(button_frame, text="Play Example Track", command=play_example_track, font=custom_font)
example_button.pack(side=tk.LEFT, padx=5)

# Embed matplotlib plot in tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()  # Correct way to pack the canvas

# Start updating visualizer
update_visualizer()

# Run the tkinter main loop
root.mainloop()
pygame.quit()