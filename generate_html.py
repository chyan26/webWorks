import os
import mimetypes

def generate_post_html(post_title, post_content, media_files):
    """Generates HTML for a single post with Facebook-like media layout."""
    # Add <br> for each line in content
    formatted_content = post_content.replace("\n", "<br>\n")

    # Media HTML with Facebook-like layout
    media_html = ""
    media_count = len(media_files)
    
    if media_count > 0:
        media_html = f'<div class="post-media media-count-{media_count}" data-media-count="{media_count}">'
        
        for i, media in enumerate(media_files):
            mime_type, _ = mimetypes.guess_type(media)
            
            # Check if it's an image or video and create the appropriate HTML
            if mime_type and mime_type.startswith('image'):
                media_html += f'''
                <div class="media-item media-item-{i+1}">
                    <a href="{media}" target="_blank">
                        <img src="{media}" alt="{media}" class="media-image">
                    </a>
                </div>'''
            elif mime_type and mime_type.startswith('video'):
                media_html += f'''
                <div class="media-item media-item-{i+1}">
                    <a href="{media}" target="_blank">
                        <video class="media-video" controls>
                            <source src="{media}" type="{mime_type}">
                            Your browser does not support the video tag.
                        </video>
                    </a>
                </div>'''
        
        media_html += '</div>'

    return f'''
    <div class="post">
        <div class="post-title">{post_title}</div>
        {media_html}
        <div class="post-content">{formatted_content}</div>
    </div>
    '''

def generate_html(posts):
    """Generates the complete HTML page with embedded JavaScript and Facebook-like styling."""
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
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }}
            .post {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                margin: 15px 0;
                overflow: hidden;
            }}
            .post-title {{
                font-size: 15px;
                font-weight: 600;
                color: #1c1e21;
                padding: 12px 16px;
                border-bottom: 1px solid #eff1f3;
            }}
            .post-content {{
                font-size: 15px;
                color: #1c1e21;
                padding: 12px 16px;
            }}
            .post-media {{
                display: grid;
                grid-gap: 2px;
                overflow: hidden;
            }}
            .post-media .media-item {{
                position: relative;
                overflow: hidden;
            }}
            .post-media img, .post-media video {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            /* Layout for different media counts */
            .media-count-1 .media-item {{ grid-template-columns: 1fr; }}
            .media-count-2 {{ grid-template-columns: 1fr 1fr; }}
            .media-count-3 {{
                grid-template-columns: 2fr 1fr;
                grid-template-rows: repeat(2, auto);
            }}
            .media-count-3 .media-item-1 {{
                grid-column: 1;
                grid-row: 1 / span 2;
            }}
            .media-count-4 {{
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr 1fr;
            }}
            .media-count-more-4 {{
                grid-template-columns: repeat(3, 1fr);
                max-height: 600px;
            }}
            .media-count-more-4 .media-item-4::after {{
                content: '+X';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {posts_html}
        </div>
        
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                const posts = document.querySelectorAll('.post-media');
                
                posts.forEach(mediaContainer => {{
                    const mediaCount = parseInt(mediaContainer.getAttribute('data-media-count'), 10);
                    const mediaItems = mediaContainer.querySelectorAll('.media-item');
                    
                    // Dynamic grid layout
                    if (mediaCount === 1) {{
                        mediaContainer.style.gridTemplateColumns = '1fr';
                    }} else if (mediaCount === 2) {{
                        mediaContainer.style.gridTemplateColumns = '1fr 1fr';
                    }} else if (mediaCount === 3) {{
                        mediaContainer.classList.add('media-count-3');
                    }} else if (mediaCount === 4) {{
                        mediaContainer.style.gridTemplateColumns = '1fr 1fr';
                        mediaContainer.style.gridTemplateRows = '1fr 1fr';
                    }} else if (mediaCount > 4) {{
                        mediaContainer.classList.add('media-count-more-4');
                        
                        // Create a style element to show extra count
                        const extraCount = mediaCount - 4;
                        const styleElement = document.createElement('style');
                        styleElement.textContent = `
                            .media-count-more-4 .media-item-4::after {{
                                content: '+${'extraCount'}';
                            }}
                        `;
                        document.head.appendChild(styleElement);
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''

def main(base_directory, posts):
    """Processes a single directory to generate posts."""
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

if __name__ == "__main__":
    # Specify the directories to process
    dir_list = [
        "西門定點", "中山定點", "三重定點", "板橋定點",
        "蘆洲定點", "信義定點", "基隆定點", "汐止定點",
    ]
    print("Processing directories:", dir_list[0:1])
    
    all_posts = []
    for directory in dir_list[0:1]:  # Adjust slicing as needed
        if os.path.exists(directory) and os.path.isdir(directory):
            main(directory, all_posts)
        else:
            print(f"Directory does not exist or is not a valid directory: {directory}")
    
    if all_posts:
        # Generate a single HTML file in the current directory
        html_content = generate_html(all_posts)
        output_file = "index.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML file generated: {output_file}")
    else:
        print("No posts were found in the specified directories.")