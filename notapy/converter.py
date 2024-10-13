import os
import pandas as pd
import music21

# Directories
DATA_INPUT_MIDI = "data/input-midi"
DATA_OUTPUT_CSV = "data/output-csv"
DATA_OUTPUT_MIDI = "data/output-midi"


def midi_to_csv(midi_file_path, output_csv_path):
    """
    Convert a MIDI file to a CSV file containing note information.

    Args:
        midi_file_path (str): Path to the input MIDI file.
        output_csv_path (str): Path to save the output CSV file.
    """
    # Load the MIDI file using music21
    midi_file = music21.midi.MidiFile()
    midi_file.open(midi_file_path)
    midi_file.read()
    midi_file.close()

    # Convert the MIDI file to a music21 Stream
    stream = music21.midi.translate.midiFileToStream(midi_file, quantizePost=False).flat

    # Create a DataFrame to store note data
    df = pd.DataFrame(columns=["note_name", "start_time", "duration", "velocity", "tempo"])

    # Assume only one tempo for simplicity
    note_tempo = stream.metronomeMarkBoundaries()[0][2].number if stream.metronomeMarkBoundaries() else 120

    # Process each note in the stream
    for element in stream.recurse().notes:
        if element.isNote:
            new_row = {
                "note_name": element.nameWithOctave,
                "start_time": round(float(element.offset), 3),
                "duration": round(element.duration.quarterLength, 3),
                "velocity": element.volume.velocity,
                "tempo": note_tempo
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save DataFrame to CSV
    df.to_csv(output_csv_path, index=False)
    print(f"MIDI to CSV conversion complete: {output_csv_path}")


def csv_to_midi(csv_file_path, output_midi_path):
    """
    Convert a CSV file containing note information back to a MIDI file.

    Args:
        csv_file_path (str): Path to the input CSV file.
        output_midi_path (str): Path to save the output MIDI file.
    """
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    stream = music21.stream.Stream()

    # Set the tempo from the CSV data (assuming it's consistent throughout)
    if not df.empty:
        desired_tempo = df.iloc[0]['tempo']
        mm = music21.tempo.MetronomeMark(number=desired_tempo)
        stream.append(mm)

    # Add notes to the music21 stream
    for _, row in df.iterrows():
        note_name = row['note_name']
        start_time = row['start_time']
        duration = row['duration']
        velocity = row['velocity']

        note = music21.note.Note(note_name, duration=music21.duration.Duration(duration))
        note.volume.velocity = velocity
        note.offset = start_time
        stream.insert(note)

    # Write the music21 stream to a MIDI file
    stream.write('midi', output_midi_path)
    print(f"CSV to MIDI conversion complete: {output_midi_path}")


def combine_midis(midi_file_paths, output_midi_path):
    """
    Combine multiple MIDI files into a single MIDI file.

    Args:
        midi_file_paths (list of str): List of paths to the input MIDI files.
        output_midi_path (str): Path to save the combined MIDI file.
    """
    combined_stream = music21.stream.Stream()

    for midi_file_path in midi_file_paths:
        # Load each MIDI file using music21
        midi_file = music21.midi.MidiFile()
        midi_file.open(midi_file_path)
        midi_file.read()
        midi_file.close()

        # Convert the MIDI file to a stream and append it to the combined stream
        stream = music21.midi.translate.midiFileToStream(midi_file, quantizePost=False).flat
        combined_stream.append(stream)

    # Write the combined stream to a MIDI file
    combined_stream.write('midi', output_midi_path)
    print(f"MIDI file created: {output_midi_path}")


def ensure_directories_exist():
    """
    Ensure that the output directories exist.
    """
    os.makedirs(DATA_OUTPUT_CSV, exist_ok=True)
    os.makedirs(DATA_OUTPUT_MIDI, exist_ok=True)


def convert_midi_to_csv(midi_file_path, output_csv_path):
    """
    Public method to convert a MIDI file to a CSV.

    Args:
        midi_file_path (str): Path to the input MIDI file.
        output_csv_path (str): Path to save the output CSV file.
    """
    midi_to_csv(midi_file_path, output_csv_path)


def convert_csv_to_midi(csv_file_path, output_midi_path):
    """
    Public method to convert a CSV file to a MIDI.

    Args:
        csv_file_path (str): Path to the input CSV file.
        output_midi_path (str): Path to save the output MIDI file.
    """
    csv_to_midi(csv_file_path, output_midi_path)


def convert_and_combine_midi_files(input_midi_files, combined_midi_output_path):
    """
    Convert multiple MIDI files to CSVs and combine them into a single MIDI file.

    Args:
        input_midi_files (list of str): List of input MIDI file paths.
        combined_midi_output_path (str): Path to save the combined MIDI file.
    """
    # Convert each MIDI to CSV
    for midi_file in input_midi_files:
        csv_path = os.path.join(DATA_OUTPUT_CSV, os.path.basename(midi_file).replace('.mid', '.csv'))
        midi_to_csv(midi_file, csv_path)

    # Combine the MIDI files into one
    combine_midis(input_midi_files, combined_midi_output_path)


# If running as a standalone script
if __name__ == "__main__":
    # Ensure output directories exist
    ensure_directories_exist()

    # Example usage
    input_midis = [
        os.path.join(DATA_INPUT_MIDI, midi_file) for midi_file in os.listdir(DATA_INPUT_MIDI) if
        midi_file.endswith('.mid')
    ]
    if len(input_midis) >= 2:
        combined_midi_path = os.path.join(DATA_OUTPUT_MIDI, 'final_recreated_combined.mid')
        convert_and_combine_midi_files(input_midis[:2], combined_midi_path)