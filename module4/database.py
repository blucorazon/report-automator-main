import sqlite3
from module5.utils import logger

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
    
    def connect(self):
        """
        Establish a connection to the SQLite database and return a cursor object.

        Returns:
            self.cursor: A cursor object that will be used to interface with the database
        
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return self.cursor
        except sqlite3.Error as error:
            logger.error(f"Error while connecting to SQLite3: {error}")
            return None
    
    def close_and_disconnect(self):
        """Close out a SQLite connection properly by closing the cursor and the connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        """
        Execute a given SQL query and return the results.

        Args:
            query (str): The SQL query to execute.
            params(tuple): Optional parameters to pass with the query.

        Returns:
            list: The results of the query
        """
        cursor = self.connect()
        if cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
            except sqlite3.Error as error:
                logger.error(f"Error while connecting to SQLite3: {error}")
                return None
            finally:
                self.close_and_disconnect()
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
        return self.execute_query(query)