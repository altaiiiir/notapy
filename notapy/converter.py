import os
import pandas as pd
import music21
import logging

from music21.note import Unpitched

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directories
DATA_INPUT_MIDI = "data/input-midi"
DATA_OUTPUT_CSV = "data/output-csv"
DATA_OUTPUT_MIDI = "data/output-midi"

# Ensure output directories exist
os.makedirs(DATA_OUTPUT_CSV, exist_ok=True)
os.makedirs(DATA_OUTPUT_MIDI, exist_ok=True)


# Private functions

def _serialize_element_to_dict(element, additional_fields):
    """
    Serialize a music21 element to a dictionary.

    Args:
        element (music21.note.Note): The music21 element to serialize.
        additional_fields (dict): Additional fields to include in the serialized output.

    Returns:
        dict: Serialized representation of the element.
    """
    if element.isRest:
        note_name = "Rest"
    elif element.isNote:
        note_name = element.nameWithOctave
    elif element.isChord:
        note_name = ",".join(p.nameWithOctave for p in element.pitches)
    elif isinstance(element, Unpitched):
        note_name = element.displayName
    else:
        note_name = ",".join(p.displayName for p in element.notes)

    base_fields = {
        "note_name": note_name,
        "start_time": round(float(element.offset), 3),
        "duration": round(element.duration.quarterLength, 3),
        "velocity": element.volume.velocity if hasattr(element, 'volume') else None,
    }
    return {**base_fields, **additional_fields}


def _deserialize_row_to_element(row):
    """
    Deserialize a row from a DataFrame to a music21 note, chord, or rest element.

    Args:
        row (pd.Series): The row containing note information.

    Returns:
        tuple: A tuple containing the deserialized music21 note/chord/rest and any additional fields.
    """
    if row['note_name'] == 'Rest':
        element = music21.note.Rest(quarterLength=row['duration'])
    elif "," in row['note_name']:
        pitches = [music21.pitch.Pitch(p) for p in row['note_name'].split(",")]
        element = music21.chord.Chord(pitches, duration=music21.duration.Duration(row['duration']))
    else:
        element = music21.note.Note(row['note_name'], duration=music21.duration.Duration(row['duration']))
        element.volume.velocity = row['velocity']
    element.offset = row['start_time']
    additional_fields = row.to_dict()
    return element, additional_fields


def _midi_to_csv(midi_file_path, output_csv_path):
    """
    Convert a MIDI file to a CSV file containing note information.

    Args:
        midi_file_path (str): Path to the input MIDI file.
        output_csv_path (str): Path to save the output CSV file.
    """
    try:
        midi_file = music21.midi.MidiFile()
        midi_file.open(midi_file_path)
        midi_file.read()
        midi_file.close()

        stream = music21.midi.translate.midiFileToStream(midi_file, quantizePost=False).flat

        df = pd.DataFrame(columns=["note_name", "start_time", "duration", "velocity", "tempo"])

        note_tempo = stream.metronomeMarkBoundaries()[0][2].number if stream.metronomeMarkBoundaries() else 120

        for element in stream.recurse().notesAndRests:
            # Handle notes, chords, and rests
            if not element.isStream and not element.lyric:
                additional_fields = {
                    "tempo": note_tempo,
                }
                new_row = _serialize_element_to_dict(element, additional_fields)
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        df.to_csv(output_csv_path, index=False)
        logging.info(f"MIDI to CSV conversion complete: {output_csv_path}")
    except Exception as e:
        logging.error(f"Failed to convert MIDI to CSV: {e}")


def _csv_to_midi(csv_file_path, output_midi_path):
    """
    Convert a CSV file containing note information back to a MIDI file.

    Args:
        csv_file_path (str): Path to the input CSV file.
        output_midi_path (str): Path to save the output MIDI file.
    """
    try:
        df = pd.read_csv(csv_file_path)
        stream = music21.stream.Stream()

        if not df.empty:
            desired_tempo = df.iloc[0]['tempo']
            mm = music21.tempo.MetronomeMark(number=desired_tempo)
            stream.append(mm)

        for _, row in df.iterrows():
            element, _ = _deserialize_row_to_element(row)
            stream.insert(element)

        stream.write('midi', output_midi_path)
        logging.info(f"CSV to MIDI conversion complete: {output_midi_path}")
    except Exception as e:
        logging.error(f"Failed to convert CSV to MIDI: {e}")


