from setuptools import setup, find_packages

setup(
    name='notapy',
    version='0.1.1',
    description='A Python library to convert MIDI files to CSV and vice versa.',
    author='Mohamed Alturfi',
    author_email='mohamed9667@gmail.com',
    url='https://github.com/altaiiiir/notapy',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'music21',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
