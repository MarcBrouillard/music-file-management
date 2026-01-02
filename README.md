# Music File Management

A modern desktop application for managing music file collections with metadata editing, intelligent organization, and duplicate detection.

## Features

- **Metadata Editor** - Edit ID3 tags for MP3, FLAC, M4A, OGG, and WAV files
- **File Organization** - Automatically organize and rename files based on metadata
- **Duplicate Detection** - Find duplicates using metadata comparison, file hashing, or audio fingerprinting
- **Local Database** - SQLite database for fast searching and filtering
- **JSON Export** - Backup and restore your music library metadata
- **Modern UI** - Dark mode interface built with CustomTkinter

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Navigate to the project directory:
```bash
cd music-file-management
```

3. Create a virtual environment:
```bash
python -m venv venv
```

4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Run the application:
```bash
python main.py
```

## Usage

### Scanning Your Music Library

1. Click **Browse Folder** and select your music directory
2. Click **Scan Library** to import all music files
3. The app will read metadata and populate the database

### Editing Metadata

1. Select files from the library view
2. Click the **Tags** section in the sidebar
3. Edit artist, title, album, year, genre, and more
4. Click **Save** to write changes to the files

### Organizing Files

1. Click **Organize** in the sidebar
2. Select a naming pattern or create a custom one
3. Preview the changes before applying
4. Click **Execute** to rename and move files

### Finding Duplicates

1. Click **Find Duplicates** in the sidebar
2. Choose detection method:
   - **Metadata**: Fast, compares tags and duration
   - **File Hash**: Medium speed, exact binary matching
   - **Audio Fingerprint**: Slow but most accurate
3. Review duplicate groups
4. Select files to keep or delete

### Exporting Data

1. Click **Export** in the sidebar
2. Choose JSON export location
3. Your entire library metadata will be saved

## Configuration

Edit `config/settings.json` to customize:
- Default scan paths
- Organization patterns
- Duplicate detection settings
- Database and backup locations
- Theme preferences

## Supported Audio Formats

- MP3 (ID3v1, ID3v2)
- FLAC
- M4A/MP4
- OGG Vorbis
- WAV (with ID3)

## Advanced Features

### Audio Fingerprinting

For the most accurate duplicate detection, install optional dependencies:

1. Install pyacoustid:
```bash
pip install pyacoustid
```

2. Install fpcalc (Chromaprint):
   - Windows: Download from https://acoustid.org/chromaprint
   - macOS: `brew install chromaprint`
   - Linux: `sudo apt-get install libchromaprint-tools`

## Troubleshooting

**"Permission denied" when editing files**
- Ensure files are not read-only
- Close any other applications using the files

**"Module not found" errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Slow duplicate detection**
- Use metadata comparison for large libraries
- Audio fingerprinting is most accurate but slowest

## License

MIT License - Feel free to modify and distribute

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
