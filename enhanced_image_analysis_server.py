#!/usr/bin/env python3
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult, Tool, TextContent

# Check for required dependencies
try:
    import mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("enhanced-image-analysis-server")

class EnhancedImageAnalysisServer:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    def analyze_image_colors(self, image_path: Path) -> Dict[str, Any]:
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.thumbnail((150, 150))
                colors = img.getcolors(maxcolors=256*256*256)
                if not colors:
                    return {"error": "Could not analyze colors"}
                colors.sort(reverse=True)
                top_colors = []
                total_pixels = sum(count for count, color in colors)
                for i, (count, color) in enumerate(colors[:5]):
                    percentage = (count / total_pixels) * 100
                    top_colors.append({"rgb": color, "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", "percentage": round(percentage, 2)})
                return {"dominant_colors": top_colors, "color_family": self.classify_color(top_colors[0]["rgb"]), "is_grayscale": self.is_grayscale_image(img), "brightness": self.calculate_brightness(img)}
        except Exception as e:
            return {"error": f"Color analysis failed: {str(e)}"}

    def classify_color(self, rgb: Tuple[int, int, int]) -> str:
        r, g, b = rgb
        if abs(r - g) < 15 and abs(g - b) < 15 and abs(r - b) < 15:
            return "black" if r < 50 else "white" if r > 200 else "gray"
        if r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        elif r > 150 and g > 150 and b < 100:
            return "yellow"
        return "mixed"

    def is_grayscale_image(self, img: Image.Image) -> bool:
        if img.mode == 'L':
            return True
        elif img.mode == 'RGB':
            for r, g, b in list(img.getdata())[:100]:
                if abs(r - g) > 10 or abs(g - b) > 10:
                    return False
            return True
        return False

    def calculate_brightness(self, img: Image.Image) -> float:
        try:
            pixels = list(img.convert('L').getdata())
            return sum(pixels) / len(pixels) / 255.0
        except:
            return 0.5

    def extract_exif_data(self, image_path: Path) -> Dict[str, Any]:
        try:
            with Image.open(image_path) as img:
                exif_data = {}
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8')
                                except:
                                    value = str(value)
                            exif_data[tag] = value
                return exif_data
        except Exception as e:
            return {"error": f"EXIF extraction failed: {str(e)}"}

    def advanced_heuristic_analysis(self, image_path: Path) -> Dict[str, Any]:
        analysis = {}
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                analysis['orientation'] = 'landscape' if width > height else 'portrait' if height > width else 'square'
                analysis['size_category'] = self.categorize_size(width * height)
                analysis['aspect_ratio'] = round(width / height, 2)
                color_info = self.analyze_image_colors(image_path)
                analysis.update(color_info)
                exif_data = self.extract_exif_data(image_path)
                if exif_data and "error" not in exif_data:
                    if 'Make' in exif_data or 'Model' in exif_data:
                        analysis['source'] = 'camera'
                    if 'Software' in exif_data:
                        software = str(exif_data['Software']).lower()
                        if 'screenshot' in software or 'capture' in software:
                            analysis['type'] = 'screenshot'
                        elif 'photoshop' in software or 'gimp' in software:
                            analysis['type'] = 'edited'
                    if 'DateTime' in exif_data:
                        analysis['has_timestamp'] = True
                analysis['file_size_category'] = self.categorize_file_size(image_path.stat().st_size)
                analysis['filename_hints'] = self.analyze_filename(image_path.stem.lower())
        except Exception as e:
            analysis['error'] = str(e)
        return analysis

    def categorize_size(self, pixels: int) -> str:
        return "huge" if pixels > 8000000 else "large" if pixels > 2000000 else "medium" if pixels > 500000 else "small"

    def categorize_file_size(self, bytes_size: int) -> str:
        mb = bytes_size / (1024 * 1024)
        return "large" if mb > 10 else "medium" if mb > 1 else "small"

    def analyze_filename(self, filename: str) -> List[str]:
        hints = []
        patterns = {
            'screenshot': ['screenshot', 'screen', 'capture', 'scr'], 'photo': ['photo', 'img', 'pic', 'picture', 'dsc'],
            'download': ['download', 'temp', 'untitled'], 'edited': ['edit', 'modified', 'copy', 'final'],
            'scan': ['scan', 'document', 'doc'], 'avatar': ['avatar', 'profile', 'headshot'],
            'logo': ['logo', 'brand', 'icon'], 'diagram': ['diagram', 'chart', 'graph', 'flowchart']
        }
        for category, keywords in patterns.items():
            if any(keyword in filename for keyword in keywords):
                hints.append(category)
        return hints

    def generate_name_from_analysis(self, analysis: Dict[str, Any], style: str) -> str:
        parts = []
        if style == "descriptive":
            if 'color_family' in analysis and analysis['color_family'] not in ['mixed', 'gray']:
                parts.append(analysis['color_family'])
            if analysis.get('orientation') != 'square':
                parts.append(analysis['orientation'])
        elif style == "technical":
            parts.append(f"{analysis.get('size_category', 'medium')}_res")
            parts.append(analysis.get('orientation', 'unknown'))
            if analysis.get('source') == 'camera':
                parts.append('camera')
            elif 'screenshot' in analysis.get('filename_hints', []):
                parts.append('screenshot')
        elif style == "artistic":
            if 'color_family' in analysis:
                parts.append(analysis['color_family'])
            if analysis.get('brightness', 0.5) > 0.7:
                parts.append('bright')
            elif analysis.get('brightness', 0.5) < 0.3:
                parts.append('dark')
            if analysis.get('is_grayscale'):
                parts.append('bw')
        elif style == "location":
            if 'has_timestamp' in analysis:
                parts.append('dated')
            parts.append(analysis.get('orientation', 'photo'))
        hints = analysis.get('filename_hints', [])
        for hint in hints[:1]:
            if hint not in parts:
                parts.append(hint)
        return '_'.join(parts) if parts else 'image'

    def is_image_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_formats

    def get_image_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        image_files = []
        try:
            if recursive:
                for file_path in directory.rglob("*"):
                    if file_path.is_file() and self.is_image_file(file_path):
                        image_files.append(file_path)
            else:
                for file_path in directory.iterdir():
                    if file_path.is_file() and self.is_image_file(file_path):
                        image_files.append(file_path)
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        return sorted(image_files)

