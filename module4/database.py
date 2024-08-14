import sqlite3
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
        self.connection = self.db_manager.connection

    def backup_database(self, backup_path):
        """
        Create a backup of the database before making any term transition changes.

        Args:
            backup_path (str): The file path where the backup will be saved.
        """
        try:
            with sqlite3.connect(backup_path) as backup_conn:
                self.connection.backup(backup_conn)
            utils.logger.info(f"Database backup successfully created at {backup_path}")
        except sqlite3.Error as error:
            utils.logger.error(f"Error while creating database backup: {error}")

    # TODO: Methods for Term Transitioning
        # Backup
        # Delete from database (aka graduate old students)
        # Delete from enrollments (aka the term has finished)
        # Insert into database (aka admit new students)
        # Update enrollments table (aka enroll in new electives)
