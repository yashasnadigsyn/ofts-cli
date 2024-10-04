# Import the built-in libraries
import os, subprocess
from pathlib import Path
import time
import json

# import the external libraries
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import sqlite3

# Create a console object
console = Console()

# import main files (TF takes a lot of time to load)
#console.print("Importing the local files...", style="bold blue")
with Progress() as progress:
    task1 = progress.add_task("[cyan]Loading the necessary libraries...", total=100)
    from main import walk_through_files, show_all_images_at_once, search_image_using_query, change_face_name
    progress.update(task1, advance=100)

# HOME DIR
home = Path.home()

# Recommended thresholds for each model and distance metric by DeepFace
THRESHOLDS = {
        "VGG-Face": {"cosine": 0.68, "euclidean": 1.17, "euclidean_l2": 1.17},
        "Facenet": {"cosine": 0.40, "euclidean": 10, "euclidean_l2": 0.80},
        "Facenet512": {"cosine": 0.30, "euclidean": 23.56, "euclidean_l2": 1.04},
        "ArcFace": {"cosine": 0.68, "euclidean": 4.15, "euclidean_l2": 1.13},
        "Dlib": {"cosine": 0.07, "euclidean": 0.6, "euclidean_l2": 0.4},
        "SFace": {"cosine": 0.593, "euclidean": 10.734, "euclidean_l2": 1.055},
        "OpenFace": {"cosine": 0.10, "euclidean": 0.55, "euclidean_l2": 0.55},
        "DeepFace": {"cosine": 0.23, "euclidean": 64, "euclidean_l2": 0.64},
        "DeepID": {"cosine": 0.015, "euclidean": 45, "euclidean_l2": 0.17},
        "GhostFaceNet": {"cosine": 0.65, "euclidean": 35.71, "euclidean_l2": 1.10},
}

# Create /home/yashas/.ofts directory if it doesn't exist
if not os.path.exists(f"{home}/.ofts"):
    os.makedirs(f"{home}/.ofts")

# OFTS - A simple Google photos alternative that run in the terminal
# This is the main file for the OFTS CLI application
console.print("OFTS - A simple Google photos alternative that run in the terminal", style="bold green")

# The whole process takes a loooong time, grab a coffee and relax
console.print("NOTE: The whole process takes a loooong time, grab a cup of coffee and relax", style="bold red")

# The OFTS CLI is divided into two parts:
# 1. Image tagging and face recognition
# 2. Image searching
print("\n")
console.print("What do you want to do?", style="bold blue")
console.print("1. Image tagging and face recognition (Do this first)", style="")
console.print("2. Image searching", style="")
console.print("3. Name faces", style="")
choice = input("Enter your choice (1/2/3): ")
print("\n")
# from here, the program goes to line 170

