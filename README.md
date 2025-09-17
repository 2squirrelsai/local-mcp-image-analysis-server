# Enhanced Image Analysis MCP Server

A powerful Model Context Protocol (MCP) server that uses advanced heuristics to analyze images and generate intelligent, descriptive filenames. Perfect for organizing large photo collections, screenshots, and digital assets.

## 🚀 Features

- **🎯 Smart Image Analysis**: Advanced heuristic analysis of image characteristics
- **📝 Intelligent Naming**: Four naming styles (descriptive, technical, artistic, location)
- **📂 Batch Processing**: Analyze entire directories with recursive search
- **🎨 Color Analysis**: Dominant color detection and classification
- **📊 EXIF Data**: Extract camera settings, timestamps, and metadata
- **📁 Auto Organization**: Sort images into folders by content, date, size, or format
- **🔍 Comprehensive Metadata**: Extract detailed technical information
- **⚡ Smart Caching**: Avoid re-analyzing unchanged images

## 📦 Installation

### Quick Setup

```bash
cd /Users/anthonyturner/MCPs/image-analysis-server
chmod +x setup.sh
./setup.sh
```

### Manual Installation

```bash
# Install dependencies
pip3 install mcp Pillow

# Make executable
chmod +x enhanced_image_analysis_server.py
```

## ⚙️ Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "image-analysis": {
      "command": "python3",
      "args": ["/Users/anthonyturner/MCPs/image-analysis-server/enhanced_image_analysis_server.py"],
      "env": {}
    }
  }
}
```

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

## 🛠️ Available Tools

### 1. `ai_analyze_directory_images`
Analyze all images in a directory and generate intelligent names.

**Parameters:**
- `directory_path` (required): Path to directory containing images
- `recursive` (optional): Search subdirectories (default: false)
- `rename_files` (optional): Actually rename files (default: false)
- `prefix` (optional): Add prefix to generated names
- `naming_style` (optional): Style of naming (default: "descriptive")

**Example Usage:**
```
Analyze all images in ~/Pictures/vacation2024 and suggest better names using technical style
```

### 2. `ai_analyze_single_image`
Analyze a single image file and generate a descriptive name.

**Parameters:**
- `image_path` (required): Path to the image file
- `naming_style` (optional): Naming style (default: "descriptive")
- `detailed_analysis` (optional): Provide comprehensive analysis (default: false)

**Example Usage:**
```
Analyze /Users/me/Desktop/photo.jpg with detailed analysis using artistic naming style
```

### 3. `extract_comprehensive_metadata`
Extract detailed metadata including EXIF data and color analysis.

**Parameters:**
- `image_path` (required): Path to the image file
- `include_color_analysis` (optional): Include color palette analysis (default: true)

**Example Usage:**
```
Extract comprehensive metadata from my screenshot including color analysis
```

### 4. `organize_images_by_content`
Organize images into folders based on detected content and characteristics.

**Parameters:**
- `directory_path` (required): Path to directory containing images
- `create_folders` (optional): Actually create folders and move files (default: false)
- `organization_method` (optional): Method to organize (default: "content")

**Organization Methods:**
- `content`: By detected content (screenshots, photos, portraits, etc.)
- `date`: By creation date (YYYY-MM format)
- `size`: By image resolution (small, medium, large, huge)
- `format`: By file format (jpg, png, gif, etc.)

## 🎨 Naming Styles

### Descriptive (Default)
Focuses on visual content and characteristics:
- `red_landscape_photo.jpg`
- `blue_portrait_screenshot.png`

### Technical
Emphasizes technical specifications:
- `large_res_landscape_camera.jpg`
- `medium_res_portrait_screenshot.png`

### Artistic
Highlights aesthetic qualities:
- `red_bright_photo.jpg`
- `gray_dark_bw.png`

### Location
Designed for organizing by context:
- `dated_landscape.jpg`
- `photo_portrait.png`

## 📊 Smart Analysis Features

### Color Analysis
- **Dominant Colors**: Top 5 colors with percentages
- **Color Family**: Classification (red, blue, green, etc.)
- **Grayscale Detection**: Identifies black & white images
- **Brightness Analysis**: Average brightness calculation

### Content Detection
The server analyzes filename patterns to detect:
- **Screenshots**: Screen captures and UI elements
- **Photos**: Camera-taken images and photography
- **Edited Images**: Modified or processed images
- **Scans**: Digitized documents
- **Logos/Icons**: Brand and graphic elements

### EXIF Data Extraction
- **Camera Information**: Make, model, settings
- **Timestamps**: When photo was taken
- **Software**: Editing applications used
- **GPS Data**: Location information (when available)

## 🚀 Example Workflows

### Organize Downloads Folder
```
I have a messy Downloads folder with hundreds of images. Can you organize them by content type and suggest better names?
```

### Rename Vacation Photos
```
Analyze images in ~/Pictures/Hawaii2024 recursively, use descriptive naming with prefix "hawaii", and actually rename the files
```

### Technical Analysis
```
Extract comprehensive metadata from ~/Desktop/camera_test.jpg including color analysis and EXIF data
```

### Batch Screenshot Organization
```
Organize all images in ~/Desktop by content, actually create the folders and move files
```

## 🔧 Advanced Features

### Intelligent Conflict Resolution
- Automatically handles duplicate filenames
- Adds incremental counters when needed
- Preserves original files during preview mode

### Performance Optimizations
- **Smart Caching**: Avoids re-analyzing unchanged images
- **Efficient Color Analysis**: Uses image thumbnails for color detection
- **Batch Processing**: Optimized for large directories

### Error Handling
- **Graceful Degradation**: Continues processing other files if one fails
- **Detailed Error Reports**: Clear error messages for troubleshooting
- **File Validation**: Ensures only supported formats are processed

## 📋 Supported Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **BMP** (.bmp)
- **TIFF** (.tiff)
- **WebP** (.webp)

## 🛡️ Safety Features

- **Preview Mode**: Default behavior suggests changes without applying them
- **Backup Consideration**: Always backup important files before batch operations
- **Permission Checks**: Validates file system permissions before operations
- **Non-destructive Analysis**: Metadata extraction never modifies original files

## 🚨 Troubleshooting

### Common Issues

1. **"No image files found"**
   - Verify directory path is correct
   - Check if images are in supported formats
   - Try recursive search for images in subdirectories

2. **"Permission denied"**
   - Ensure read/write permissions on target directory
   - Check if files are not locked by other applications

3. **"Failed to analyze image"**
   - File may be corrupted or not a valid image
   - Check if sufficient disk space is available

### Debug Mode
```bash
# Run with debug logging
python3 enhanced_image_analysis_server.py --debug
```

## 🔮 Future Enhancements

The server is designed to be easily extensible:

- **AI Vision Integration**: Add OpenAI GPT-4 Vision or Google Cloud Vision
- **Face Detection**: Identify and organize photos with people
- **Object Recognition**: Detect specific objects, animals, or scenes
- **Duplicate Detection**: Find and organize duplicate images
- **Cloud Storage**: Support for Google Photos, iCloud, etc.

## 📄 License

MIT License - Feel free to modify and distribute.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional naming styles
- More sophisticated content detection
- Integration with cloud vision APIs
- Performance optimizations
- Additional metadata extraction

---

**Ready to organize your images intelligently? Install the Enhanced Image Analysis MCP Server and transform your photo management workflow!**