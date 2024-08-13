import argparse
from datetime import datetime
from module2.drive_api import GoogleDriveManager
from module4.database import DatabaseManager
import module4.database as database
import module5.utils as utils

def main(start_year, end_year, term_number, mode):
    """ Generate and organize student report templates.

    This program creates and organizes report templates for students 
    based on a specified school term and mode of operation. It uses
    a predefined report template, retrieves student data from a SQLite 
    database, and generates individual reports sorted by course folders. 

    Args:
        start_year (int): The starting year of the school term. 
        end_year (int): The ending year of the school term. 
        term_number (int): The term number (e.g - 1 for Fall, 2 for Winter, etc.)
        mode (str): The mode of operation, either 'normal' or 'test'.
            - 'normal': Generate reports for all students.
            - 'test': Generate reports for students in a smaller data set. 
    
    Raises:
        sqlite3.Error: If there's an error connecting to the SQLite database. 
    
    Returns:
        None
    """
    start_time = datetime.now()
    utils.log_run_header() # Set header for logging

    # Define the parent folder ID where the main destination folder will be created
    PARENT_FOLDER_ID = "1jZ-d76K-h2nvYGIwHjlsj6fnPJ_c17WZ"

    # Create an instance of GoogleDriveManager
    drive_manager = GoogleDriveManager(PARENT_FOLDER_ID)

    # Create parent destination for reports
    folder_id = drive_manager.create_destination_folder(start_year, end_year, term_number) # Parent directory for created reports
    source_file_id = "1mu6gW8FvtZ1xg6u9Is1BSJVlbF0UUqL_LZcOq2Z8ALc" # Location of report template in Google Drive

    # Retrieve student data from database
    utils.logger.debug("# Retreiving student data from database")
    if mode == "test":
        # TODO: Implement test table in database.py module
        students_data = database.readTestTable()
    else:
        students_data = database.readSqliteTable()
    
    # Create a dictionary to track course folders
    utils.logger.debug("# Creating a dictionary to track course folders")
    course_folders = {}

    if students_data:
        for last_name, first_name, course_name in students_data:
            # Check if course folder exists; if not, create it
            course_folder_id = course_folders.get(course_name)

            # If it doesn't exist, create it and store the ID
            if not course_folder_id:
                course_folder_id = drive_manager.create_course_folder(course_name, folder_id)
                course_folders[course_name] = course_folder_id
                utils.logger.info(f"Folder: '{course_name}' successfully created in parent directory.")

            # Copy the template for current student
            utils.logger.debug("# Copying the template for current student")
            unformatted_report_id = drive_manager.copy_template(course_folder_id, source_file_id)

            # Format the new title
            formatted_title = f"{last_name}, {first_name} ({course_name})"
            drive_manager.format_document_title(unformatted_report_id, formatted_title)
    
    utils.logger.info("Reports generated and sorted successfully.")
    
    # Record the end time
    end_time = datetime.now()
    duration = end_time - start_time

    # Log and Print total run time
    utils.logger.info(f"Total run time: {duration}")

if __name__ == "__main__":    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate and organize student report templates.")
    parser.add_argument("start_year", type=int, help="Starting year of the School term")
    parser.add_argument("end_year", type=int, help="Ending year of the School term")
    parser.add_argument("term_number", type=int, help="Term number")
    parser.add_argument("mode", type=str, nargs="?", default="normal", choices=["normal", "test"],
                        help="Mode of operation (normal or test)")
    args = parser.parse_args()

    # Main program
    main(args.start_year, args.end_year, args.term_number, args.mode)

