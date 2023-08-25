# Tech Exam InstaShare
This is the backend of a Python project that uses FastAPI, SQLAlchemy, and encryption modules to provide a user authentication and registration system, along with the ability to upload and download files.

## Characteristics
- User registration and authentication with password encryption.
- Session management and authentication based on JWT tokens.
- Upload files to the server.
- Download files from the server.
- Secure file storage using encryption methods.

## Previous requirements
- Python (version 3.9)
- Pip (version 23.2.1)

## Facility
1. Clone the repository or download the project files.
2. Create and activate a virtual environment (using venv is recommended).
3. Install the project dependencies using the following command:

   bash
   
   pip install -r requirements.txt

## Project Structure
The project is organized as follows:

├── auth.py # Script where the functions related to user authentication are executed 

├── files.py # Script where the respective functions to work with the files are executed

├── InstaShare.py # Main project code

├── requirements.txt # Project requirements

├── schemas.py # Script where the models and schematics are

├── users.py # Script where the respective functions to work with the users are executed

└── usersdb.py # Script where the models and methods of the Sqlalchemy ORM for users and files are 

## Use
1. Run the project backend using the following command:
   
   bash
   
   uvicorn InstaShare:app --reload
3. Access the API through the browser or tools like Postman using the URL http://localhost:8000.

## Contribution
1. Fork this repository.
2. Create a new branch for your contribution.
3. Make your changes and improvements.
4. Make a pull request with your changes.

## Contact
If you have any questions or comments about the project, you can contact me via my email address [izaguirredaniel9712@gmail.com].
