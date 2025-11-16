import streamlit as st
import requests
import base64
import urllib.parse
import time # Import time for delay
import math

st.set_page_config(page_title="Simple Social", layout="wide")

IMAGEKIT_UPLOAD_URL = "https://upload.imagekit.io/api/v1/files/upload"

# --- STATE INITIALIZATION ---

# This logic handles redirects from other pages
if 'page_to_set' in st.session_state:
    # Set the app's "source of truth"
    st.session_state.current_page = st.session_state.page_to_set
    # Clear the request
    del st.session_state.page_to_set

# Initialize session state for pagination and navigation
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'page_size' not in st.session_state:
    st.session_state.page_size = 5
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Feed"


def upload_page():
    st.title("📸 Share Something")

    title = st.text_input("Title:")
    caption = st.text_area("Caption (Content):", placeholder="What's on your mind?")

    uploaded_files = st.file_uploader(
        "Choose media (images/videos)",
        type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'],
        accept_multiple_files=True
    )

    # ---- PREVIEW SELECTED FILES ----
    if uploaded_files:
        st.subheader("Preview")
        cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            with cols[i % 3]:
                if file.type.startswith("image"):
                    st.image(file, use_container_width=True)
                elif file.type.startswith("video"):
                    st.video(file)
        st.markdown("---")

    if st.button("Share", type="primary"):
        if not title.strip():
            st.error("Please enter a title.")
            return

        if not caption.strip() and not uploaded_files:
            st.error("Please add a caption or upload at least one file.")
            return

        artifacts_list = []

        with st.spinner("Uploading..."):
            if uploaded_files:
                progress = st.progress(0)

                for idx, file in enumerate(uploaded_files):

                    # 🔥 GET NEW AUTH PARAMS FOR EACH FILE
                    try:
                        auth_response = requests.get("http://localhost:8000/upload_auth_params")
                        auth_response.raise_for_status()
                        auth_data = auth_response.json()

                        public_key = auth_data["public_key"]
                        token = auth_data["token"]
                        expire = auth_data["expire"]
                        signature = auth_data["signature"]

                    except Exception as e:
                        st.error(f"Failed to get auth params: {e}")
                        return

                    # ---- UPLOAD FILE WITH THAT AUTH ----
                    try:
                        file_bytes = file.getvalue()

                        upload_files = {
                            'file': (file.name, file_bytes, file.type)
                        }
                        upload_data = {
                            'fileName': file.name,
                            'token': token,
                            'expire': expire,
                            'signature': signature,
                            'publicKey': public_key
                        }

                        upload_response = requests.post(
                            IMAGEKIT_UPLOAD_URL,
                            files=upload_files,
                            data=upload_data
                        )
                        upload_response.raise_for_status()
                        upload_result = upload_response.json()

                        artifacts_list.append({
                            "file_id": upload_result.get("fileId"),
                            "file_path": upload_result.get("filePath"),
                            "file_type": upload_result.get("fileType"),
                            "thumbnail_url": upload_result.get("thumbnailUrl"),
                            "url": upload_result.get("url"),
                        })

                    except Exception as e:
                        st.error(f"Upload failed: {e}")
                        return

                    # update progress
                    progress.progress((idx + 1) / len(uploaded_files))

                st.success("All files uploaded!")

            # ---- Create post in backend ----
            json_payload = {
                "title": title,
                "content": caption,
                "artifacts": artifacts_list
            }

            response = requests.post("http://localhost:8000/posts", json=json_payload)

            if response.status_code == 200:
                st.success("Posted! Redirecting to feed...")
                st.balloons()
                time.sleep(1)
                st.session_state.page_to_set = "🏠 Feed"
                st.session_state.page = 1
                st.rerun()
            else:
                st.error(f"Post creation failed ({response.status_code}): {response.text}")



