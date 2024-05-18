# Student Report Automator

## Description
This project is designed to facilitate the report generation process for educators using Google
APIs. From a database, templates for student reports are created and then organized within a user's
Google Drive. 

### Video Demo: [<Video Demo>](https://youtu.be/owpr9zTJKWk)

## Technologies and Libraries
- Python
- Google Drive API
- Google Sheets API
- Google Docs API
- SQLite3

## Project details
My project is made up of a number of modules that handle the OAuth authentication, API requests, database management, logging,
and various helper functions. 

- Main Program Flow
  The program takes up to four command line arguments; three are integers and will be formatted into the parent directory's
  title. They label the numbers representing the starting year of the school term, the ending year, and the term number (1-3). If
  no fourth command line argument is passed, the default mode is to run the program in normal mode. If the user inputs 'test' as 
  their mode, they can run the program on a smaller data set for testing purposes. Prior versions of the program featured a hard
  coded method of naming the parent directory. 

  The program then checks for valid credentials to access the user's Google Drive. If there is no record of the credentials or if they 
  are invalid, then the Oauth 2.0 authentication occurs in the browser. The credentials are stored and the program creates 
  the parent directory in which all reports will be organized. A dictionary is used to track the course folders as they get created to 
  prevent duplicates. A course folder is created for every course in the batch and the students who are enrolled in that course have 
  a report template copied, formatted with their information, and then organized in the propers directory.

### Module 1 - Authorization
This module handles the OAuth 2.0 authentication flow at the beginning of the program. It attempts to load the 
credentials from a file; if for some reason they are lost, expired or invalid, it initiates an authentication flow
in the browser to obtain new credentials. The valid credentials are then saved securely for future use. 

### Module 2 - Google Drive API
All functions dealing with the Google Drive API are inside this module. It enables the creation of folders in the 
user's Google Drive. The user is able to copy report templates for each student and format the titles according to 
their rosters. 

### Module 4 - Database
There are a number of SQLite calls that need to be made throughout the program, especially if there is a large 
number of students in the batch. This module handles all the queries to the database. 

### Module 5 - Logging
This module is set up for logging. There is both a console logger as well as a handler for keeping rotating log files. 

### Database
The database for this project was made in SQLite3. It contains a main table with student data, as well as two other tables
containing information on the names of courses and the enrollments of those courses, respectively. 

### Features for Future Development
There are currently few optimizations within the database process (management, etc.). I would like some more automation in the
management of the database. Currently DB Browser is how I run the database, removing and adding students by way of SQL queries that
I have written, but not implemented into the main program flow yet. 

I would like to be able to use this in conjunction with Blackbaud's API and access the actual data on my teacher account. This will
enable me to dynamically load the student information into my program as it formats the template titles. This will naturally demand 
a deep look at the security of the program and how it handles the sensitive data.

Another feature I want to add is populating the templates with the course description that I will use for the course. These 
get edited from time to time, but it is rare. To have these populated in a student template automatically will save the manual
copy / paste process. 
