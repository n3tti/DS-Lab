import os
from markdownify import markdownify as md

# For now this expects the html binary files to be in html_files directory
# and the conversion is saved in the markdown directory
# TODO: adjust code, to save and access data from db

# Create markdown and decoded_html directories if they don't exist
os.makedirs('html2mdTest/markdown', exist_ok=True)

# Process all files in html_files directory
for filename in os.listdir('html2mdTest/html_files'):
    html_path = os.path.join('html2mdTest/html_files', filename)
    md_path = os.path.join('html2mdTest/markdown', f'{filename}.md')
    
    # Read HTML file
    with open(html_path, 'rb') as html_file:
        html_content = html_file.read().decode('utf-8')

    # Convert HTML to Markdown
    markdown_content = md(html_content)
    
    # Save to markdown file
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)
        
        
    print(f'Converted {filename} to markdown and saved decoded HTML')
