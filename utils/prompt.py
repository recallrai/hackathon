import os
import re
from jinja2 import Environment, FileSystemLoader

def process_prompt_md(file_path: str, **kwargs) -> str:
    # Set up Jinja environment using directory of markdown file
    template_dir = os.path.dirname(file_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Get template name from file path
    template_name = os.path.basename(file_path)
    
    # Load and render template with variables
    template = env.get_template(template_name)
    content = template.render(**kwargs)
    
    # Remove commented out code
    content = re.sub(r'<!--(.*?)-->\n', '', content, flags=re.DOTALL)
    
    # Replace multiple newlines
    while '\n\n\n' in content:
        content = content.replace('\n\n\n', '\n\n')
        
    return content.strip()
