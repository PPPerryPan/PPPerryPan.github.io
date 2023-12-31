from PIL import Image
import os

def clear_exif(image_path):
    image = Image.open(image_path)
    image.save(image_path, exif=b'')

def clear_exif_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            clear_exif(image_path)
            print(f"Cleared Exif for {image_path}")

# 清除当前目录下所有图片的Exif信息
clear_exif_in_directory(os.getcwd())
