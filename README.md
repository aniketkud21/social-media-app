Here's a comprehensive `README.md` for the provided codebase:

---

# 🚀 Simple Social App

A simple social media application that allows users to create posts with titles, captions, and media (images/videos). It features a FastAPI backend for the API and a Streamlit frontend for an interactive user experience, leveraging ImageKit.io for media management and PostgreSQL for data storage.

## ✨ Key Features

*   **Post Creation**: Users can create new posts with a title, a textual caption, and multiple image or video uploads.
*   **Media Uploads**: Seamlessly handles image and video uploads to ImageKit.io using secure authentication parameters.
*   **Dynamic Feed**: Displays a paginated feed of all posts, showcasing media content with on-the-fly transformations.
*   **API Endpoints**: A robust backend API to manage posts and artifacts.
*   **Database Migrations**: Utilizes Alembic for database schema management.
*   **Seed Data**: Includes a script to populate the database with dummy posts for development and testing.

## 🛠️ Technologies Used

This project is built using a modern Python stack:

*   **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (for building the API).
*   **Web Server**: [Uvicorn](https://www.uvicorn.org/) (ASGI server for FastAPI).
*   **Frontend Framework**: [Streamlit](https://streamlit.io/) (for building the interactive web UI).
*   **Database**: [PostgreSQL](https://www.postgresql.org/) (relational database).
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (Python SQL Toolkit and Object Relational Mapper).
*   **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/en/latest/) (lightweight database migration tool for SQLAlchemy).
*   **Media Management**: [ImageKit.io](https://imagekit.io/) (for cloud-based image/video storage and transformations).
*   **Environment Variables**: [python-dotenv](https://pypi.org/project/python-dotenv/) (for managing environment-specific configurations).
*   **Dependency Management**: [uv](https://github.com/astral-sh/uv) (fast Python package installer and resolver).
*   **Data Validation**: [Pydantic](https://pydantic.dev/) (for data validation and settings management).
*   **Styling/UI Components**: [Rich](https://github.com/Textualize/rich) and [Quill](https://pypi.org/project/quill/) (for enhancing console output and potentially UI components).

##  prerequisites

Before you begin, ensure you have the following installed:

*   **Python**: Version 3.12 or higher. You can verify your version with `python --version`. The project specifies `3.12` in `.python-version`.
*   **PostgreSQL**: A running PostgreSQL database instance.
*   **ImageKit.io Account**: You will need an ImageKit.io account to handle media uploads. Obtain your Public Key, Private Key, and URL Endpoint from your ImageKit dashboard.
*   **uv**: A fast Python package installer and resolver. Install it via pip:
    ```bash
    pip install uv
    ```

## ⚙️ Installation Guide

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd fast-api-tutorial # Replace with actual folder name if different
```

### 2. Set up Python Virtual Environment and Install Dependencies

This project uses `uv` for dependency management.

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (Cmd):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies using uv
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the root of the project directory (where `pyproject.toml` is located) and add the following:

```dotenv
# Database Configuration
# Replace 'your_user', 'your_password', 'localhost', 'your_database_name' with your PostgreSQL credentials
DATABASE_URL="postgresql://your_user:your_password@localhost/your_database_name"

# ImageKit.io Configuration
# Get these from your ImageKit.io dashboard
IMAGEKIT_PUBLIC_KEY="your_imagekit_public_key"
IMAGEKIT_PRIVATE_KEY="your_imagekit_private_key"
IMAGEKIT_URL="your_imagekit_url_endpoint" # e.g., https://ik.imagekit.io/your_imagekit_id
```

**Important Notes:**
*   Ensure your PostgreSQL database `your_database_name` exists.
*   Your `IMAGEKIT_URL` should typically look like `https://ik.imagekit.io/your_imagekit_id`.

### 4. Run Database Migrations

This project uses Alembic for database migrations.

```bash
# Ensure your virtual environment is active and .env is configured
# Initialize the database schema
alembic upgrade head
```

This command will apply all pending migrations, creating the `posts` and `artifacts` tables in your configured PostgreSQL database.

### 5. Seed Initial Data (Optional)

You can populate your database with some dummy posts for testing purposes.

```bash
python seed.py
```

This will add 20 dummy posts to your database.

## 🚀 Usage

The application consists of two main parts: the FastAPI backend API and the Streamlit frontend.

### 1. Start the FastAPI Backend

In your terminal, with the virtual environment activated:

```bash
python main.py
```

This will start the FastAPI server, usually accessible at `http://0.0.0.0:8000`. The `reload=True` option in `main.py` means the server will automatically restart on code changes during development.

### 2. Start the Streamlit Frontend

Open a **new terminal tab/window**, activate your virtual environment, and then run:

```bash
streamlit run frontend.py
```

This will open the Streamlit application in your web browser, typically at `http://localhost:8501`.

## 🌐 API Endpoints

The FastAPI backend exposes the following endpoints:

*   **`GET /`**:
    *   Returns a welcome message.
    *   Example: `http://localhost:8000/`

*   **`GET /posts`**:
    *   Retrieves a paginated list of posts.
    *   Query Parameters:
        *   `page` (optional, default: 1): The page number to retrieve.
        *   `page_size` (optional, default: 5): The number of posts per page.
    *   Example: `http://localhost:8000/posts?page=1&page_size=3`
    *   **Error Handling**: If the requested `page` is out of bounds (e.g., `start >= total_no_posts`), it returns a `404 Not Found` error.

*   **`GET /posts/{public_id}`**:
    *   Retrieves a single post by its `public_id` (UUID).
    *   Example: `http://localhost:8000/posts/a1b2c3d4-e5f6-7890-1234-567890abcdef` (replace with an actual UUID from your database).
    *   **Error Handling**: Returns `404 Not Found` if the post with the given `public_id` does not exist.

*   **`POST /posts`**:
    *   Creates a new post.
    *   Request Body (JSON):
        ```json
        {
          "title": "My Awesome Post",
          "content": "This is a great caption for my new post.",
          "artifacts": [
            {
              "file_id": "image_abc123",
              "file_path": "/default/image_abc123.jpg",
              "file_type": "image",
              "thumbnail_url": "https://ik.imagekit.io/your_ik_id/tr:w-100/default/image_abc123.jpg"
            },
            {
              "file_id": "video_xyz456",
              "file_path": "/default/video_xyz456.mp4",
              "file_type": "video",
              "thumbnail_url": null
            }
          ]
        }
        ```
    *   Returns the created post including its artifacts.
    *   **Error Handling**: Returns `500 Internal Server Error` if post creation fails.

*   **`GET /upload_auth_params`**:
    *   Returns authentication parameters (token, expire, signature, public\_key) required to upload files directly to ImageKit.io.
    *   Example: `http://localhost:8000/upload_auth_params`

*   **`GET /signed_url`**:
    *   Generates a signed URL for a given ImageKit.io file path.
    *   Query Parameter:
        *   `file_path` (string, required): The ImageKit.io path of the file (e.g., `/default/image_abc123.jpg`).
    *   Example: `http://localhost:8000/signed_url?file_path=/default/my_image.jpg`

## 🎨 Frontend Application (Streamlit)

The Streamlit application (`frontend.py`) provides a user-friendly interface to interact with the backend API.

*   **Navigation**: Use the sidebar to switch between "üè† Feed" and "üì∏ Upload".
*   **üì∏ Upload Page**:
    *   Allows entering a `Title` and `Caption`.
    *   Supports uploading multiple `images` or `videos`.
    *   Clicking "Share" will upload media to ImageKit.io and then create a post via the backend API.
*   **üè† Feed Page**:
    *   Displays all posts from the backend, including their associated media.
    *   Images/videos are displayed with a transformation `w-600` (width 600px) applied by ImageKit.io.
    *   **Pagination**: Navigate through pages using "Previous" and "Next" buttons. Adjust "Posts per page" to change the number of items displayed per page.

## 📂 Project Structure

```
.
├── alembic/                          # Alembic migration scripts
│   ├── versions/                     # Individual migration files
│   │   ├── 03d697fd463a_...py
│   │   ├── 1013558eed03_...py
│   │   ├── baf4a9bd9845_...py
│   │   └── dc01f2dc07bf_...py
│   ├── README                        # Alembic README
│   ├── env.py                        # Alembic environment setup
│   └── script.py.mako                # Mako template for new migration scripts
├── app/                              # Main application source code
│   ├── config/                       # Application configuration
│   │   └── database.py               # Database connection and session management
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── artifact.py               # Artifact model (for media)
│   │   └── post.py                   # Post model
│   ├── services/                     # Business logic and external service interactions
│   │   ├── artifact_processing.py    # ImageKit.io integration
│   │   ├── artifacts.py              # CRUD operations for Artifacts
│   │   └── posts.py                  # CRUD operations for Posts
│   ├── app.py                        # FastAPI application instance and API endpoints
│   └── schemas.py                    # Pydantic schemas for request/response validation
├── .python-version                   # Specifies Python version (e.g., pyenv)
├── README.md                         # Project README (this file)
├── alembic.ini                       # Alembic configuration file
├── frontend.py                       # Streamlit frontend application
├── main.py                           # Entry point for running the FastAPI backend
├── pyproject.toml                    # Project metadata and dependencies (for uv)
├── seed.py                           # Script to populate the database with dummy data
└── uv.lock                           # uv dependency lock file
```

## 📝 Contributing

No specific contributing guidelines were found in the codebase. However, feel free to fork the repository, make your changes, and submit a pull request.

## 📄 License

No license information was explicitly found in the codebase.

---