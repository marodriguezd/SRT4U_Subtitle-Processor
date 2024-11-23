# SRT4U - Subtitle Processor  
---

## Translate, Clean, and Convert SRT/VTT Subtitles  

![User Interface Preview](https://i.imgur.com/Idf0Hn7.png)  

## Features  

- **Support for SRT and VTT Formats**:  
   - Import and process SRT or VTT subtitle files.  
   - Export processed subtitles in your chosen format (SRT or VTT).  
- **Output Format Selection**:  
   - Choose the format for the processed file: SRT or VTT.  
- **Subtitle Translation**:  
   - Translate subtitles into multiple languages while preserving the original structure.  
- **Spam Cleaning**:  
   - Automatically removes unwanted content from subtitles.  
- **User-Friendly Interface**:  
   - Easily select files and output directories.  
   - Progress bar to track processing status.  
   - Notifications to inform about success or errors.  

## How to Use  

1. Select an SRT or VTT file to process.  
2. Choose an output directory to save the processed file.  
3. Optional: Enable translation and specify the target language.  
4. Select the output format (SRT or VTT).  
5. Click the "Process" button to start processing.  
6. Monitor progress via the progress bar and notifications.  
7. Once completed, the processed file will be saved in the selected directory.  

## Requirements  

- Python 3.8 or later.  
- Dependencies:  
  ```bash  
  pip install nicegui deep_translator  
  ```  

## Installation  

1. Clone the repository:  
   ```bash  
   git clone https://github.com/your-username/SRT4U.git  
   cd SRT4U  
   ```  
2. Run the application:  
   ```bash  
   python main.py  
   ```  

## Credits  

- Developed by Miguel Ángel (using AI).  
- License: Apache License 2.0.  