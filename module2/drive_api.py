from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions
from module1.auth import authenticate
from module5.utils import logger
import time

class GoogleDriveManager:
    def __init__(self, parent_folder_id):
        """
        Initialize the GoogleDriveManager with a specified parent folder ID and 
        authenticate with Google Drive.

        This constructor sets up the GoogleDriveManager instance by storing the 
        ID of the top-level parent folder and authenticating with Google Drive. 
        It builds the drive service for use by other methods of the class.

        Args:
            parent_folder_id (str): The Google Drive folder ID of the top-level 
                                    parent directory where the initial folders 
                                    will be created.
        Raises:
            Exception: If authentication fails or the drive service cannot be built.
        """
        self.parent_folder_id = parent_folder_id

        # Authenticate and build the drive service
        logger.debug("# Authenticating and build drive service")
        self.credentials = authenticate()

        if self.credentials is None:
            logger.error("Failed to obtain credentials; cannot proceed with Google Drive operations")
            raise Exception("Google Drive authentication failed")
        try:
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            logger.debug("# Google Drive service built successfully")
        except google.auth.exceptions.DefaultCredentialsError as e:
            logger.error("Default credentials not found.")
            raise Exception("Google Drive service creation failed") from e

    def _create_folder_metadata(self, folder_name, parent_id):
        """Create metadata for a new folder"""
        return {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]
        }

    def create_destination_folder(self, start_year, end_year, term_number):
        """
        Creates a folder in Google Drive named in the format "startYear_endYear_TtermNumber".

        This method creates a new folder in Google Drive with a specified naming convention based 
        on the provided start year, end year, and term number. The folder is created within the 
        parent directory specified at the class initialization.

        Parameters:
        - start_year (int): The starting year of the folder's content.
        - end_year (int): The ending year of the folder's content.
        - term_number (int): The term number associated with the folder's content.

        Returns:
        - str: The ID of the newly created folder in Google Drive.

        Raises:
        - Exception: If the folder cannot be created after multiple attempts.
        """
        logger.debug(f"# Calling create_destination_folder({start_year}, {end_year}, {term_number}):")
        
        # Create folder metadata
        logger.debug("# Creating folder metadata")
        folder_name = f"{start_year}_{end_year}_T{term_number}"
        file_metadata = self._create_folder_metadata(folder_name, self.parent_folder_id)
  
        # Create the folder
        for attempt in range(5):
            try:
                logger.debug("# Creating the folder")
                folder = self.drive_service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()

                # Return folder ID for future use
                logger.debug("# Returning folder ID")
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
    
    def create_course_folder(self, course_name, parent_id):
        """ 
        Creates a folder in Google Drive according to the given course name.

        This method creates a new folder with the specified naming convention based 
        on the provided course name. The folder is created within the parent directory 
        specified by `parent_id`. If no `parent_id` is provided, it defaults to the 
        top-level parent folder.

        Parameters:
        - course_name (str): The name of the course per the student database.
        - parent_id (str): The ID of the parent folder where the course folder should 
                           be created. Defaults to the top-level parent folder.

        Returns:
        - str: The ID of the newly created folder in Google Drive.

        Raises:
        - Exception: If the folder cannot be created after multiple attempts.
        """

        logger.debug("# Calling create_course_folder():")

        # Create folder metadata
        logger.debug("# Creating folder metadata")
        file_metadata = self._create_folder_metadata(course_name, parent_id)

        # Create the folder
        for attempt in range(5):
            try:
                logger.debug("# Creating the folder")
                folder = self.drive_service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                    
                # Return folder ID
                logger.debug("# Returning folder ID")
                logger.debug(f"Folder: {course_name} created successfully in parent: {parent_id}")
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

    def copy_template(self, folder_id, source_file_id):
        """ Copies a template in Google Drive to a specific folder identified by folder_id.

        This method copies a Google Drive file (template) to a new location specified by the 
        provided folder ID.

        Parameters:
        - folder_id (str): The ID of the Google Drive folder where the template will be copied.
        - source_file_id (str): The ID of the Google Drive file to be copied.

        Returns:
        - str: The file ID of the newly copied file in Google Drive.
        """
        logger.debug(f"# Calling copy_template({folder_id}, {source_file_id}):")

        # Create file metadata
        logger.debug("# Creating file metadata")
        file_metadata = {
            "parents": [folder_id]
        }

        # Copy the template to the new location
        logger.debug("# Copying the template")
        file = self.drive_service.files().copy(
            fileId=source_file_id, 
            body=file_metadata, 
            fields="id, name"
            ).execute()

        logger.debug(f"File '{file.get("name")}' ID ({file.get("id")}) created successfully.")
        return file.get('id')

    def format_document_title(self, unformatted_report_id, formatted_title):
        """ 
        Updates a Google Doc template's title based on provided metadata.

        This method updates the title of a Google Doc identified by its file ID. It uses the
        Google Drive API to set the document's title to the specified `formatted_title`.

        Parameters:
        - unformatted_report_id (str): The ID of the Google Doc whose title will be updated.
        - formatted_title (str): The new title to apply to the Google Doc.

        Raises:
        - Exception: If an error occurs while updating the document title.
        """
        logger.debug(f"Calling format_document_title({unformatted_report_id}, {formatted_title}):")

        try:
            # Prepare the new metadata for the document
            logger.debug("Prepare the new metadata for the document")
            new_title_metadata = {"name": formatted_title}

            # Update the document title using Drive API
            logger.debug(f"# Updating the document title for document ID: {unformatted_report_id}")
            self.drive_service.files().update(
                fileId=unformatted_report_id,
                body=new_title_metadata
            ).execute()
            logger.info(f"Report created for: {formatted_title}")

        except Exception as e:
            logger.error(f"An error occurred while updating the document title: {e}")
            raise