def _combine_midis(midi_file_paths, output_midi_path):
    """
    Combine multiple MIDI files into a single MIDI file.

    Args:
        midi_file_paths (list of str): List of paths to the input MIDI files.
        output_midi_path (str): Path to save the combined MIDI file.
    """
    try:
        combined_stream = music21.stream.Stream()

        for midi_file_path in midi_file_paths:
            try:
                midi_file = music21.midi.MidiFile()
                midi_file.open(midi_file_path)
                midi_file.read()
                midi_file.close()

                stream = music21.midi.translate.midiFileToStream(midi_file, quantizePost=False).flat
                combined_stream.append(stream)
            except Exception as e:
                logging.error(f"Failed to process MIDI file {midi_file_path}: {e}")

        combined_stream.write('midi', output_midi_path)
        logging.info(f"Combined MIDI file created: {output_midi_path}")
    except Exception as e:
        logging.error(f"Failed to combine MIDI files: {e}")


# Public functions

def midi_to_csv(input_path, output_path, combine_output=False):
    """
    Convert MIDI files to CSV files.
    This function can handle both single file and directory input modes.

    Args:
        input_path (str): Path to the input MIDI file or directory.
        output_path (str): Path to save the output CSV file or directory.
        combine_output (bool): Whether to combine all MIDI files in the input directory into one CSV (default: False).
    """
    try:
        if os.path.isdir(input_path):
            midi_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.mid')]
            for midi_file in midi_files:
                csv_output_path = os.path.join(output_path, os.path.basename(midi_file).replace('.mid', '.csv'))
                _midi_to_csv(midi_file, csv_output_path)
            if combine_output and len(midi_files) > 1:
                combined_csv_path = os.path.join(output_path, 'combined.csv')
                combined_dfs = [pd.read_csv(os.path.join(output_path, f)) for f in os.listdir(output_path) if
                                f.endswith('.csv')]
                combined_df = pd.concat(combined_dfs, ignore_index=True)
                combined_df.to_csv(combined_csv_path, index=False)
                logging.info(f"Combined CSV file created: {combined_csv_path}")
        else:
            _midi_to_csv(input_path, output_path)
    except Exception as e:
        logging.error(f"Error in midi_to_csv: {e}")


def csv_to_midi(input_path, output_path, combine_output=False):
    """
    Convert CSV files to MIDI files.
    This function can handle both single file and directory input modes.

    Args:
        input_path (str): Path to the input CSV file or directory.
        output_path (str): Path to save the output MIDI file or directory.
        combine_output (bool): Whether to combine all CSV files in the input directory into one MIDI (default: False).
    """
    try:
        if os.path.isdir(input_path):
            csv_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.csv')]
            for csv_file in csv_files:
                midi_output_path = os.path.join(output_path, os.path.basename(csv_file).replace('.csv', '.mid'))
                _csv_to_midi(csv_file, midi_output_path)
            if combine_output and len(csv_files) > 1:
                combined_midi_path = os.path.join(output_path, 'combined.mid')
                _combine_midis([os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith('.mid')],
                               combined_midi_path)
        else:
            _csv_to_midi(input_path, output_path)
    except Exception as e:
        logging.error(f"Error in csv_to_midi: {e}")


def combine_midis(input_directory, output_midi_path):
    """
    Combine multiple MIDI files from a directory into a single MIDI file.

    Args:
        input_directory (str): Path to the directory containing input MIDI files.
        output_midi_path (str): Path to save the combined MIDI file.
    """
    try:
        midi_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith('.mid')]
        _combine_midis(midi_files, output_midi_path)
    except Exception as e:
        logging.error(f"Error in combine_midis: {e}")


# Example usage (if running as a standalone script)
if __name__ == "__main__":
    try:
        # midi_to_csv("data/input-midi/test_song.mid", "data/output-csv/test_song.csv")
        # csv_to_midi("data/output-csv/test_song.csv", "data/output-midi/test_song.mid")

        midi_to_csv(DATA_INPUT_MIDI, DATA_OUTPUT_CSV, combine_output=True)
        csv_to_midi(DATA_OUTPUT_CSV, DATA_OUTPUT_MIDI, combine_output=True)

        # combine_midis(DATA_INPUT_MIDI, os.path.join(DATA_OUTPUT_MIDI, 'final_recreated_combined.mid'))
    except Exception as e:
        logging.error(f"Error in main script: {e}")
