## Troubleshooting

### Common Issues

**"No module named 'PyQt6'" Error**
```bash
pip install PyQt6>=6.4.0
```

**Translation Not Working**  
- Check your internet connection
- Verify the language code is correct (e.g., 'es', not 'spanish')
- Some languages may have limited support

**File Not Processing**
- Ensure the subtitle file has valid SRT/VTT format
- Check file encoding (UTF-8 recommended)
- Verify file permissions

**UI Not Responding**
- Large files may take time to process
- Check the progress bar for updates
- Translation of very long subtitles may take several minutes

### Performance Tips

- **For large files**: Processing may take 2-5 minutes depending on file size
- **Translation speed**: Depends on subtitle count and internet connection
- **Memory usage**: Minimal, even with large subtitle files

---

## Changelog from NiceGUI Version

### ✅ Improvements
- **Native Desktop Experience**: True desktop app with OS-native dialogs
- **Better Performance**: No web server overhead or browser dependency  
- **Enhanced Threading**: Responsive UI during processing with PyQt signals
- **Modern Interface**: Dark theme with improved contrast and readability
- **Error Handling**: Better error messages and user feedback
- **File Handling**: Direct file system access without temporary uploads

### 🔄 Maintained Features
- All original subtitle processing logic
- Translation functionality with batch processing
- Spam cleaning with the same pattern recognition
- Support for both SRT and VTT formats
- Progress tracking and status updates# SRT4U - Subtitle Processor (PyQt Version)

---

## Translate, Clean, and Convert SRT/VTT Subtitles  

![Application Screenshot](https://raw.githubusercontent.com/marodriguezd/SRT4U_Subtitle-Processor/main/assets/demo-screenshot.png)

A native desktop application built with PyQt6 for processing subtitle files with translation and cleaning capabilities. Features a modern dark theme interface with intuitive controls.

## Features  

- **Support for SRT and VTT Formats**:  
   - Import and process SRT or VTT subtitle files with native file dialogs.  
   - Export processed subtitles in your chosen format (SRT or VTT).  
   - ⚠️ **Note**: VTT files with additional styles or metadata will be converted to plain text during processing (see **Important Notes** below).  

- **Smart Translation System**:  
   - Translate subtitles into multiple languages while preserving original timing structure.
   - Batch processing for efficient API usage and faster translation.
   - Auto-detection of source language for optimal translation quality.

- **Advanced Subtitle Cleaning**:  
   - Automatically removes spam content, promotional messages, and unwanted text.
   - Filters out Telegram links, promotional URLs, and subtitle credits.
   - Cleans musical notes and formatting tags that interfere with readability.

- **Native Desktop Experience**:  
   - Built with PyQt6 for native look and feel across all platforms.
   - Modern dark theme interface with intuitive controls.
   - Native file dialogs for seamless file and directory selection.  
   - Real-time progress tracking with detailed status messages.
   - Responsive threading to keep the UI smooth during processing.

- **Output Format Flexibility**:  
   - Choose between SRT or VTT output format regardless of input format.
   - Automatic format conversion with proper headers (WEBVTT for VTT files).
   - Preserves timing precision and subtitle numbering.  

---

## Important Notes  

### About VTT File Processing  
Internally, SRT4U processes subtitle files in the **SRT format**. If you import a VTT file with additional features such as styles, metadata, or non-standard properties, these will be **stripped out during processing**.  
- The application ensures that translations and basic formatting are preserved.  
- However, **styles, positioning, or metadata specific to VTT will not be retained** when exporting back to VTT.  

This design ensures maximum compatibility across formats and simplifies translation and processing tasks.

---

## How to Use  

### Quick Start Guide

1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Select Your Subtitle File**
   - Click "Select SRT/VTT file" button
   - Choose your subtitle file from the native file dialog
   - Supported formats: `.srt`, `.vtt`

3. **Choose Output Location**  
   - Click "Select output directory" button
   - Pick where you want the processed file to be saved

4. **Configure Translation (Optional)**
   - Check "Enable translation" if you want to translate subtitles
   - Enter target language code in the text field (examples: `es` for Spanish, `en` for English, `fr` for French, `de` for German, `it` for Italian, `pt` for Portuguese, `ru` for Russian, `ja` for Japanese, `ko` for Korean, `zh` for Chinese)

5. **Select Output Format**
   - Choose between `srt` or `vtt` format from the dropdown menu
   - This is independent of your input file format

6. **Start Processing**  
   - Click the "Process" button to begin
   - Monitor progress through the progress bar and status messages
   - The application will show real-time updates during processing

7. **Results**
   - Success notifications will appear when processing completes
   - The processed file will be saved with `_processed` suffix in your chosen directory
   - Any errors will be displayed with detailed error messages

### Language Codes Reference
Common language codes for translation:
- `en` - English
- `es` - Spanish  
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese (Simplified)
- `ar` - Arabic
- `hi` - Hindi  

---

## Installation & Requirements

### System Requirements
- **Python 3.8 or later** (Python 3.9+ recommended)
- **Windows, macOS, or Linux**
- **Internet connection** (required for translation feature)

### Dependencies Installation

Install required libraries using pip:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyQt6>=6.4.0 deep-translator>=1.11.4
```

### Quick Installation

1. **Clone the repository**:  
   ```bash  
   git clone https://github.com/your-username/SRT4U-PyQt.git  
   cd SRT4U-PyQt  
   ```  

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:  
   ```bash  
   python main.py  
   ```  

### Alternative Installation (Standalone)

If you prefer to run without cloning:

1. Download all source files
2. Ensure the project structure matches the one shown below
3. Install dependencies and run  

---

## Advanced Features & Technical Details

### Subtitle Processing Pipeline

1. **File Reading**: UTF-8 encoding support for international characters
2. **Content Cleaning**: Removes promotional content, spam, and unwanted formatting
3. **Block Extraction**: Parses subtitle timing and text blocks
4. **Translation** (if enabled): Batch processing with Google Translate API
5. **Timing Optimization**: Ensures smooth subtitle timing continuity  
6. **Format Export**: Outputs in chosen format with proper headers

### Supported Spam Patterns (Auto-Removed)

The application automatically detects and removes:
- Subtitle credits ("Subtitled by...")
- Promotional URLs and Telegram links
- Musical note symbols and formatting
- Course promotion text
- Font tags and HTML formatting
- Chat invitation links

### Threading Architecture

- **Main Thread**: Handles UI updates and user interactions
- **Worker Thread**: Processes subtitles without blocking the interface
- **Signal System**: PyQt6 signals ensure thread-safe communication
- **Progress Updates**: Real-time status and progress reporting

### Error Handling

- **File Format Validation**: Checks for valid SRT/VTT structure
- **Translation Errors**: Graceful fallback to original text if translation fails
- **Network Issues**: Clear error messages for connectivity problems
- **Input Validation**: Prevents processing with invalid parameters
