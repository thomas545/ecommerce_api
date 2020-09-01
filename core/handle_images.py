from django.core.files import File
from io import BytesIO
from PIL import Image


def compress_image(image):
    img = Image.open(image)
    img_io = BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(img_io, format="JPEG", quality=70, optimize=True)
    new_img = File(img_io, name=image.name)
    return new_img
