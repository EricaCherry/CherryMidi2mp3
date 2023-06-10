import os
import configparser
from midi2audio import FluidSynth
from tkinter import filedialog
from tkinter import Tk
from pydub import AudioSegment
import pretty_midi

# Create a ConfigParser object
config = configparser.ConfigParser()

# Try to read the config file
config.read('config.ini')

# If the config file exists and has an initial_dir setting, use it
if config.has_option('DEFAULT', 'initial_dir_soundfont'):
    initial_dir_soundfont = config['DEFAULT']['initial_dir_soundfont']
else:
    # Otherwise, use the user's desktop directory and write it to the config file
    initial_dir_soundfont = os.path.join(os.path.expanduser('~'), 'Desktop')
    config['DEFAULT']['initial_dir_soundfont'] = initial_dir_soundfont

if config.has_option('DEFAULT', 'initial_dir_midi'):
    initial_dir_midi = config['DEFAULT']['initial_dir_midi']
else:
    # Otherwise, use the user's desktop directory and write it to the config file
    initial_dir_midi = os.path.join(os.path.expanduser('~'), 'Desktop')
    config['DEFAULT']['initial_dir_midi'] = initial_dir_midi

with open('config.ini', 'w') as configfile:
    config.write(configfile)

def increase_velocity(midi_file_path, increase_amount=20):
    # Load the MIDI file
    mid = pretty_midi.PrettyMIDI(midi_file_path)

    # Iterate over all instruments and notes
    for instrument in mid.instruments:
        for note in instrument.notes:
            # Increase velocity by specified amount, but don't exceed max velocity (127)
            note.velocity = min(note.velocity + increase_amount, 127)

    # Save the modified MIDI file
    output_file_path = midi_file_path.replace('.midi', '_boosted.midi').replace('.mid', '_boosted.mid')
    mid.write(output_file_path)

    return output_file_path, mid.get_end_time()  # return end time of midi file

def main():
    root = Tk()
    root.withdraw()

    sound_font = filedialog.askopenfilename(initialdir = initial_dir_soundfont, title='Please choose a soundfont:')
    midi_file = filedialog.askopenfilename(initialdir = initial_dir_midi, title='Please choose a MIDI file:')

    # Increase the velocity of all notes in the MIDI file
    boosted_midi_file, end_time = increase_velocity(midi_file, increase_amount=20)

    fs = FluidSynth(sound_font)
    fs.midi_to_audio(boosted_midi_file, 'output.wav')

    # Get the original filename without extension
    original_filename = os.path.splitext(os.path.basename(midi_file))[0]
    output_filename = f"{original_filename}_CherryMidiRender.mp3"

    # Load audio file and cut silence at the end according to end_time of MIDI
    sound = AudioSegment.from_wav("output.wav")
    sound = sound[:end_time*1000]  # multiply by 1000 to convert seconds to milliseconds

    sound.export(output_filename, format="mp3")

    # Delete intermediary files
    os.remove("output.wav")
    os.remove(boosted_midi_file)

if __name__ == "__main__":
    main()
