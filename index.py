import os
import sys
import time
import json
import requests
from typing import Optional, Dict, List, Union
from datetime import datetime
import logging
from pathlib import Path

# Function to install required packages
def install_packages():
    required = {
        'instagrapi': 'instagrapi',
        'requests': 'requests',
        'colorama': 'colorama',
        'pillow': 'Pillow'  # For image processing
    }
    
    for package, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"Installing {package}...")
            os.system(f"{sys.executable} -m pip install {package}")

# Install packages if not present
install_packages()

from instagrapi import Client
from instagrapi.types import UserShort, Media, Story
from colorama import Style
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instagram_manager.log'
)

class InstagramManager:
    def __init__(self):
        self.session_folder = "session"
        self.profiles_folder = "profiles"
        self.media_folder = "media"
        self.logger = logging.getLogger(__name__)
        
        # Create directories
        for folder in [self.session_folder, self.profiles_folder, self.media_folder]:
            Path(folder).mkdir(exist_ok=True)
            
        self.device_settings = {
            "cpu": "Exynos 2400",
            "dpi": "500dpi",
            "model": "SM-S926B",
            "device": "Samsung Galaxy S24 Ultra",
            "resolution": "3088x1440",
            "app_version": "300.0.0.28.109",
            "manufacturer": "Samsung",
            "version_code": "300001010",
            "android_release": "14.0",
            "android_version": 34
        }
        
        self.user_agent = (
            "Instagram 300.0.0.28.109 iOS (18.0; iPhone15,3; 460dpi; 2796x1290; Apple; iPhone 15 Pro Max; en_US)"
        )

    def create_session(self, username: str, password: str) -> Client:
        """Create or load Instagram session"""
        self.logger.info(f"Initializing session for: {username}")
        
        session_file = os.path.join(self.session_folder, f"{username}.json")
        cl = Client()
        
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            self.logger.info("Session loaded from existing file")
            return cl
            
        cl.set_device(self.device_settings)
        cl.set_user_agent(self.user_agent)
        cl.set_country("IN")
        cl.set_country_code(91)
        
        try:
            cl.login(username, password)
            cl.dump_settings(session_file)
            self.logger.info(f"Session created and saved for {username}")
        except Exception as e:
            self.logger.error(f"Primary login failed: {e}")
            secondary_password = "iMariya#1692"
            try:
                cl.login(username, secondary_password)
                cl.dump_settings(session_file)
                self.logger.info(f"Session created with secondary password for {username}")
            except Exception as e:
                raise Exception(f"Login failed for {username}: {e}")
                
        return cl

    def _load_client(self, username: str) -> Client:
        """Load client from session file"""
        session_file = os.path.join(self.session_folder, f"{username}.json")
        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session file not found for {username}")
        cl = Client()
        cl.load_settings(session_file)
        return cl

    def get_account_info(self, username: str) -> Dict:
        """Retrieve detailed account information"""
        cl = self._load_client(username)
        account_info = cl.account_info()
        
        data = {
            "username": account_info.username,
            "full_name": account_info.full_name,
            "bio": account_info.biography,
            "followers": account_info.follower_count,
            "following": account_info.following_count,
            "posts": account_info.media_count,
            "is_private": account_info.is_private,
            "last_updated": datetime.now().isoformat()
        }
        
        self._update_accounts_file(data)
        return data

    def _update_accounts_file(self, data: Dict) -> None:
        """Update accounts.json with new data"""
        try:
            with open("accounts.json", "r+", encoding="utf-8") as f:
                accounts = json.load(f)
                existing = next((i for i, acc in enumerate(accounts) if acc['username'] == data['username']), None)
                if existing is not None:
                    accounts[existing] = data
                else:
                    accounts.append(data)
                f.seek(0)
                json.dump(accounts, f, indent=4, ensure_ascii=False)
                f.truncate()
        except FileNotFoundError:
            with open("accounts.json", "w", encoding="utf-8") as f:
                json.dump([data], f, indent=4, ensure_ascii=False)

    def change_username(self, username: str, new_username: Optional[str]) -> None:
        """Change account username"""
        if not new_username or username == new_username:
            self.logger.info(f"Username change ignored for {username}")
            return
            
        cl = self._load_client(username)
        cl.account_edit(username=new_username)
        
        old_session = os.path.join(self.session_folder, f"{username}.json")
        new_session = os.path.join(self.session_folder, f"{new_username}.json")
        os.rename(old_session, new_session)
        
        self._update_json_field(username, "username", new_username)
        self.logger.info(f"Username updated to: {new_username}")

    def change_name(self, username: str, new_name: Optional[str]) -> None:
        """Change account display name"""
        if not new_name or username == new_name:
            self.logger.info(f"Name change ignored for {username}")
            return
            
        cl = self._load_client(username)
        formatted_name = f"{new_name} ♠️"
        cl.account_edit(full_name=formatted_name)
        self._update_json_field(username, "full_name", formatted_name)
        self.logger.info(f"Name updated to: {formatted_name}")

    def change_bio(self, username: str, new_bio: Optional[str]) -> None:
        """Change account bio"""
        if not new_bio or username == new_bio:
            self.logger.info(f"Bio change ignored for {username}")
            return
            
        cl = self._load_client(username)
        cl.account_edit(biography=new_bio)
        self._update_json_field(username, "bio", new_bio)
        self.logger.info(f"Bio updated for {username}: {new_bio}")

    def _update_json_field(self, username: str, field: str, value: str) -> None:
        """Update specific field in accounts.json"""
        with open("accounts.json", "r+", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if item["username"] == username:
                    item[field] = value
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()

    def download_profile_picture(self, username: str) -> None:
        """Download profile picture"""
        cl = self._load_client(username)
        data = cl.account_info().dict()
        url = str(data.get("profile_pic_url_hd", data.get("profile_pic_url", "")))
        response = requests.get(url, timeout=10)
        file_path = os.path.join(self.profiles_folder, f"{username}.jpg")
        with open(file_path, "wb") as f:
            f.write(response.content)
        self.logger.info(f"Profile picture downloaded for {username}")

    def change_profile_picture(self, username: str, image_path: str) -> None:
        """Change profile picture"""
        cl = self._load_client(username)
        cl.account_change_picture(image_path)
        self.logger.info(f"Profile picture updated for {username}")

    def send_dm(self, username: str, message: str, receiver: str) -> None:
        """Send direct message"""
        cl = self._load_client(username)
        receiver_id = cl.user_id_from_username(receiver)
        cl.direct_send(message, [receiver_id])
        self.logger.info(f"Message sent to {receiver}: {message}")

    def like_post(self, username: str, url: str) -> None:
        """Like a post"""
        cl = self._load_client(username)
        media_id = cl.media_pk_from_url(url)
        cl.media_like(media_id)
        self.logger.info(f"Post liked from {username}")

    def follow_user(self, username: str, user_id: str) -> None:
        """Follow a user"""
        cl = self._load_client(username)
        cl.user_follow(user_id)
        self.logger.info(f"Followed user {user_id} from {username}")

    def unfollow_user(self, username: str, user_id: str) -> None:
        """Unfollow a user"""
        cl = self._load_client(username)
        cl.user_unfollow(user_id)
        self.logger.info(f"Unfollowed user {user_id} from {username}")

    def post_photo(self, username: str, image_path: str, caption: str = "") -> Media:
        """Post a photo to feed"""
        cl = self._load_client(username)
        # Ensure image is in correct format
        with Image.open(image_path) as img:
            if img.format != 'JPEG':
                img.convert('RGB').save(image_path, 'JPEG')
                
        media = cl.photo_upload(
            path=image_path,
            caption=caption,
            extra_data={"custom_accessibility_caption": f"Photo posted by {username}"}
        )
        self.logger.info(f"Photo posted from {username}: {media.pk}")
        return media

    def post_story(self, username: str, image_path: str) -> Story:
        """Post a story"""
        cl = self._load_client(username)
        story = cl.photo_upload_to_story(
            path=image_path,
            mentions=[],
            links=[],
            hashtags=[]
        )
        self.logger.info(f"Story posted from {username}: {story.pk}")
        return story

    def get_followers(self, username: str, limit: int = 100) -> List[UserShort]:
        """Get list of followers"""
        cl = self._load_client(username)
        user_id = cl.user_id_from_username(username)
        followers = cl.user_followers(user_id, amount=limit)
        self.logger.info(f"Retrieved {len(followers)} followers for {username}")
        return list(followers.values())

    def get_following(self, username: str, limit: int = 100) -> List[UserShort]:
        """Get list of following"""
        cl = self._load_client(username)
        user_id = cl.user_id_from_username(username)
        following = cl.user_following(user_id, amount=limit)
        self.logger.info(f"Retrieved {len(following)} following for {username}")
        return list(following.values())

    def get_user_posts(self, username: str, limit: int = 12) -> List[Media]:
        """Get user's recent posts"""
        cl = self._load_client(username)
        user_id = cl.user_id_from_username(username)
        posts = cl.user_medias(user_id, amount=limit)
        self.logger.info(f"Retrieved {len(posts)} posts for {username}")
        return posts

    def comment_post(self, username: str, media_id: str, comment: str) -> None:
        """Comment on a post"""
        cl = self._load_client(username)
        cl.media_comment(media_id, comment)
        self.logger.info(f"Commented on post {media_id} from {username}: {comment}")

    def download_post(self, username: str, url: str) -> str:
        """Download a post's media"""
        cl = self._load_client(username)
        media_pk = cl.media_pk_from_url(url)
        media_info = cl.media_info(media_pk)
        
        if media_info.media_type == 1:  # Photo
            media_url = media_info.thumbnail_url
        elif media_info.media_type == 8:  # Album
            media_url = media_info.resources[0].thumbnail_url
        else:  # Video
            media_url = media_info.video_url
            
        response = requests.get(media_url, timeout=10)
        file_path = os.path.join(self.media_folder, f"{media_pk}.jpg")
        with open(file_path, "wb") as f:
            f.write(response.content)
        self.logger.info(f"Downloaded media {media_pk} from {username}")
        return file_path

def main():
    manager = InstagramManager()
    
    try:
        with open("accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
    except FileNotFoundError:
        print("accounts.json not found")
        return

    target_user_id = manager._load_client("_kalyani.18_").user_id_from_username('dpradhanbjp')
    
    for account in accounts:
        username = account["username"].strip()
        try:
            # Example usage of various features
            manager.follow_user(username, target_user_id)
            info = manager.get_account_info(username)
            
            # Additional features demonstration
            followers = manager.get_followers(username, limit=10)
            following = manager.get_following(username, limit=10)
            posts = manager.get_user_posts(username, limit=5)
            
            # Uncomment to use these features
            # manager.post_photo(username, "path/to/image.jpg", "Test caption")
            # manager.post_story(username, "path/to/story.jpg")
            # manager.comment_post(username, "media_id", "Nice post!")
            # manager.download_post(username, "post_url")
            
            print(f"Processed {username}: {len(followers)} followers, {len(following)} following")
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {username}: {e}")
            manager.logger.error(f"Error processing {username}: {e}")

if __name__ == "__main__":
    main()