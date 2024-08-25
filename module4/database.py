import os
import sqlite3
from datetime import datetime
import module5.utils as utils

""" 
TODO: 
[x] Refactor into class structure / Confirm that all functions work still
[ ] Add logging
[ ] Refactor again into ConnectionManager and QueryManager 
[ ] Create queries that will enable more rapid management in between terms
"""
class DatabaseManager:
    def __init__(self, db_path):
        """
        Initialize the DatabaseManager with the path to the student database.

        This constructor sets up the DatabaseManager instance by connecting to the 
        SQLite database with the provided file path and creating a cursor.

        Args:
            db_path (str): The file path of the SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def establish_connection(self):
        """
        Establish a connection to the SQLite database and return a cursor object.

        Returns:
            self.cursor: A cursor object that will be used to interface with the database
        
        """
        try:
            utils.logger.debug("# Calling establish_connection(): ")
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            utils.logger.debug("# SQLite connection established and cursor created")
            return self.cursor
        except sqlite3.Error as error:
            utils.logger.error(f"Error while connecting to SQLite3: {error}")
            return None
    
    def close_and_disconnect(self):
        """Close out a SQLite connection properly by closing the cursor and the connection"""
        utils.logger.debug("# Calling close_and_disconnect():")
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        utils.logger.debug("# SQLite connection and cursor object closed successfully")

    def execute_query(self, query, params=None):
        """
        Execute a given SQL query and return the results.

        Args:
            query (str): The SQL query to execute.
            params(tuple): Optional parameters to pass with the query.

        Returns:
            list: The results of the query
        """
        utils.logger.debug("# Calling execute_query():")
        cursor = self.establish_connection()
        if cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
            except sqlite3.Error as error:
                utils.logger.error(f"Error while connecting to SQLite3: {error}")
                return None
            finally:
                self.close_and_disconnect()
                utils.logger.debug("# SQL query executed successfully.")
                return results

    def select_all_students(self):
        """
        Select all student data from the database and orders them by 
        Course ID. The student names are formatted as follows:
        'Last, First (CourseName)'

        Use this method when student reports need to be generated for every
        student on roster, including LS and MS.
        
        Returns:
            list: The results of the selection.
        """
        query =""" 
        SELECT last_name, first_name, courses.name as course_name
        FROM students
        JOIN enrollments ON students.id = enrollments.student_id
        JOIN courses ON enrollments.course_id = courses.id 
        ORDER BY courses.id;
        """
        utils.logger.debug("# Calling select_all_students():")
        return self.execute_query(query)

    def select_students_test(self):
        """
        Select a small subset of student data to use as a test use this method when 
        testing changes or any time a short test of functionality is needed.

        Returns:
            list: The results of the selection
        """
        query="""
        SELECT last_name, first_name, courses.name as course_name
        FROM students
        JOIN enrollments ON students.id = enrollments.student_id
        JOIN courses ON enrollments.course_id = courses.id 
        ORDER BY courses.id
        LIMIT 10;
        """
        utils.logger.debug("# Calling select_students_test():")
        return self.execute_query(query)
    
class TermTransitionManager:
    def __init__(self, db_manager):
        """
        Initialize the TermTransitionManager with an instance of DatabaseManager and
        establish a connection with the database.

        Args:
            db_manager (DatabaseManager): The instance of the DatabaseManager to use 
                                          for database operations.
        """
        self.db_manager = db_manager
        if self.db_manager.connection is None:
            self.db_manager.establish_connection()
        
        if self.db_manager.connection is None:
            raise ConnectionError("Failed to establish connection to SQLite database")
        
        self.connection = self.db_manager.connection

    def backup_database(self, backup_dir):
        """
        Create a backup of the database before making any term transition changes.

        Args:
            backup_dir(str): The directory where the backup will be saved.
        
        Returns:
            BACKUP_PATH (str): The path to the newly created database backup.
        """
        # Ensure the backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
       
        # Format timestamp of backup filename
        timestamp = datetime.now().strftime("%Y-%m%d_%H-%M-%S")
        backup_filename = f"backup-roster--{timestamp}.db"
        BACKUP_PATH = os.path.join(backup_dir, backup_filename)
        
        try:
            dst = sqlite3.connect(BACKUP_PATH)
        
            with dst:
                if self.db_manager.connection:
                    self.db_manager.connection.backup(dst, pages=-1, name='main', sleep=0.250)
                else:
                    utils.logger.error("No active database connection for backup")
                    return None
            utils.logger.info(f"Database successfully backed up to: {BACKUP_PATH}")
            
        except sqlite3.Error as error:
            utils.logger.error(f"Error during backup: {error}")
            return None
        
        finally:
            dst.close()
        
        return BACKUP_PATH

    def delete_from_database(self):
        """
        Delete all students from the database who are in a specific year.
        Use this method when "graduating" students at the end of their eigth grade year.
        """
        # Find the smallest year (oldest graduating class)
        smallest_year_query = "SELECT MIN(year) FROM students;"
        result = self.db_manager.execute_query(smallest_year_query)
        smallest_year = result[0][0]

        # Delete the students
        delete_students_query="DELETE FROM students WHERE year = ?;"
        self.db_manager.execute_query(delete_students_query, (smallest_year,))

        utils.logger.info(f"Successfully deleted all students from the database from the Class of {smallest_year}")


# TODO: Methods for Term Transitioning
# Delete from database (aka graduate old students)
# Delete from enrollments (aka the term has finished)
# Insert into database (aka admit new students)
# Update enrollments table (aka enroll in new electives)

# Create an instance of DatabaseManager and TermTransitionManager
BACKUP_DIR = '/home/blu/vs-code/report-automator-main/backups'
db_manager = DatabaseManager('/home/blu/vs-code/report-automator-main/data/roster.db')
db_manager.establish_connection()

transition_manager = TermTransitionManager(db_manager)
backup_path = transition_manager.backup_database(BACKUP_DIR)
db_manager.close_and_disconnect()

print(f"Backup successfully created: {backup_path}")