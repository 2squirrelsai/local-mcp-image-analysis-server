#!/usr/bin/env python3
"""
Demo script showing the Enhanced Image Analysis MCP Server capabilities
"""
import sys
import os
sys.path.append('/Users/anthonyturner/MCPs/image-analysis-server')
from enhanced_image_analysis_server import EnhancedImageAnalysisServer
import asyncio
from pathlib import Path
import json

async def demo_analysis():
    print("🚀 Enhanced Image Analysis MCP Server Demo")
    print("=" * 50)
    
    server = EnhancedImageAnalysisServer()
    
    # Demo 1: Analyze a single image with detailed analysis
    print("\n🎯 DEMO 1: Single Image Analysis")
    print("-" * 30)
    
    test_images = [
        "/Users/anthonyturner/Pictures/2squirrels_tree.jpg",
        "/Users/anthonyturner/Pictures/Screenshot 2025-08-18 at 7.50.15 PM.png",
        "/Users/anthonyturner/Pictures/2027-maserati-mc20.png"
    ]
    
    for img_path in test_images:
        image_path = Path(img_path)
        if image_path.exists():
            print(f"\n📁 Analyzing: {image_path.name}")
            analysis = server.advanced_heuristic_analysis(image_path)
            
            # Show different naming styles
            styles = ["descriptive", "technical", "artistic"]
            for style in styles:
                new_name = server.generate_name_from_analysis(analysis, style)
                print(f"  {style.title()}: {new_name}{image_path.suffix.lower()}")
            
            # Show key analysis data
            print(f"  🎨 Color: {analysis.get('color_family', 'unknown')}")
            print(f"  📐 Orientation: {analysis.get('orientation', 'unknown')}")
            print(f"  💾 Size: {analysis.get('size_category', 'unknown')}")
            print(f"  🔍 Type hints: {analysis.get('filename_hints', [])}")
            
            if 'dominant_colors' in analysis:
                colors = analysis['dominant_colors'][:3]
                color_str = ", ".join([f"{c['hex']} ({c['percentage']:.1f}%)" for c in colors])
                print(f"  🌈 Top colors: {color_str}")
            break  # Just show one detailed example
    
    # Demo 2: Directory analysis
    print(f"\n🎯 DEMO 2: Directory Analysis")
    print("-" * 30)
    
    pictures_dir = Path("/Users/anthonyturner/Pictures")
    image_files = server.get_image_files(pictures_dir, False)
    
    print(f"📊 Found {len(image_files)} images in Pictures folder")
    print("\nSuggested names for first 10 images:")
    
    analysis_results = []
    for i, image_path in enumerate(image_files[:10], 1):
        try:
            analysis = server.advanced_heuristic_analysis(image_path)
            new_name = server.generate_name_from_analysis(analysis, "descriptive")
            print(f"[{i:2}] {image_path.name}")
            print(f"     → {new_name}{image_path.suffix.lower()}")
            
            analysis_results.append({
                'original': image_path.name,
                'suggested': f"{new_name}{image_path.suffix.lower()}",
                'color': analysis.get('color_family', 'unknown'),
                'orientation': analysis.get('orientation', 'unknown'),
                'hints': analysis.get('filename_hints', [])
            })
            
        except Exception as e:
            print(f"[{i:2}] ❌ Error analyzing {image_path.name}: {e}")
    
    # Demo 3: Organization analysis
    print(f"\n🎯 DEMO 3: Content Organization Analysis")
    print("-" * 30)
    
    # Categorize images by content
    categories = {}
    for result in analysis_results:
        category = "miscellaneous"
        
        if 'screenshot' in result['hints']:
            category = "screenshots"
        elif 'photo' in result['hints']:
            category = "photos"
        elif result['orientation'] == 'portrait':
            category = "portraits"
        elif result['orientation'] == 'landscape':
            category = "landscapes"
        elif result['color'] in ['black', 'white', 'gray']:
            category = "black_white"
        
        if category not in categories:
            categories[category] = []
        categories[category].append(result['original'])
    
    print("📂 Proposed organization:")
    for category, files in categories.items():
        print(f"  📁 {category.replace('_', ' ').title()} ({len(files)} files)")
        for filename in files[:3]:  # Show first 3 files
            print(f"     • {filename}")
        if len(files) > 3:
            print(f"     • ... and {len(files) - 3} more")
    
    # Demo 4: Metadata extraction
    print(f"\n🎯 DEMO 4: Comprehensive Metadata")
    print("-" * 30)
    
    sample_image = Path("/Users/anthonyturner/Pictures/2squirrels_tree.jpg")
    if sample_image.exists():
        print(f"📄 Extracting metadata from: {sample_image.name}")
        
        try:
            # Basic metadata
            with open(sample_image, 'rb') as f:
                file_size = len(f.read())
            
            print(f"  📏 File size: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
            
            from PIL import Image
            with Image.open(sample_image) as img:
                print(f"  📐 Dimensions: {img.width} x {img.height} pixels")
                print(f"  🎨 Color mode: {img.mode}")
                print(f"  📊 Format: {img.format}")
            
            # Color analysis
            color_analysis = server.analyze_image_colors(sample_image)
            if 'dominant_colors' in color_analysis:
                print(f"  🌈 Dominant color: {color_analysis['color_family']}")
                print(f"  ☀️ Brightness: {color_analysis['brightness']:.2f}")
                print(f"  ⚫ Grayscale: {color_analysis['is_grayscale']}")
        
        except Exception as e:
            print(f"  ❌ Error extracting metadata: {e}")
    
    print(f"\n🎉 Demo completed! The Enhanced Image Analysis MCP Server is ready to use.")
    print("=" * 50)
    print("\n📋 Available MCP Tools:")
    print("  • ai_analyze_directory_images - Batch analyze and rename")
    print("  • ai_analyze_single_image - Single image analysis")
    print("  • extract_comprehensive_metadata - Full metadata extraction")
    print("  • organize_images_by_content - Smart folder organization")
    
    print(f"\n⚙️  To use with Claude Desktop, add this to your config:")
    print('  "image-analysis": {')
    print('    "command": "python3",')
    print(f'    "args": ["/Users/anthonyturner/MCPs/image-analysis-server/enhanced_image_analysis_server.py"],')
    print('    "env": {}')
    print('  }')

if __name__ == "__main__":
    asyncio.run(demo_analysis())