# intial function
def initial_image_tagging():
    """
        The initial image tagging and face recognition process
    """
    # Choose the directory
    console.print("Choose the directory with the images: ", style="bold blue")
    time.sleep(1)

    # Use fzf to search for the directory
    directory_path = os.popen(f"find {home} -type d -print | fzf -q {home}").read().strip()
    console.print(f"Chosen directory: [cyan]{directory_path}[/cyan]", style="")
    print("\n")

    #Choose the Face Detection model
    console.print("Choose the model for face detection: ", style="bold blue")
    models = [
            "VGG-Face",
            "Facenet",
            "Facenet512",
            "OpenFace",
            "DeepFace",
            "DeepID",
            "ArcFace",
            "Dlib",
            "SFace",
            "GhostFaceNet",
        ]
    for i, model in enumerate(models):
        if i == 1:
            console.print(f"{i+1}. {model} (Recommended)", style="")
        else:
            console.print(f"{i+1}. {model}", style="")
    model_name = input("Enter your choice (1-10): ")
    console.print(f"Chosen model: [cyan]{models[int(model_name)-1]}[/cyan]", style="")
    print("\n")

    # Choose the distance metric
    console.print("Choose the distance metric: ", style="bold blue")
    distance_metrics = [
        "cosine",
        "euclidean",
        "euclidean_l2",
    ]
    for i, metric in enumerate(distance_metrics):
        if i == 2:
            console.print(f"{i+1}. {metric} (Recommended)", style="")
        else:
            console.print(f"{i+1}. {metric}", style="")
    distance_metric = input("Enter your choice (1-3): ")
    console.print(f"Chosen distance metric: [cyan]{distance_metrics[int(distance_metric)-1]}[/cyan]", style="")
    print("\n")

    # Choose the distance threshold
    console.print("Choose the distance threshold: ", style="bold blue")

    # using rich to display the thresholds in a table
    rtable = Table(title="Thresholds")
    rtable.add_column("Model", style="bold")
    rtable.add_column("Cosine", style="bold")
    rtable.add_column("Euclidean", style="bold")
    rtable.add_column("Euclidean L2", style="bold")

    for model in THRESHOLDS:
        rtable.add_row(model, str(THRESHOLDS[model]["cosine"]), str(THRESHOLDS[model]["euclidean"]), str(THRESHOLDS[model]["euclidean_l2"]))
    console.print(rtable)
    console.print("These are the recommended thresholds for each model and distance metric by DeepFace. You can choose any value you want.", style="bold red")
    threshold = input("Enter the threshold value: ")
    console.print(f"Chosen threshold: [cyan]{threshold}[/cyan]", style="")
    print("\n")

    # Print the chosen settings
    console.print("These are the chosen settings: ", style="bold blue")
    console.print(f"Directory: [cyan]{directory_path}[/cyan]", style="")
    console.print(f"Model: [cyan]{models[int(model_name)-1]}[/cyan]", style="")
    console.print(f"Distance Metric: [cyan]{distance_metrics[int(distance_metric)-1]}[/cyan]", style="")
    console.print(f"Threshold: [cyan]{threshold}[/cyan]", style="")

    # Create a SQLite database to store the initial data
    conn = sqlite3.connect(f"{home}/.ofts/init_ofts.db")
    c = conn.cursor()

    # Create a table to store the initial data
    c.execute('''CREATE TABLE IF NOT EXISTS init_data (directory text, model text, distance_metric text, threshold real)''')
    conn.commit()

    # Insert the initial data into the table
    c.execute("INSERT INTO init_data VALUES (?, ?, ?, ?)", (directory_path, models[int(model_name)-1], distance_metrics[int(distance_metric)-1], threshold))
    conn.commit()
    conn.close()

    # Run the image tagging and face recognition process
    run_image_tagging(directory_path, models[int(model_name)-1], distance_metrics[int(distance_metric)-1], threshold)

def run_image_tagging(
        directory_path: str,
        model_name: str,
        distance_metric: str,
        threshold: float
    ):
    """
        Run the image tagging and face recognition process
        Args:
            directory_path (str): the directory to walk through
            model_name (str): the name of the model for DeepFace
            distance_metric (str): the distance metric
            threshold (str): the threshold value
        Returns:
            None
    """
    walk_through_files(directory_path, model_name, distance_metric, float(threshold))
    console.print("Completed successfully.", style="bold green")
    console.print("Now, Name the faces to search through images with names and tags", style="bold green")

def image_searching():
    """
        Search for images in OFTS database
        Args:
            None
        Returns:
            None
    """
    console.print("Choose the search method: ", style="bold blue")
    console.print("1. Show all images at once and use fzf to search for image (May take some time to load)", style="")
    console.print("2. Enter a query to search for the image (Faster, but need to run the cli again to search for another query)", style="")
    show_all = input("Enter your choice (1/2): ")
    if show_all.strip() == "1":
        results = show_all_images_at_once()
        fzf_preview(results)
    elif show_all.strip() == "2":
        console.print("Enter your query: ", style="bold blue")
        query = input(">> ")

        # Stop words
        stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "this", "have", "but", "not",
        "they", "his", "her", "she", "him", "you", "your", "yours", "me",
        "my", "i", "we", "our", "ours", "had", "been", "do", "does", "did",
        "doing", "am", "all", "any", "more", "most", "other", "some", "such",
        "no", "nor", "only", "own", "same", "so", "than", "too", "very",
        "can", "will", "just", "don", "should", "now", "linkedin", "instagram",
        "facebook", "join", "us"
    }

        # Remove the stop words from the query
        words = query.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        query =  " ".join(filtered_words)

        # Search for the images using the query
        results = search_image_using_query(query)

        # Display the results
        if len(results) == 0:
            console.print("No images found.", style="bold red")
        else:
            fzf_preview(results)
    else:
        console.print("Invalid choice. Exiting...", style="bold red")

