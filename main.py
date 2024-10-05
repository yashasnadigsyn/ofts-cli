#!/usr/bin/env python3

# Importing the inbuilt libraries
import os
from os import walk
from pathlib import Path

# Importing the external libraries
import magic

from rich.progress import track
from rich.console import Console

# Importing the local files
from recognize_faces import rec_face_image
from caption_images import tag_image_GIT
import ofts_database as ofts_db

# HOME DIR
home = Path.home()

# DATABASE PATH
DB_PATH = f"{home}/.ofts/ofts.db"

# Create a console object
console = Console()

# MIME object
mime = magic.Magic(mime=True)

# Walk through all the files in the directory
def walk_through_files(
        directory_path: str,
        model_name: str,
        distance_metric: str,
        threshold: float
    ):
    """
        Walk through all the files in the directory
        Args:
            directory_path (str): the directory to walk through
            model_name (str): the name of the model for DeepFace
            distance_metric (str): the distance metric
            threshold (str): the threshold value
        Returns:
            None
    """
    try:
        for (dirpath, dirnames, filenames) in track(walk(directory_path), description="Processing..."):
            for f in filenames:
                # Get the MIME type of the file
                filename = mime.from_file(f"{dirpath}/{f}")

                # Check if the file is a video or an image
                if filename.find("video") != -1:
                    pass
                elif filename.find("image") != -1:
                    # Get the faces and caption of the image
                    faces = rec_face_image(f"{dirpath}/{f}", model_name, distance_metric, threshold)
                    caption = tag_image_GIT(f"{dirpath}/{f}")

                    # Remove all special characters and lowercase everything
                    caption = ''.join(e for e in caption if e.isalnum() or e.isspace())
                    caption = caption.lower()

                    # If DB_PATH doesn't exist create it and add faces, caption to database
                    if not os.path.exists(DB_PATH):
                        ofts_db.initialize_database(db_path=DB_PATH)
                    ofts_db.add_image(f"{dirpath}/{f}", faces, caption, db_path=DB_PATH)
                else:
                    console.print(f"Unknown file type: {f}", style="bold red")
    except Exception as e:
        console.print(e, style="bold red")

def search_image_using_query(query: str):
    """
        Searches for an image in ofts database
        Args:
            query (str): the text to search
        Returns:
            list: a list of tuples
    """
    if os.path.exists(DB_PATH):
        results = ofts_db.search_images(query, DB_PATH)
        return results
    else:
        console.print("You need to run Image tagging and face recognition first.", style="bold red")
        return None

def change_face_name(face_id: str, face_name: str):
    """
        Changes the face_id to face_name in the OFTS database
        Args:
            face_id (str): unique face id,
            face_name (str): actual face name
        Returns:
            list: a list of tuples
    """
    if os.path.exists(DB_PATH):
        results = ofts_db.name_faces(db_path=DB_PATH, face_id=face_id, face_name=face_name)
        return results
    else:
        console.print("You need to run Image tagging and face recognition first.", style="bold red")
        return None

def show_all_images_at_once():
    """
        Shows all the images in the OFTS database
        Args:
            None
        Returns:
            list: a list of tuples
    """
    if os.path.exists(DB_PATH):
        results = ofts_db.show_all_at_once(db_path=DB_PATH)
        return results
    else:
        console.print("You need to run Image tagging and face recognition first.", style="bold red")
        return None
