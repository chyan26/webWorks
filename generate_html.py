import os
import mimetypes

def generate_post_html(post_title, post_content, media_files):
    """Generates HTML for a single post with Facebook-like media layout."""
    # Add <br> for each line in content
    formatted_content = post_content.replace("\n", "<br>\n")

    # Media HTML with Facebook-like layout
    media_html = ""
    media_count = len(media_files)
    
    if (media_count > 0):
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
                cursor: pointer;
            }}
            .post-media img, .post-media video {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.8);
            }}
            .modal-content {{
                position: relative;
                margin: auto;
                padding: 0;
                width: 80%;
                max-width: 700px;
            }}
            .close {{
                position: absolute;
                top: 10px;
                right: 25px;
                color: white;
                font-size: 35px;
                font-weight: bold;
                cursor: pointer;
            }}
            .modal-media {{
                width: 100%;
                height: auto;
            }}
            .prev, .next {{
                cursor: pointer;
                position: absolute;
                top: 50%;
                width: auto;
                padding: 16px;
                margin-top: -50px;
                color: white;
                font-weight: bold;
                font-size: 20px;
                transition: 0.6s ease;
                border-radius: 0 3px 3px 0;
                user-select: none;
            }}
            .next {{
                right: 0;
                border-radius: 3px 0 0 3px;
            }}
            .prev:hover, .next:hover {{
                background-color: rgba(0,0,0,0.8);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {posts_html}
        </div>
        
        <div id="myModal" class="modal">
            <span class="close">&times;</span>
            <div class="modal-content">
                <img class="modal-media" id="modalImage">
                <video class="modal-media" id="modalVideo" controls></video>
                <a class="prev" onclick="changeSlide(-1)">&#10094;</a>
                <a class="next" onclick="changeSlide(1)">&#10095;</a>
            </div>
        </div>

        <script>
            let currentSlideIndex = 0;
            const modal = document.getElementById("myModal");
            const modalImage = document.getElementById("modalImage");
            const modalVideo = document.getElementById("modalVideo");
            const closeModal = document.getElementsByClassName("close")[0];

            document.querySelectorAll('.media-item img, .media-item video').forEach((item, index) => {{
                item.addEventListener('click', () => {{
                    currentSlideIndex = index;
                    showSlide(currentSlideIndex);
                    modal.style.display = "block";
                }});
            }});

            closeModal.onclick = function() {{
                modal.style.display = "none";
            }}

            window.onclick = function(event) {{
                if (event.target == modal) {{
                    modal.style.display = "none";
                }}
            }}

            function showSlide(index) {{
                const items = document.querySelectorAll('.media-item img, .media-item video');
                const media = items[index];
                if (media.tagName === 'IMG') {{
                    modalImage.src = media.src;
                    modalImage.style.display = "block";
                    modalVideo.style.display = "none";
                }} else if (media.tagName === 'VIDEO') {{
                    modalVideo.src = media.querySelector('source').src;
                    modalVideo.style.display = "block";
                    modalImage.style.display = "none";
                }}
            }}

            function changeSlide(n) {{
                const items = document.querySelectorAll('.media-item img, .media-item video');
                currentSlideIndex = (currentSlideIndex + n + items.length) % items.length;
                showSlide(currentSlideIndex);
            }}

            document.addEventListener('keydown', function(event) {{
                if (event.key === 'ArrowLeft') {{
                    changeSlide(-1);
                }} else if (event.key === 'ArrowRight') {{
                    changeSlide(1);
                }} else if (event.key === 'Escape') {{
                    modal.style.display = "none";
                }}
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