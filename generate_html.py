import os
import mimetypes
import shutil

def generate_post_html(post_title, formatted_content, media_files):
    """Generates the HTML for a single post."""
    # Convert newlines to <br> tags
    formatted_content = formatted_content.replace('\n', '<br>')
    
    media_count = len(media_files)
    media_html = f'<div class="post-media media-count-{("more-4" if media_count > 4 else media_count)}" data-media-count="{media_count}">'
    
    # Show only first 5 items
    visible_items = media_files[:5]
    remaining_count = len(media_files) - 5 if len(media_files) > 5 else 0
    
    for index, media in enumerate(visible_items):
        # Remove 'html/' from the media file path
        media = os.path.relpath(media, 'html')
        mime_type = "video/mp4" if media.endswith(".mp4") else "image/jpeg"
        if mime_type.startswith("image"):
            media_html += f'''
                <div class="media-item media-item-{index + 1}" data-post-index="{post_title}" {f'data-remaining="{remaining_count}"' if index == 4 and remaining_count > 0 else ''}>
                    <img src="{media}" alt="Media">
                </div>'''
        else:
            media_html += f'''
                <div class="media-item media-item-{index + 1}" data-post-index="{post_title}" {f'data-remaining="{remaining_count}"' if index == 4 and remaining_count > 0 else ''}>
                    <div class="video-container">
                        <video class="media-video" controls>
                            <source src="{media}" type="{mime_type}">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                </div>'''
    
    media_html += '</div>'
    post_title = formatted_content.split('<br>')[0]
    return f'''
    <div class="post" data-post-index="{post_title}">
        <div class="post-title">{post_title}</div>
        {media_html}
        <div class="post-content">{formatted_content}</div>
    </div>
    '''

def generate_html(posts, current_location, valid_locations):
    """Generates the complete HTML page with embedded JavaScript and Facebook-like styling."""
    
    # Generate navigation links
    nav_links = []
    for location in valid_locations:
        is_active = location == current_location
        nav_links.append(
            f'<a href="{location}.html" class="nav-item{" active" if is_active else ""}">{location}</a>'
        )
    nav_html = "\n".join(nav_links)
    
    if not posts:
        posts_html = '''
        <div class="post no-posts">
            <div class="post-content">目前尚無貼文</div>
        </div>
        '''
    else:
        posts_html = "\n".join(posts)
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{current_location}</title>
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
                padding-top: 10px;
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
                white-space: pre-line;
                line-height: 1.5;
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
                height: 100%;
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
            /* Single image */
            .media-count-1 {{
                grid-template-columns: 1fr;
                aspect-ratio: 16/9;
            }}
            /* Two images */
            .media-count-2 {{
                grid-template-columns: repeat(2, 1fr);
                aspect-ratio: 16/9;
            }}
            /* Three images */
            .media-count-3 {{
                grid-template-columns: 2fr 1fr;
                grid-template-rows: repeat(2, 1fr);
                aspect-ratio: 4/3;
            }}
            .media-count-3 .media-item-1 {{
                grid-row: 1 / span 2;
            }}
            /* Four images */
            .media-count-4 {{
                grid-template-columns: repeat(2, 1fr);
                grid-template-rows: repeat(2, 1fr);
                aspect-ratio: 1/1;
            }}
            /* Five or more images */
            .media-count-more-4 {{
                grid-template-columns: repeat(6, 1fr);
                grid-template-rows: repeat(2, 1fr);
                aspect-ratio: 3/2;
            }}
            .media-count-more-4 .media-item-1 {{
                grid-column: span 3;
                grid-row: 1;
            }}
            .media-count-more-4 .media-item-2 {{
                grid-column: span 3;
                grid-row: 1;
            }}
            .media-count-more-4 .media-item-3,
            .media-count-more-4 .media-item-4,
            .media-count-more-4 .media-item-5 {{
                grid-column: span 2;
                grid-row: 2;
            }}
            .media-count-more-4 .media-item-5[data-remaining]::after {{
                content: '+' attr(data-remaining);
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.4);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
            }}
            .nav-bar {{
                position: sticky;
                top: 0;
                background: white;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                padding: 10px 0;
                z-index: 100;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }}
            .nav-item {{
                padding: 8px 16px;
                color: #1c1e21;
                text-decoration: none;
                white-space: nowrap;
                border-radius: 18px;
                margin: 4px;
                transition: background-color 0.2s;
                font-size: 14px;
            }}
            .nav-item:hover {{
                background-color: #f0f2f5;
            }}
            .nav-item.active {{
                background-color: #e7f3ff;
                color: #1877f2;
                font-weight: bold;
            }}
            .no-posts {{
                background-color: white;
                border-radius: 8px;
                text-align: center;
                color: #65676b;
                padding: 20px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="nav-bar">
            {nav_html}
        </div>
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

            document.querySelectorAll('.media-item img, .media-item video').forEach((item) => {{
                item.addEventListener('click', (event) => {{
                    const postContainer = event.target.closest('.post');
                    const postIndex = postContainer.getAttribute('data-post-index');
                    
                    // Filter media items within the same post
                    const postMediaItems = postContainer.querySelectorAll('.media-item img, .media-item video');
                    const postMediaArray = Array.from(postMediaItems);
                    currentSlideIndex = postMediaArray.indexOf(event.target);
                    
                    function showPostSlide(index) {{
                        const media = postMediaArray[index];
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

                    function changePostSlide(n) {{
                        currentSlideIndex = (currentSlideIndex + n + postMediaArray.length) % postMediaArray.length;
                        showPostSlide(currentSlideIndex);
                    }}

                    showPostSlide(currentSlideIndex);
                    modal.style.display = "block";

                    // Override global slide change functions for this post's media
                    window.changeSlide = changePostSlide;
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

            document.addEventListener('keydown', function(event) {{
                if (event.key === 'ArrowLeft') {{
                    window.changeSlide(-1);
                }} else if (event.key === 'ArrowRight') {{
                    window.changeSlide(1);
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
                
                # Ensure the content ends with a new line
                if not post_content.endswith('\n'):
                    post_content += '\n'
                
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
        "西門定點","中山定點","三重定點","板橋定點",
        "蘆洲定點","信義定點","基隆定點","汐止定點",
        "永和定點","中和定點","新店定點","樹林定點",
    ]
    first_html_generated = False
    for location_directory in dir_list:
        download_directory = os.path.join("html/", location_directory)
        print("Processing directories:", download_directory)

        all_posts = []
        if os.path.exists(download_directory) and os.path.isdir(download_directory):
            main(download_directory, all_posts)
        
        # Always generate HTML, regardless of whether posts are found
        html_content = generate_html(all_posts, location_directory, dir_list)
        output_file = f"{download_directory}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        if not all_posts:
            print(f"No posts were found in the specified directory: {download_directory}")

        shutil.copy('icon-play.png', "html/")
        # Copy the first generated HTML file to index.html
        if not first_html_generated:
            shutil.copy(output_file, "html/index.html")
            first_html_generated = True