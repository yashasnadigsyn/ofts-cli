# import the built-in libraries
import os, uuid
import warnings
from pathlib import Path
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# import the external libraries
from deepface import DeepFace
from deepface.modules.verification import find_distance
import cv2
import numpy as np
from rich.console import Console

# Look here for more information: https://github.com/serengil/deepface/

# Disable warnings
warnings.filterwarnings("ignore")

# Home directory
home = str(Path.home())

# Known Embeddings directory
if not os.path.exists(f"{home}/.ofts/KNOWN_EMBEDDINGS"):
    os.makedirs(f"{home}/.ofts/KNOWN_EMBEDDINGS")
known_embedding_folder = f"{home}/.ofts/KNOWN_EMBEDDINGS"

# console object
console = Console()

def create_directory_if_not_exists(directory: str):
    """
        Create directory if it doesn't exist
        Args:
            directory (str): the path to the directory
        Returns:
            None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def check_if_known_embedding(
        given_embedding: np.array,
        distance_metric: str,
        threshold: float
    ):
    """
        Check if the given embedding is known
        Args:
            given_embedding (numpy array): the embedding of the given image
            distance_metric (str): the distance metric
            threshold (float): the threshold
        Returns:
            the unique id if the image is known, False otherwise
    """

    # This checks against all the known embeddings even if the distance is less than threshold
    min_distance = float('inf')
    closest_match = False

    # loop through all the known embeddings
    for known_embedding_dir in os.listdir(known_embedding_folder):

        # The whole below code loops through known_embedding directory and checks if the given embedding is known
        # If the given embedding is known, it returns the embedding directory name where all the similar embeddings are stored
        # else it returns False

        # Example: All elon musk embeddings are stored in one directory and all biden embeddings are stored in another directory
        # so that we can loop through all different embeddings of same person and check if the given embedding is known
        # Personally, This improved my accuracy a lot than simply checking against one embedding
        known_embedding_dir_path = os.path.join(known_embedding_folder, known_embedding_dir)
        if os.path.isdir(known_embedding_dir_path):
            for known_embedding in os.listdir(known_embedding_dir_path):
                if known_embedding.endswith(".npy"):
                    known_embedding = np.load(os.path.join(known_embedding_dir_path, known_embedding))

                    # Use the find_distance function from deepface to find the distance between the embeddings
                    result = find_distance(known_embedding, given_embedding, distance_metric=distance_metric)
                    #print(f"Comparing with {known_embedding_dir}: distance = {result}")

                    # If the distance is less than the minimum distance till now, update the minimum distance and the closest match
                    if result < min_distance:
                        min_distance = result
                        closest_match = known_embedding_dir

    # finally, If the minimum distance is less than the threshold, return the closest match

    if min_distance <= threshold:
        return closest_match
    else:
        return False

def get_unique_id(
        given_embedding: np.array,
        distance_metric: str,
        threshold: float
    ):
    """
        Get the unique id for the given embedding
        Args:
            given_embedding (np.array): the embedding of the given image
        Returns:
            the unique id if the image is known, a new unique id otherwise
    """
    check = check_if_known_embedding(given_embedding, distance_metric, threshold)
    if check:
        return check
    else:
        unique_id = str(uuid.uuid4().hex)
        create_directory_if_not_exists(os.path.join(known_embedding_folder, unique_id))
        return unique_id

def rec_face_image(
        image_path: str,
        model_name: str,
        distance_metric: str,
        threshold: str
    ):
    """
        Recognize the face in the given image
        Args:
            image_path (str): the path to the image
            model_name (str): the name of the model for DeepFace
            distance_metric (str): the distance metric
            threshold (float): the threshold value
        Returns:
            the unique id of the recognized face
    """
    console.print(f"[bold blue]IMAGE:[/bold blue] {image_path}", style="")
    try:

        # Read the image and resize it
        # (300, 300) gave me good accuracy opposed to Facent's 224x224 or 256x256
        img = cv2.imread(image_path)
        img = cv2.resize(img, (300, 300))

        # Get all the embeddings of the faces in the image
        given_image_objs = DeepFace.represent(img, model_name = model_name)
        all_faces = []

        # Loop through all the embeddings
        for given_image_obj in given_image_objs:
            given_embedding = given_image_obj["embedding"]

            # Get the unique id for the given embedding
            unique_id = get_unique_id(given_embedding, distance_metric, threshold)
            unique_id_dir = os.path.join(known_embedding_folder, unique_id)

            # Save the embedding
            embedding_path = os.path.join(unique_id_dir, f"{str(uuid.uuid4().hex)}.npy")
            np.save(embedding_path, given_embedding)

            # Save the face image
            x, y, w, h = given_image_obj["facial_area"]["x"], given_image_obj["facial_area"]["y"], given_image_obj["facial_area"]["w"], given_image_obj["facial_area"]["h"]
            roi = img[y:y+h, x:x+w]
            image_path = os.path.join(unique_id_dir, f"{str(uuid.uuid4().hex)}.png")
            cv2.imwrite(image_path, roi)

            # append all the unique ids to a list
            all_faces.append(unique_id)
        return all_faces
    except ValueError as e:
        # if no face is detected, return unknown
        if not "Face could not be detected in numpy array." in str(e):
            print(e)
        return ["unknown"]
