"""Public item image file serving (BIZ-26). Filenames are unguessable UUIDs."""

from flask import Blueprint

from app.controllers import item_image_controller

item_images_bp = Blueprint("item_images", __name__, url_prefix="/item-images")


@item_images_bp.get("/files/<filename>")
def serve_item_image(filename):
    return item_image_controller.serve_item_image(filename)
