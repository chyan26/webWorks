import os
import mimetypes
import sys

def generate_post_html(post_title, post_content, media_files):
    """Generates HTML for a single post."""
    media_html = ""
    for media in media_files:
        if media.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            media_html += f'<img src="{media}" alt="{media}" style="max-width: 100%; margin: 10px 0;">\n'
        elif media.lower().endswith(('.mp4', '.webm')):
            media_html += f'''
            <video controls style="max-width: 100%; margin: 10px 0;">
                <source src="{media}" type="{mimetypes.guess_type(media)[0]}">
                Your browser does not support the video tag.
            </video>\n'''
    
    return f'''
    <div class="post">
        <h2>{post_title}</h2>
        <p>{post_content}</p>
        {media_html}
    </div>
    '''

def generate_html(posts):
    """Generates the complete HTML page."""
    posts_html = "\n".join(posts)
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Posts</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 80%;
                margin: 20px auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
            }}
            .post {{
                margin-bottom: 40px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 20px;
            }}
            .post h2 {{
                color: #333;
            }}
            .post p {{
                margin: 10px 0;
                color: #555;
            }}
            img, video {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {posts_html}
        </div>
    </body>
    </html>
    '''

def main(directories):
    """Processes specified directories to generate posts."""
    posts = []
    for base_directory in directories:
        for post_dir in os.listdir(base_directory):
            post_path = os.path.join(base_directory, post_dir)
            if os.path.isdir(post_path):
                content_file = os.path.join(post_path, "content.txt")
                if os.path.exists(content_file):
                    with open(content_file, "r", encoding="utf-8") as f:
                        post_content = f.read()
                    
                    media_files = [
                        os.path.join(post_path, f) 
                        for f in os.listdir(post_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm'))
                    ]
                    post_html = generate_post_html(post_dir, post_content, media_files)
                    posts.append(post_html)
    
    html_content = generate_html(posts)
    output_file = "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML file generated: {output_file}")

if __name__ == "__main__":
    # Ensure directories are provided
    dir_list = [
        "西門定點","中山定點","三重定點","板橋定點",
        "蘆洲定點","信義定點","基隆定點","汐止定點",
    ]

    for directories in dir_list[0:1]:
        main(directories)
