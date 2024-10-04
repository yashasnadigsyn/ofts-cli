# import the necessary libraries
import sqlite3
import os
from rich.console import Console

# Create a console object
console = Console()

def initialize_database(db_path: str):
     """
        Initializes a new SQLite database with a table named "photos"
        The table has three columns: "image_path", "faces", and "caption".
        Args:
            db_path (str): The path to the SQLite database file.
        Returns:
            None
    """
     conn = None
     try:
         conn = sqlite3.connect(db_path)
         cursor = conn.cursor()

         # Create the photos table
         cursor.execute('''
         CREATE VIRTUAL TABLE IF NOT EXISTS photos USING fts5(
             image_path,
             faces,
             caption,
         );
         ''')
         conn.commit()
     except sqlite3.Error as e:
         print(f"An error occurred: {e.args[0]}")
     finally:
         if conn:
             conn.close()

def add_image(
        image_path: str,
        faces: list,
        caption: str,
        db_path: str
    ):
    """
        Adds image_path, faces, and caption to the database.
        Args:
            image_path (str): The path to the image file.
            faces (list): A list of faces detected in the image.
            caption (str): A caption for the image.
            db_path (str): The path to the SQLite database file.
        Returns:
            None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Convert the list of faces to string
        faces_str = ' '.join(faces)

        # Insert the image data into the database
        try:
            cursor.execute('''
            INSERT INTO photos (image_path, faces, caption) VALUES (?, ?, ?)
            ''', (image_path, faces_str, caption))
            conn.commit()
        except sqlite3.IntegrityError:
            console.print(f"Image at '{image_path}' already exists in the database.", style="bold red")
    except sqlite3.Error as e:
        print(f"An error occurred: {e.args[0]}")
    finally:
        if conn:
            conn.close()

def search_images(
        query: str,
        db_path: str
    ):
    """
        Searches the database for images that match the query.
        Args:
            query (str): The search query.
            db_path (str): The path to the SQLite database file.
        Returns:
            list: A list of tuples containing the image_path, faces, and caption of the matching images.
    """
    conn = None
    results = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Using FTS5 to search the database
        cursor.execute('''
        SELECT image_path, faces, caption
        FROM photos
        WHERE photos MATCH ?
        ''', (query,))

        results = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e.args[0]}")
    finally:
        if conn:
            conn.close()
    return results

def name_faces(db_path: str, face_id: str, face_name: str):
     """
          Changes the face_id to face_name in the database.
          Args:
               db_path (str): The path to the SQLite database file.
               face_id (str): The face_id to change.
               face_name (str): The new face_name.
          Returns:
               None
     """
     conn = None
     try:
          conn = sqlite3.connect(db_path)
          cursor = conn.cursor()

                    # Retrieve the rows that need to be updated
          cursor.execute('''
          SELECT image_path, faces, caption
          FROM photos
          WHERE faces LIKE ?
          ''', ("%"+face_id+"%",))

          rows = cursor.fetchall()

          # Update the faces column for each row
          for row in rows:
              image_path, faces, caption = row
              new_faces = faces.replace(face_id, face_name)

              # Update the row
              cursor.execute('''
              DELETE FROM photos
              WHERE image_path = ? AND faces = ?
              ''', (image_path, faces))

              cursor.execute('''
              INSERT INTO photos (image_path, faces, caption)
              VALUES (?, ?, ?)
              ''', (image_path, new_faces, caption))

          conn.commit()
     except sqlite3.Error as e:
          print(f"An error occurred: {e.args[0]}")
     finally:
          if conn:
               conn.close()

def show_all_at_once(db_path: str):
     """
          Shows all the rows in the database at once.
          Args:
               db_path (str): The path to the SQLite database file.
          Returns:
               None
     """
     conn = None
     try:
          conn = sqlite3.connect(db_path)
          cursor = conn.cursor()

          # Retrieve all the rows
          cursor.execute('''
          SELECT image_path, faces, caption
          FROM photos
          ''')

          rows = cursor.fetchall()
          return rows
     except sqlite3.Error as e:
          print(f"An error occurred: {e.args[0]}")
     finally:
          if conn:
               conn.close()