def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params):
    if not transformation_params:
        return original_url

    parts = original_url.split("/")

    # Check if 'tr:' is already in the URL (from thumbnail)
    if any("tr:" in part for part in parts):
        # More complex logic might be needed, but for now, just append
        # This naive append might not be ideal, but it's safer than breaking the URL
        return f"{original_url},tr:{transformation_params}"

    imagekit_id_index = -1
    for i, part in enumerate(parts):
        if "ik.imagekit.io" in part and i + 1 < len(parts):
            imagekit_id_index = i + 1
            break
    
    if imagekit_id_index == -1:
        return original_url # Cannot find imagekit id, return original

    imagekit_id = parts[imagekit_id_index]
    file_path = "/".join(parts[imagekit_id_index+1:])
    base_url = "/".join(parts[:imagekit_id_index+1])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    st.title("🏠 Feed")

    page_num = st.session_state.page
    page_size = st.session_state.page_size

    response = requests.get(f"http://localhost:8000/posts?page={page_num}&page_size={page_size}")
    
    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", [])
        total_posts = data.get("no_of_posts", 0)
        
        # Calculate total pages ourselves
        total_pages = 1
        if total_posts > 0 and page_size > 0:
            total_pages = math.ceil(total_posts / page_size)
        else:
            total_pages = 1 # Default to 1 page if no posts

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.info(post['title'])
                st.markdown(f"User • {post.get('created_at', 'Date not available')[:10]}")

            # Display caption
            content = post.get('content', '')
            if content:
                st.write(content)
                
            # Display artifacts
            if post.get('artifacts'):
                for artifact in post['artifacts']:
                    # Use columns to control media width
                    media_col1, media_col2, media_col3 = st.columns([1, 8, 1])
                    with media_col2:
                        url = artifact.get('url') # This URL now comes from your backend
                        file_type = artifact.get('file_type')

                        if file_type == 'image' and url:
                            transformed_url = create_transformed_url(url, "w-600")
                            st.image(transformed_url)
                        elif file_type == 'video' and url:
                            transformed_url = create_transformed_url(url, "w-600")
                            st.video(transformed_url)
                        else:
                            st.caption(f"Unsupported artifact type: {file_type}")

            st.markdown("")  # Space between posts
        
        st.markdown("---")
        
        # --- PAGINATION CONTROLS ---
        
        # Row 1: Buttons and page number
        nav_cols = st.columns([2, 2, 2])
        
        with nav_cols[0]:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(page_num <= 1)):
                st.session_state.page -= 1
                st.rerun()

        with nav_cols[1]:
            st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page {page_num} of {total_pages}</div>", unsafe_allow_html=True)

        with nav_cols[2]:
            if st.button("Next ➡️", use_container_width=True, disabled=(page_num >= total_pages)):
                st.session_state.page += 1
                st.rerun()
        
        # Row 2: Page size selector
        page_size_cols = st.columns([2, 2, 2])
        with page_size_cols[1]: # Centered
            # Use a non-callback, direct-check method for page size
            new_page_size = st.number_input(
                "Posts per page:", 
                min_value=1, 
                max_value=50, 
                value=st.session_state.page_size,
                key="page_size_input" # Use a key just for the widget
            )
            
            if new_page_size != st.session_state.page_size:
                st.session_state.page_size = new_page_size
                st.session_state.page = 1 # Reset to page 1
                st.rerun()

    else:
        st.error(f"Failed to load feed ({response.status_code}): {response.text}")


# --- SIDEBAR NAVIGATION ---
st.sidebar.title(f"👋 Hi User!")

# We use this as the "source of truth"
current_page_title = st.session_state.current_page
page_options = ["🏠 Feed", "📸 Upload"]
# Find the index of the current page to set the radio button
current_page_index = page_options.index(current_page_title)

# The radio button reads its value from `index` and writes to its `key`
selected_page = st.sidebar.radio(
    "Navigate:", 
    page_options, 
    index=current_page_index,
    key='nav_radio' # A key for the widget itself
)

# If the user's selection changes the state, update our "source of truth"
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.session_state.page = 1 # Reset pagination when changing pages
    st.rerun()


# --- PAGE ROUTING ---
if st.session_state.current_page == "🏠 Feed":
    feed_page()
else:
    upload_page()