# Create server instance
image_server = EnhancedImageAnalysisServer()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="ai_analyze_directory_images",
            description="Analyze all images in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string"},
                    "recursive": {"type": "boolean", "default": False},
                    "rename_files": {"type": "boolean", "default": False},
                    "prefix": {"type": "string", "default": ""},
                    "naming_style": {"type": "string", "default": "descriptive", "enum": ["descriptive", "technical", "artistic", "location"]}
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="ai_analyze_single_image",
            description="Analyze a single image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"},
                    "naming_style": {"type": "string", "default": "descriptive", "enum": ["descriptive", "technical", "artistic", "location"]},
                    "detailed_analysis": {"type": "boolean", "default": False}
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="extract_comprehensive_metadata",
            description="Extract comprehensive metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"},
                    "include_color_analysis": {"type": "boolean", "default": True}
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="organize_images_by_content",
            description="Organize images into folders",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string"},
                    "create_folders": {"type": "boolean", "default": False},
                    "organization_method": {"type": "string", "default": "content", "enum": ["content", "date", "size", "format"]}
                },
                "required": ["directory_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "ai_analyze_directory_images":
            return await ai_analyze_directory_images(arguments)
        elif name == "ai_analyze_single_image":
            return await ai_analyze_single_image(arguments)
        elif name == "extract_comprehensive_metadata":
            return await extract_comprehensive_metadata(arguments)
        elif name == "organize_images_by_content":
            return await organize_images_by_content(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def ai_analyze_single_image(arguments: Dict[str, Any]) -> list[TextContent]:
    image_path = Path(arguments["image_path"])
    naming_style = arguments.get("naming_style", "descriptive")
    detailed_analysis = arguments.get("detailed_analysis", False)
    
    if not image_path.exists():
        return [TextContent(type="text", text=f"Image file does not exist: {image_path}")]
    if not image_server.is_image_file(image_path):
        return [TextContent(type="text", text=f"File is not a supported image format: {image_path}")]
    
    try:
        analysis_data = image_server.advanced_heuristic_analysis(image_path)
        new_name = image_server.generate_name_from_analysis(analysis_data, naming_style)
        
        if detailed_analysis:
            analysis_text = f"""🎯 Enhanced Image Analysis
📁 File: {image_path.name}
📍 Path: {image_path}
📊 Suggested Name: {new_name}{image_path.suffix.lower()}
🎨 Naming Style: {naming_style}

🔍 Technical Details:
- Dimensions: {analysis_data.get('aspect_ratio', 'unknown')} ratio
- Size Category: {analysis_data.get('size_category', 'unknown')}
- File Size: {analysis_data.get('file_size_category', 'unknown')}
- Orientation: {analysis_data.get('orientation', 'unknown')}

🎨 Visual Analysis:
- Color Family: {analysis_data.get('color_family', 'unknown')}
- Brightness: {analysis_data.get('brightness', 0.5):.2f}
- Grayscale: {analysis_data.get('is_grayscale', False)}

📝 Content Insights:
- Detected Hints: {', '.join(analysis_data.get('filename_hints', ['none']))}
- Source Type: {analysis_data.get('source', 'unknown')}"""
            
            if 'dominant_colors' in analysis_data:
                colors = analysis_data['dominant_colors'][:3]
                color_info = [f"{color['hex']} ({color['percentage']:.1f}%)" for color in colors]
                analysis_text += f"\n- Top Colors: {', '.join(color_info)}"
            
            return [TextContent(type="text", text=analysis_text)]
        else:
            return [TextContent(type="text", text=f"💡 Suggested name: {new_name}{image_path.suffix.lower()}\n🎨 Style: {naming_style}\n🔍 Analysis: Advanced heuristics")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error analyzing image: {str(e)}")]

async def ai_analyze_directory_images(arguments: Dict[str, Any]) -> list[TextContent]:
    directory_path = Path(arguments["directory_path"])
    recursive = arguments.get("recursive", False)
    rename_files = arguments.get("rename_files", False)
    prefix = arguments.get("prefix", "")
    naming_style = arguments.get("naming_style", "descriptive")
    
    if not directory_path.exists():
        return [TextContent(type="text", text=f"Directory does not exist: {directory_path}")]
    
    image_files = image_server.get_image_files(directory_path, recursive)
    if not image_files:
        return [TextContent(type="text", text="No image files found in the directory")]
    
    results, renamed_files, analysis_results = [], [], []
    
    for i, image_path in enumerate(image_files):
        try:
            progress = f"[{i+1}/{len(image_files)}]"
            analysis_data = image_server.advanced_heuristic_analysis(image_path)
            new_name = image_server.generate_name_from_analysis(analysis_data, naming_style)
            
            if prefix:
                new_name = f"{prefix}_{new_name}"
            
            new_name = f"{new_name}{image_path.suffix.lower()}"
            new_path = image_path.parent / new_name
            
            counter = 1
            original_new_name = new_name
            while new_path.exists() and new_path != image_path:
                name_parts = original_new_name.rsplit('.', 1)
                new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                new_path = image_path.parent / new_name
                counter += 1
            
            if rename_files and new_path != image_path:
                try:
                    image_path.rename(new_path)
                    renamed_files.append(f"{progress} ✅ {image_path.name} → {new_name}")
                except Exception as e:
                    results.append(f"{progress} ❌ Failed to rename {image_path.name}: {str(e)}")
            else:
                results.append(f"{progress} 💡 {image_path.name} → {new_name}")
            
            analysis_results.append({'original': image_path.name, 'suggested': new_name, 'analysis': analysis_data})
        except Exception as e:
            results.append(f"{progress} ❌ Error processing {image_path.name}: {str(e)}")
    
    summary_parts = [f"🎯 Enhanced Image Analysis Complete", f"📊 Processed {len(image_files)} image files using {naming_style} style", ""]
    
    if rename_files:
        summary_parts.extend([f"✅ Successfully renamed {len(renamed_files)} files:", ""])
        summary_parts.extend(renamed_files)
    else:
        summary_parts.extend([f"💡 Suggested names (use rename_files=true to apply):", ""])
        summary_parts.extend(results)
    
    if analysis_results:
        color_families, orientations = {}, {}
        for result in analysis_results:
            analysis = result['analysis']
            if 'color_family' in analysis:
                color_families[analysis['color_family']] = color_families.get(analysis['color_family'], 0) + 1
            if 'orientation' in analysis:
                orientations[analysis['orientation']] = orientations.get(analysis['orientation'], 0) + 1
        
        summary_parts.extend(["", "📈 Analysis Insights:", f"🎨 Color distribution: {dict(list(color_families.items())[:3])}", f"📐 Orientations: {orientations}"])
    
    return [TextContent(type="text", text="\n".join(summary_parts))]

async def extract_comprehensive_metadata(arguments: Dict[str, Any]) -> list[TextContent]:
    image_path = Path(arguments["image_path"])
    include_color_analysis = arguments.get("include_color_analysis", True)
    
    if not image_path.exists():
        return [TextContent(type="text", text=f"Image file does not exist: {image_path}")]
    
    try:
        metadata = {"filename": image_path.name, "path": str(image_path)}
        
        with Image.open(image_path) as img:
            metadata.update({"format": img.format, "mode": img.mode, "size": img.size, "width": img.width, "height": img.height, "aspect_ratio": round(img.width / img.height, 3)})
        
        stat = image_path.stat()
        metadata.update({"file_size_bytes": stat.st_size, "file_size_mb": round(stat.st_size / (1024 * 1024), 2), "created": datetime.fromtimestamp(stat.st_ctime).isoformat(), "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()})
        
        exif_data = image_server.extract_exif_data(image_path)
        if exif_data and "error" not in exif_data:
            metadata["exif"] = exif_data
        
        if include_color_analysis:
            color_analysis = image_server.analyze_image_colors(image_path)
            if "error" not in color_analysis:
                metadata["color_analysis"] = color_analysis
        
        metadata_text = json.dumps(metadata, indent=2, default=str)
        return [TextContent(type="text", text=f"🔍 Comprehensive Metadata for {image_path.name}:\n\n```json\n{metadata_text}\n```")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error extracting metadata: {str(e)}")]

async def organize_images_by_content(arguments: Dict[str, Any]) -> list[TextContent]:
    directory_path = Path(arguments["directory_path"])
    create_folders = arguments.get("create_folders", False)
    organization_method = arguments.get("organization_method", "content")
    
    if not directory_path.exists():
        return [TextContent(type="text", text=f"Directory does not exist: {directory_path}")]
    
    image_files = image_server.get_image_files(directory_path, False)
    if not image_files:
        return [TextContent(type="text", text="No image files found in the directory")]
    
    categories = {}
    
    for image_path in image_files:
        try:
            category = "miscellaneous"
            if organization_method == "content":
                analysis = image_server.advanced_heuristic_analysis(image_path)
                if 'screenshot' in analysis.get('filename_hints', []):
                    category = "screenshots"
                elif 'photo' in analysis.get('filename_hints', []):
                    category = "photos"
                elif analysis.get('source') == 'camera':
                    category = "camera_photos"
                elif 'edited' in analysis.get('filename_hints', []):
                    category = "edited_images"
                elif analysis.get('orientation') == 'portrait':
                    category = "portraits"
                elif analysis.get('orientation') == 'landscape':
                    category = "landscapes"
                elif analysis.get('color_family') in ['black', 'white', 'gray']:
                    category = "black_white"
            elif organization_method == "date":
                stat = image_path.stat()
                date = datetime.fromtimestamp(stat.st_ctime)
                category = f"{date.year}-{date.month:02d}"
            elif organization_method == "size":
                with Image.open(image_path) as img:
                    category = image_server.categorize_size(img.width * img.height)
            elif organization_method == "format":
                category = image_path.suffix.lower().replace('.', '')
            
            if category not in categories:
                categories[category] = []
            categories[category].append(image_path)
        except Exception as e:
            logger.error(f"Error analyzing {image_path}: {e}")
            if "errors" not in categories:
                categories["errors"] = []
            categories["errors"].append(image_path)
    
    plan_parts = [f"📁 Image Organization Plan", f"📊 Method: {organization_method}", f"🔍 Found {len(image_files)} images in {len(categories)} categories", ""]
    
    for category, files in categories.items():
        plan_parts.append(f"📂 {category.replace('_', ' ').title()} ({len(files)} files):")
        for file_path in files[:5]:
            plan_parts.append(f"   • {file_path.name}")
        if len(files) > 5:
            plan_parts.append(f"   • ... and {len(files) - 5} more")
        plan_parts.append("")
    
    if create_folders:
        moved_files, errors = [], []
        for category, files in categories.items():
            category_dir = directory_path / category
            try:
                category_dir.mkdir(exist_ok=True)
                for file_path in files:
                    try:
                        new_path = category_dir / file_path.name
                        counter = 1
                        while new_path.exists():
                            name_parts = file_path.name.rsplit('.', 1)
                            new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                            new_path = category_dir / new_name
                            counter += 1
                        file_path.rename(new_path)
                        moved_files.append(f"✅ {file_path.name} → {category}/{new_path.name}")
                    except Exception as e:
                        errors.append(f"❌ Failed to move {file_path.name}: {str(e)}")
            except Exception as e:
                errors.append(f"❌ Failed to create folder {category}: {str(e)}")
        
        plan_parts.extend([f"🎯 Organization Results:", f"✅ Successfully moved {len(moved_files)} files", f"❌ Encountered {len(errors)} errors", ""])
        
        if moved_files:
            plan_parts.extend(["Moved Files:"] + moved_files[:10])
            if len(moved_files) > 10:
                plan_parts.append(f"... and {len(moved_files) - 10} more")
        if errors:
            plan_parts.extend(["Errors:"] + errors)
    else:
        plan_parts.append("💡 Use create_folders=true to actually organize the files")
    
    return [TextContent(type="text", text="\n".join(plan_parts))]

async def main():
    logger.info("Starting Enhanced Image Analysis MCP Server")
    
    # Check dependencies at startup
    if not MCP_AVAILABLE:
        print("Error: MCP library not found. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)
    
    if not PIL_AVAILABLE:
        print(f"Warning: PIL/Pillow not found. Limited functionality available.", file=sys.stderr)
        print(f"Install with: {sys.executable} -m pip install Pillow", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="enhanced-image-analysis-server", 
                server_version="2.1.0", 
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
