#!/usr/bin/env python3
"""
Fix Indentation Issues in Dashboard
The emoji removal script affected indentation, this will fix it
"""

import re

def fix_indentation():
    """Fix indentation issues caused by emoji removal"""
    
    print("🔧 Fixing indentation issues...")
    
    with open("streamlit_dashboard.py", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    fixed_lines = []
    inside_class = False
    inside_function = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Check for class definition
        if line.strip().startswith('class '):
            inside_class = True
            indent_level = 0
            fixed_lines.append(line)
            continue
            
        # Check for function definition inside class
        if inside_class and line.strip().startswith('def '):
            inside_function = True
            # Function should be indented 4 spaces from class
            fixed_line = '    ' + line.strip() + '\n'
            fixed_lines.append(fixed_line)
            continue
            
        # Check for docstring
        if inside_function and line.strip().startswith('"""'):
            fixed_line = '        ' + line.strip() + '\n'
            fixed_lines.append(fixed_line)
            continue
            
        # Regular content inside function
        if inside_function and line.strip() and not line.startswith('class ') and not line.startswith('def '):
            # Content inside function should be indented 8 spaces
            if line.strip().startswith('return'):
                fixed_line = '        ' + line.strip() + '\n'
            elif line.strip().startswith('if ') or line.strip().startswith('try:') or line.strip().startswith('except'):
                fixed_line = '        ' + line.strip() + '\n'
            elif line.strip().startswith('st.') or line.strip().startswith('pd.') or line.strip().startswith('conn'):
                fixed_line = '            ' + line.strip() + '\n'
            else:
                fixed_line = '        ' + line.strip() + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        # Check if we're leaving a function
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            inside_function = False
            if not line.startswith('class ') and not line.startswith('def '):
                inside_class = False
        
        # Keep original line if no special handling needed
        fixed_lines.append(original_line)
    
    # Write fixed content
    with open("streamlit_dashboard.py", 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)
    
    print("✅ Indentation fixed!")

if __name__ == "__main__":
    fix_indentation()