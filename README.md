# NotaPy

NotaPy is a Python library for converting MIDI files to CSV files and vice versa, as well as combining multiple MIDI files into a single track. It leverages `music21` to ensure accurate conversion and manipulation of MIDI files, making it ideal for musical data analysis, modification, or generation projects.

## Features

- **Convert MIDI to CSV**: Extract note information, such as pitch, duration, and velocity, from MIDI files and save it in a CSV format.
- **Convert CSV to MIDI**: Recreate the original music from CSV files that contain note information.
- **Combine Multiple MIDI Files**: Merge multiple MIDI files into a single MIDI file.
- **Easy Integration**: Designed for seamless integration with other music or data processing pipelines.

## Installation

To install NotaPy, clone the repository or install via pip (if published on PyPI):

```sh
pip install notapy
```

## Usage

Here is how you can use the key features of NotaPy:

### 1. Convert MIDI to CSV

```python
from notapy import convert_midi_to_csv

convert_midi_to_csv('path/to/input.mid', 'path/to/output.csv')
```

### 2. Convert CSV to MIDI

```python
from notapy import convert_csv_to_midi

convert_csv_to_midi('path/to/input.csv', 'path/to/output.mid')
```

### 3. Combine Multiple MIDI Files

```python
from notapy import convert_and_combine_midi_files

input_midis = ['path/to/input1.mid', 'path/to/input2.mid']
combined_output = 'path/to/combined_output.mid'
convert_and_combine_midi_files(input_midis, combined_output)
```

## Project Structure

- `midi_converter/`: The main library directory containing the conversion code.
- `README.md`: Description and usage information for the library.
- `setup.py`: Setup script for installing the library and dependencies.

## Requirements

- Python 3.6+

All required dependencies, such as `pandas` and `music21`, will be installed automatically when you install NotaPy via `pip`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Contributing

Contributions are always welcome! Feel free to open issues or submit pull requests on [GitHub](https://github.com/altaiiiir/notapy).
