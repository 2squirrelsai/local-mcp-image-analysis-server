#!/bin/bash

echo "🔧 Fixing Enhanced Image Analysis MCP Server Dependencies"
echo "========================================================="

# Check Python version
echo "🐍 Checking Python installation..."
PYTHON_PATH="/usr/local/bin/python3"
if [ -f "$PYTHON_PATH" ]; then
    echo "✅ Found Python at: $PYTHON_PATH"
    $PYTHON_PATH --version
else
    echo "❌ Python not found at $PYTHON_PATH"
    echo "Looking for alternative Python installations..."
    which python3
    PYTHON_PATH=$(which python3)
fi

echo ""
echo "📦 Installing dependencies with the correct Python..."

# Install MCP
echo "Installing MCP..."
$PYTHON_PATH -m pip install --user mcp

# Install Pillow
echo "Installing Pillow..."
$PYTHON_PATH -m pip install --user Pillow

# Also try system-wide installation as fallback
echo "Attempting system-wide installation as fallback..."
$PYTHON_PATH -m pip install mcp Pillow 2>/dev/null || echo "System-wide install failed (this is normal if you don't have admin rights)"

echo ""
echo "🧪 Testing dependencies..."

# Test imports
$PYTHON_PATH -c "
import sys
print(f'Python executable: {sys.executable}')
print(f'Python path: {sys.path}')

try:
    import mcp
    print('✅ MCP imported successfully')
except ImportError as e:
    print(f'❌ MCP import failed: {e}')

try:
    from PIL import Image
    print('✅ PIL imported successfully')
except ImportError as e:
    print(f'❌ PIL import failed: {e}')
"

echo ""
echo "🚀 Testing MCP Server..."

# Test the server
cd /Users/anthonyturner/MCPs/image-analysis-server

echo "Testing server startup..."
timeout 5s $PYTHON_PATH enhanced_image_analysis_server.py <<< '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' 2>&1 | head -10

echo ""
echo "🔍 Server diagnostics..."
$PYTHON_PATH -c "
import sys
sys.path.append('/Users/anthonyturner/MCPs/image-analysis-server')

try:
    from enhanced_image_analysis_server import EnhancedImageAnalysisServer
    server = EnhancedImageAnalysisServer()
    print('✅ Server class imported successfully')
    
    # Test basic functionality
    from pathlib import Path
    test_dir = Path('/Users/anthonyturner/Pictures')
    if test_dir.exists():
        images = server.get_image_files(test_dir, False)
        print(f'✅ Found {len(images)} image files in Pictures')
    else:
        print('⚠️ Pictures directory not found')
        
except Exception as e:
    print(f'❌ Server test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "📋 Installation Summary:"
echo "========================"
echo "Python Path: $PYTHON_PATH"
echo "Server Location: /Users/anthonyturner/MCPs/image-analysis-server/enhanced_image_analysis_server.py"
echo ""
echo "🔄 Next Steps:"
echo "1. Restart Claude Desktop completely"
echo "2. The server should now work with dependency checking"
echo "3. If you see 'Limited analysis' messages, it means Pillow needs to be installed for full functionality"
echo ""
echo "🆘 If problems persist, try:"
echo "   brew install python3"
echo "   /opt/homebrew/bin/python3 -m pip install mcp Pillow"
echo "   Then update the Claude config to use /opt/homebrew/bin/python3"