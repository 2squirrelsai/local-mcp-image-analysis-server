#!/bin/bash

# Install Enhanced Image Analysis MCP Server

echo "🚀 Setting up Enhanced Image Analysis MCP Server..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Found Python $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make the server executable
chmod +x enhanced_image_analysis_server.py

echo "🎯 Setup complete! The Enhanced Image Analysis MCP Server is ready to use."
echo ""
echo "📋 Next steps:"
echo "1. Add the server to your MCP client configuration"
echo "2. Use the server to analyze and organize your images"
echo ""
echo "📚 Available tools:"
echo "   • ai_analyze_directory_images - Analyze and rename images in a directory"
echo "   • ai_analyze_single_image - Analyze a single image file"
echo "   • extract_comprehensive_metadata - Extract detailed image metadata"
echo "   • organize_images_by_content - Organize images into folders"
echo ""
echo "🔧 Configuration example for Claude Desktop:"
echo "Add this to your claude_desktop_config.json:"
echo '{'
echo '  "mcpServers": {'
echo '    "image-analysis": {'
echo '      "command": "python3",'
echo '      "args": ["'$(pwd)'/enhanced_image_analysis_server.py"],'
echo '      "env": {}'
echo '    }'
echo '  }'
echo '}'