def face_naming():
    """
        Name the faces in the images
    """
    count = 0
    known_embedding_folder = f"{home}/.ofts/KNOWN_EMBEDDINGS"
    for known_embedding in os.listdir(known_embedding_folder):
        for image in os.listdir(f"{known_embedding_folder}/{known_embedding}"):
            if image.endswith(".png"):
                os.system(f"kitty icat {known_embedding_folder}/{known_embedding}/{image}")
                console.print("Name the above face: ", style="bold blue")
                if count == 0:
                    console.print("TIP: If you get the same face twice, name them same. It will help when searching the image.", style="bold red")
                    count += 1
                face_name = input(">> ")
                change_face_name(face_id=known_embedding, face_name=face_name)
                break

    console.print("Names changed successfully!", style="bold green")

def fzf_preview(results: list):
    """
        Preview the image using fzf and kitty icat
        Args:
            query (bool): whether to search for the image using a query
        Returns:
            None
    """
    # Create a list of image paths
    image_paths = [image[0] for image in results]

    # Create a list of faces and caption
    image_metadata = [f"{image[1]}  |  {image[2]}" for image in results]

    # Pipe the image paths to fzf
    #fzf_cmd = ['fzf', '--preview', 'kitty icat --clear --transfer-mode=memory --stdin=no --place=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}@0x0 {}']
    fzf_cmd = [
        'fzf',
        '--cycle',
        '--preview-window',
        'noborder:right:60%',
        '--padding',
        '2',
        '--prompt',
        '> ',
        '--marker',
        '',
        '--pointer',
        '',
        '--separator',
        '',
        '--scrollbar',
        '',
        '--reverse',
        '--info',
        'right',
        '--preview',
        'kitty icat --clear --transfer-mode=memory --stdin=no --place=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}@0x0  "$(echo {} | sed "s/.*||//")"',
        '--delimiter',
        '||',
    ]

    # Create a list of strings containing the image metadata and the corresponding image path
    fzf_input = '\n'.join([f"{metadata}          ||{path}" for metadata, path in zip(image_metadata, image_paths)]).encode('utf-8')


    # handling errors with fzf
    try:
        selected_image = subprocess.run(fzf_cmd, input=fzf_input, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        selected_index = image_paths.index(selected_image.stdout.decode('utf-8').strip().split("||")[1])

        # Display the selected image and its metadata
        os.system(f"kitty icat '{image_paths[selected_index]}'")
        console.print(image_metadata[selected_index], style="bold blue")
    except:
        # print stderr if there is an error
        console.print(selected_image.stderr.decode('utf-8'), style="bold red")
        console.print("No image selected. Exiting...", style="bold red")


# User Choice
if choice == "1":
    # Use the initial database if it already exists
    if os.path.exists(f"{home}/.ofts/init_ofts.db"):
        console.print("Using the existing database", style="bold green")
        console.print("These are the initial settings: ", style="bold blue")

        # Connect to the database and fetch all the data
        conn = sqlite3.connect(f"{home}/.ofts/init_ofts.db")
        c = conn.cursor()
        c.execute("SELECT * FROM init_data")
        data = c.fetchall()
        conn.close()

        # Display the initial settings
        directory_path = data[0][0]
        model_name = data[0][1]
        distance_metric = data[0][2]
        threshold = data[0][3]
        console.print(f"Directory: [cyan]{directory_path}[/cyan]", style="")
        console.print(f"Model: [cyan]{model_name}[/cyan]", style="")
        console.print(f"Distance Metric: [cyan]{distance_metric}[/cyan]", style="")
        console.print(f"Threshold: [cyan]{threshold}[/cyan]", style="")
        console.print(f"NOTE: If you want to change the initial settings, delete the existing database at ({home}/.ofts/init_db) and run the program again.", style="bold red")
        print("\n")

        # run the image tagging and face recognition process
        run_image_tagging(directory_path, model_name, distance_metric, threshold)
    else:
        # if init_db doesn't exist, go through inital config settings
        initial_image_tagging()

elif choice == "2":
    image_searching()

elif choice=="3":
    if not os.path.exists(f"{home}/.ofts/ofts.db"):
        console.print("You need to run Image tagging and face recognition first.", style="bold red")
    else:
        face_naming()
else:
    console.print("Invalid choice. Please enter 1 or 2.", style="bold red")
