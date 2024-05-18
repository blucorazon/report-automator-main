from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from module1.auth import authenticate
from module5.utils import logger
import time

"""TODO:
Google Drive Functions:
[x] Create destination folder for all reports in batch
[ ] Create folders for each course in batch 
[x] Create report template copy
[x] Format template copy
- Error handling
    [ ] create_destination_folder
    [ ] copy_template

"""

def create_destination_folder(start_year, end_year, term_number):
    """
    Creates a folder in Google Drive named in the format "startYear_endYear_TtermNumber".

    This function authenticates with Google Drive, builds the drive service, and creates a new folder
    with the specified naming convention based on the provided start year, end year, and term number.
    The folder is created within a predefined parent directory.

    Parameters:
    - start_year (int): The starting year of the folder's content.
    - end_year (int): The ending year of the folder's content.
    - term_number (int): The term number associated with the folder's content.

    Returns:
    - str: The ID of the newly created folder in Google Drive.
    """
    # Verify that the function input is valid
    if not all(isinstance(x, int) for x in [start_year, end_year, term_number]):
        logger.error("All parameters must be integers")
        raise ValueError("All parameters must be integers")
    
    logger.debug("# create_destination_folder({0}, {1}, {2})".format(start_year, end_year, term_number))
    
    # Create folder metadata
    logger.debug("# Create folder metadata")
    folder_name = f"{start_year}_{end_year}_T{term_number}"
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": ["1jZ-d76K-h2nvYGIwHjlsj6fnPJ_c17WZ"]
    }

    # Authenticate and build the drive service
    logger.debug("# Authenticate and build drive service")
    credentials = authenticate()
    drive_service = build('drive', 'v3', credentials=credentials)

    # Create the folder
    for attempt in range(5):
        try:
            logger.debug("# Create the folder")
            folder = drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            # Return folder ID for future use
            logger.debug("# Return folder ID")
            logger.info(f"Folder: {folder_name} created successfully")
            return folder.get('id')
        except HttpError as error:
            logger.error(f"Attempt {attempt + 1}: Failed to create folder. Error: {error}")
            if error.status_code in [429, 500, 502, 503, 504]: # Retryable errors
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
    raise Exception("Failed to create folder after multiple attempts") 

def copy_template(folder_id, source_file_id):
    """ Copies a template in Google Drive to a specific folder identified by folder_id.

    Parameters:
    - folder_id (str): The ID of the Google Drive folder where the template will be copied.
    - source_file_id (str): The ID of the Google Drive file to be copied.

    Returns:
    - str: The file ID of the newly copied file in Google Drive.
    """
    logger.debug(f"copy_template({folder_id}, {source_file_id})")

    # Create file metadata
    logger.debug("# Create file metadata")
    file_metadata = {
        "parents": [folder_id]
    }
    
    # Authenticate and build the drive service
    logger.debug("# Authenticate and build the drive service")
    credentials = authenticate()
    drive_service = build('drive', 'v3', credentials = credentials)

    # Copy the template to the new location
    logger.debug("Copy the template")
    file = drive_service.files().copy(
        fileId=source_file_id, 
        body=file_metadata, 
        fields="id, name"
        ).execute()

    # Log success message
    logger.debug("# Return new file ID")
    logger.debug(f"File '{file.get("name")}' ID ({file.get("id")}) created successfully.")
    
    # Return new file ID
    return file.get('id')

def format_document_title(unformatted_report_id, formatted_title):
    """ Updates blank google doc template and formats it based on SQL database
    """
    logger.debug("format_document_title():")
    try:
        # Authenticate and build the Docs service
        logger.debug("# Authenticate and build the Docs service")
        credentials = authenticate()
        drive_service = build('drive', 'v3', credentials = credentials)

        # Prepare the new metadata for the document
        logger.debug("Prepare the new metadata for the document")
        new_title_metadata = {"name": formatted_title}

        # Update the document title using Drive API
        logger.debug(f"# Update the document title for document ID: {unformatted_report_id}")
        drive_service.files().update(
            fileId=unformatted_report_id,
            body=new_title_metadata
        ).execute()
        logger.info(f"Report created for: {formatted_title}")
    except Exception as e:
        logger.error(f"An error occurred while updating the document title: {e}")

def create_course_folder(course_name, folder_id):
    """ Creates a folder in Google drive according to given course name.
    
    This function authenticates with Google Drive, builds the drive service, and
    creates a new folder with the specified naming convention based on the provided
    course name. 

    Parameters:
    - course_name (str): the name of the course per the student database
    - folder_id (int): The ID of the folder created by "create_destination_folder()"

    Returns:
    - str: The ID of the newly created folder in Google Drive.
    """
    # TODO: Verify that the function input is valid

    logger.debug("create_course_folder():")

    # Authenticate and build the drive service
    logger.debug("# Authenticate and build drive service")
    credentials = authenticate()
    drive_serivce = build('drive', 'v3', credentials=credentials)


    # Create folder metadata
    logger.debug("# Create folder metadata")
    file_metadata = {
        "name": course_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [folder_id]
    }

    # Create the folder
    for attempt in range(5):
        try:
            logger.debug("# Create the folder")
            folder = drive_serivce.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
                
            # Return folder ID
            logger.debug("# Return folder ID")
            logger.debug(f"Folder: {course_name} created successfully in parent: {folder_id}")
            return folder.get('id')
        except HttpError as error:
            logger.error(f"Attempt {attempt + 1}: Failed to create folder. Error: {error}")
            if error.status_code in [429, 500, 502, 503, 504]:
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                raise
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")
            raise
        raise Exception("Failed to create course folder after multiple attempts.")