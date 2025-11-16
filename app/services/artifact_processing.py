from imagekitio import ImageKit

import os
from dotenv import load_dotenv
load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL")
)

def generate_auth_params():
    params = imagekit.get_authentication_parameters()
    params['public_key'] = os.getenv("IMAGEKIT_PUBLIC_KEY")
    return params

# def generate_auth_params():
#     return imagekit.get_authentication_parameters()
    
def generate_signed_url(file_path, expire_seconds=600):
    signed_url = imagekit.url({
        'path': file_path,
        'signed': True,
        'expire_seconds': expire_seconds 
    })
    
    return signed_url