#!/usr/bin/env python3
import sys
sys.path.append('/Users/anthonyturner/MCPs/image-analysis-server')
from enhanced_image_analysis_server import EnhancedImageAnalysisServer
import asyncio
from pathlib import Path

async def test_server():
    server = EnhancedImageAnalysisServer()
    
    # Test single image analysis
    print("🎯 Testing Single Image Analysis...")
    test_image = Path("/Users/anthonyturner/Pictures/2squirrels_tree.jpg")
    if test_image.exists():
        analysis = server.advanced_heuristic_analysis(test_image)
        new_name = server.generate_name_from_analysis(analysis, "descriptive")
        print(f"📁 Original: {test_image.name}")
        print(f"💡 Suggested: {new_name}{test_image.suffix.lower()}")
        print(f"🔍 Analysis: {analysis}")
        print()
    
    # Test directory analysis on Pictures folder (first 5 images)
    print("🎯 Testing Directory Analysis...")
    pictures_dir = Path("/Users/anthonyturner/Pictures")
    image_files = server.get_image_files(pictures_dir, False)[:5]  # Limit to first 5
    
    print(f"📊 Found {len(image_files)} images (showing first 5):")
    
    for i, image_path in enumerate(image_files, 1):
        try:
            analysis = server.advanced_heuristic_analysis(image_path)
            new_name = server.generate_name_from_analysis(analysis, "descriptive")
            print(f"[{i}] {image_path.name} → {new_name}{image_path.suffix.lower()}")
            print(f"    🎨 Color: {analysis.get('color_family', 'unknown')}")
            print(f"    📐 Orientation: {analysis.get('orientation', 'unknown')}")
            print(f"    💾 Size: {analysis.get('size_category', 'unknown')}")
            if analysis.get('filename_hints'):
                print(f"    🔍 Hints: {', '.join(analysis.get('filename_hints', []))}")
            print()
        except Exception as e:
            print(f"[{i}] Error analyzing {image_path.name}: {e}")
    
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_server())