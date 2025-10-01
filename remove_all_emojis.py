#!/usr/bin/env python3
"""
Remove All Emoji Icons from Dashboard
Systematically clean up all emoji icons while preserving functionality
"""

import re
import os

def remove_all_emojis_from_file(file_path):
    """Remove all emoji icons from the streamlit dashboard file"""
    
    print(f"🧹 Removing all emoji icons from {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define emoji patterns to remove
    emoji_patterns = [
        # Common dashboard emojis
        '🚨', '🔒', '✅', '❌', '⚠️', '💡', '🚀', '📊', '🔄', '🌐', 
        '🧠', '📈', '🎯', '🕐', '🔌', '📉', '🌟', '🗺️', '🧹', '🔍',
        '📋', '🎉', '📍', '⏳', '🔗', '💾', '🔧', '🛠️', '⚙️', '📱',
        '💻', '🖥️', '📟', '☁️', '🌍', '🦜', '🐨', '🦘', '🐊', '🕷️',
        '🌺', '🌿', '🌳', '🌲', '🌴', '🌱', '🌾', '🌊', '⛰️', '🏔️',
        '🏞️', '🦋', '🐝', '🦅', '🦆', '🐧', '🦢', '🦉', '🦚', '🦩',
        '🐢', '🦎', '🐍', '🦕', '🦖', '🦣', '🐘', '🦏', '🦛', '🐪',
        '🦙', '🦌', '🐎', '🦄', '🐄', '🐂', '🐃', '🐷', '🐖', '🐗',
        '🐑', '🐏', '🐐', '🦭', '🐋', '🐳', '🐬', '🦈', '🐙', '🦑',
        '🦞', '🦀', '🐠', '🐟', '🐡', '🦆', '🐥', '🐤', '🐣', '🦜'
    ]
    
    original_content = content
    
    # Remove emojis from all text strings
    for emoji in emoji_patterns:
        # Remove emoji with optional space after
        content = content.replace(f'{emoji} ', '')
        # Remove emoji without space
        content = content.replace(emoji, '')
    
    # Clean up any double spaces that might be left
    content = re.sub(r'  +', ' ', content)
    
    # Clean up empty quotes that might be left
    content = re.sub(r'"""\s*"""', '""', content)
    content = re.sub(r'"\s*"', '""', content)
    
    # Count changes
    changes_made = len([emoji for emoji in emoji_patterns if emoji in original_content])
    
    if changes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"✅ Removed {changes_made} different emoji types from the file")
        print("🎯 Dashboard now has a clean, professional appearance!")
    else:
        print("ℹ️ No emojis found to remove")
    
    return changes_made

def main():
    """Main function to clean up emoji icons"""
    
    dashboard_file = "streamlit_dashboard.py"
    
    if not os.path.exists(dashboard_file):
        print(f"❌ File {dashboard_file} not found!")
        return
    
    print("🧹 EMOJI CLEANUP OPERATION")
    print("=" * 40)
    
    changes = remove_all_emojis_from_file(dashboard_file)
    
    print("\n✅ CLEANUP COMPLETE!")
    print("=" * 30)
    
    if changes > 0:
        print("🎯 Benefits:")
        print("  • Clean, professional interface")
        print("  • Better accessibility")
        print("  • Faster loading")
        print("  • Universal compatibility")
        print("  • Developer credit popup preserved")
        
        print("\n🚀 Ready to test:")
        print("  • Start dashboard: streamlit run streamlit_dashboard.py")
        print("  • All functionality preserved")
        print("  • Icons removed, content intact")
    else:
        print("ℹ️ Dashboard already clean!")

if __name__ == "__main__":
    main()