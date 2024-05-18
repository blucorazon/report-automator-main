import sqlite3
from module5.utils import logger

""" 
TODO: 
"""
def readTestTable():
    """
    Executes a predefined SQL query to retrieve data from the database for testing.
    The query is executed against the SQLite database, and returns the 
    last name, first name, and course name of selected students from the first course. 

    The results are returned as a list of tuples, each tuple representing 
    a row from the query result. This data can be used to format the titles of
    report templates for any given batch. 

    The function targets only one course for testing purposes.
    """
    logger.debug("readTestTable():")
    try:
        # Connect to database and create cursor
        logger.debug("# Connect to database and create cursor")
        connection = sqlite3.connect("data/roster.db")
        cursor = connection.cursor()

        # Get the ID of the first course
        logger.debug("# Get the ID of the first course")
        cursor.execute("SELECT id FROM courses ORDER BY id LIMIT 1")
        first_course_id = cursor.fetchone()[0]

        # Query returns last name, first name, and course name for a single course
        sqlite_select_query = """
        SELECT last_name, first_name, courses.name as course_name
        FROM students
        JOIN enrollments ON students.id = enrollments.student_id
        JOIN courses ON enrollments.course_id = courses.id
        WHERE courses.id = ?
        ORDER BY courses.id
        """

        # Run query that reads data from database
        logger.debug("# Run query that reads data from database")
        cursor.execute(sqlite_select_query, (first_course_id,))

        # Read the query result into variable
        logger.debug("# Read the query result into variable")
        record = cursor.fetchall()
    
    except sqlite3.Error as error:
        logger.error(f"Error while connecting to SQLite3: {error}")
        return None, None, None 

    finally:
        if cursor:
            # Close the cursor after using:
            logger.debug("# Close the cursor after using")
            cursor.close()
        if connection:
            # Close the connection after using
            logger.debug("# Close the connection after using")
            connection.close()
            logger.debug("SQLite connection closed successfully.")
        if record:
            return record
        else:
            logger.error("Error. Data not returned in variable 'record'")
            return None, None, None


def readSqliteTable():
    """ Executes a predefined SQL query to retrieve data from the database.
    The query is executed against the SQLite database, and returns the 
    last name, first name, and course names of selected students. 
    
    The results are returned as a list of tuples, each tuple representing 
    a row from the query result. This data can be used to format the titles of
    report templates for any given batch. 

    Add a WHERE keyword when particular courses are needed. Fall and Spring terms
    require more reports, so this keyword will pare results down. 
    """
    logger.debug("readSqliteTable():")
    try:
        # Connect to database and create cursor
        logger.debug("# Connect to database and create cursor")
        connection = sqlite3.connect("data/roster.db")
        cursor = connection.cursor()

        # Query returns last name, first name, and course name
        sqlite_select_query = """ 
        SELECT last_name, first_name, courses.name as course_name
        FROM students
        JOIN enrollments ON students.id = enrollments.student_id
        JOIN courses ON enrollments.course_id = courses.id 
        ORDER BY courses.id;
        """
        # Run query that reads data from database
        logger.debug("# Run query that reads data from database")
        cursor.execute(sqlite_select_query)

        # Read the query result into variable
        logger.debug("# Read the query result into variable")
        record = cursor.fetchall()
    
    except sqlite3.Error as error:
        logger.error(f"Error while connecting to SQLite3: {error}")
        return None, None, None
    
    finally:
        if cursor: 
            # Close the cursor after using
            logger.debug("# Close the cursor after using")
            cursor.close()
        if connection:
            # Close the connection after using
            connection.close() 
            logger.debug("# Close the connection after using")
            logger.debug("SQLite connection closed successfully.")
        if record:
            # Return query result
            return record
        else: 
            logger.error("Error. Data not returned in variable 'record'")
            return None, None, None