#!/usr/bin/env python3
"""
Diagnostic script for the Enhanced Image Analysis MCP Server
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    print("🔍 Enhanced Image Analysis MCP Server Diagnostics")
    print("=" * 50)
    
    # Python info
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Python Executable: {sys.executable}")
    print(f"📁 Current Directory: {os.getcwd()}")
    print()
    
    # Check MCP
    try:
        import mcp
        print("✅ MCP library: Available")
    except ImportError as e:
        print(f"❌ MCP library: Not found ({e})")
        print(f"   Install with: {sys.executable} -m pip install mcp")
    
    # Check PIL/Pillow
    try:
        from PIL import Image
        print("✅ PIL/Pillow library: Available")
        
        # Test basic functionality
        try:
            # Create a small test image in memory
            test_img = Image.new('RGB', (100, 100), color='red')
            print("✅ PIL basic functionality: Working")
        except Exception as e:
            print(f"⚠️ PIL basic functionality: Error ({e})")
            
    except ImportError as e:
        print(f"❌ PIL/Pillow library: Not found ({e})")
        print(f"   Install with: {sys.executable} -m pip install Pillow")
    
    print()
    
    # Check server file
    server_path = Path("/Users/anthonyturner/MCPs/image-analysis-server/enhanced_image_analysis_server.py")
    if server_path.exists():
        print(f"✅ Server file: Found at {server_path}")
    else:
        print(f"❌ Server file: Not found at {server_path}")
    
    # Check test directory
    pictures_dir = Path("/Users/anthonyturner/Pictures")
    if pictures_dir.exists():
        # Count image files
        image_count = len([f for f in pictures_dir.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}])
        print(f"✅ Test directory: Found {image_count} images in {pictures_dir}")
    else:
        print(f"⚠️ Test directory: Pictures folder not found")
    
    print()
    
    # Test server import
    try:
        sys.path.append(str(server_path.parent))
        from enhanced_image_analysis_server import EnhancedImageAnalysisServer
        print("✅ Server import: Successful")
        
        # Test server initialization
        server = EnhancedImageAnalysisServer()
        print("✅ Server initialization: Successful")
        
        # Test basic functionality
        if pictures_dir.exists():
            images = server.get_image_files(pictures_dir, False)
            print(f"✅ Image detection: Found {len(images)} images")
        
    except ImportError as e:
        print(f"❌ Server import: Failed ({e})")
    except Exception as e:
        print(f"❌ Server functionality: Error ({e})")
    
    print()
    print("🎯 **RECOMMENDATIONS:**")
    
    # Check if all dependencies are available
    mcp_available = True
    pil_available = True
    
    try:
        import mcp
    except ImportError:
        mcp_available = False
        
    try:
        from PIL import Image
    except ImportError:
        pil_available = False
    
    if mcp_available and pil_available:
        print("✅ All dependencies are installed!")
        print("🚀 Server should work properly in Claude Desktop")
        print("💡 If still having issues, restart Claude Desktop completely")
    elif mcp_available and not pil_available:
        print("⚠️ MCP is installed but Pillow is missing")
        print(f"📦 Run: {sys.executable} -m pip install Pillow")
        print("🔧 Server will work with limited functionality until Pillow is installed")
    elif not mcp_available and pil_available:
        print("⚠️ Pillow is installed but MCP is missing")
        print(f"📦 Run: {sys.executable} -m pip install mcp")
    else:
        print("❌ Both MCP and Pillow are missing")
        print(f"📦 Run: {sys.executable} -m pip install mcp Pillow")
    
    print()
    print("🔧 **TROUBLESHOOTING:**")
    print("1. If using Homebrew Python, try: /opt/homebrew/bin/python3 -m pip install mcp Pillow")
    print("2. If using system Python, try: /usr/bin/python3 -m pip install mcp Pillow")  
    print("3. Update Claude config to use the correct Python path")
    print("4. Restart Claude Desktop after installing dependencies")

if __name__ == "__main__":
    check_dependencies()