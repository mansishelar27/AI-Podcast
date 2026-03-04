import cloudinary
import cloudinary.uploader
import os
from app.core.config import settings
 

# ── Configuration ──────────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key    = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET,
)

 

# ── Upload ─────────────────────────────────────────────────────────────────────
def upload_mp3(file_path: str, public_id: str = None) -> dict:
    """Upload an MP3 file to Cloudinary and return the response."""

 

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

 

    print(f"Uploading '{file_path}' ...")

 

    response = cloudinary.uploader.upload(
        file_path,
        resource_type = "video",   # Cloudinary uses "video" for audio files
        format        = "mp3",
        public_id     = public_id, # optional custom name; omit for auto-generated
    )

 

    print("✅ Upload successful!")
    print(f"   URL       : {response['secure_url']}")
    print(f"   Public ID : {response['public_id']}")
    print(f"   Duration  : {response.get('duration', 'N/A')} seconds")
    print(f"   Size      : {response['bytes'] / 1024:.1f} KB")

 

    return response

 

 

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Change this to the path of your MP3 file
    MP3_FILE = "audio.mp3"

 

    result = upload_mp3(MP3_FILE, public_id="my_audio_file")



