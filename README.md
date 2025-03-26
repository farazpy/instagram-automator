# InstagramManager

InstagramManager is a Python-based automation tool built with `instagrapi`, designed to streamline Instagram account management and interactions. This project is split into two main files: `index.py` for core functionality (posting, liking, following, etc.) and `createSession.py` for session creation and management. Whether you're updating profiles, posting content, or analyzing followers, this tool has you covered.

## Features

- **Session Management** (`createSession.py`)
  - Create and load Instagram sessions
  - Persistent session storage in JSON files

- **Core Functionality** (`index.py`)
  - Update username, name, bio, and profile picture
  - Post photos and stories
  - Like, comment, follow, and unfollow
  - Send direct messages
  - Download media and profile pictures
  - Retrieve followers, following, and posts

- **Additional Capabilities**
  - Automatic dependency installation
  - Detailed logging
  - Image processing support

## Prerequisites

- Python 3.8+
- Instagram account credentials
- Internet connection

## Installation

1. **Download the Files**
   Download the two main scripts from the repository:
   - [`index.py`](./index.py)
   - [`createSession.py`](./createSession.py)

   You can do this manually or via command line:
   ```bash
   wget https://raw.githubusercontent.com/faraz_py/instagram-automator/main/index.py
   wget https://raw.githubusercontent.com/faraz_py/instagram-automator/main/createSession.py
