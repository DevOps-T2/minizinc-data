import mysql.connector as mysql
from models import File

SERVICE_NAME = 'minizinc-data'
MYSQL_READ_DB_URL = f'{SERVICE_NAME}-mysql-read'
MYSQL_WRITE_DB_URL = f'{SERVICE_NAME}-mysql-0.{SERVICE_NAME}-headless'


read_config = {
    'user': 'root',
    'host': MYSQL_READ_DB_URL,
    'database': 'Default'
}


write_config = {
    'user': 'root',
    'host': MYSQL_WRITE_DB_URL,
    'database': 'Default'
}


def get_files(userID):
    # Get files for userid
    query = """SELECT userID, fileName, fileUUID FROM files WHERE userID = %s"""
    result = __read_prep_statement(query, (userID))
    return result


def delete_files(userID):
    # delete all files associated with userid
    query = """DELETE FROM files WHERE userID = %s"""
    result = __write_prep_statement(query, (userID))
    return result


def get_file(userID, fileUUID):
    # get the file with given userid and fileuuid
    query = """SELECT userID, fileName, fileUUID FROM files WHERE userID = %s AND fileUUID = %s"""
    result = __read_prep_statement(query, (userID, fileUUID))
    return result

def create_file(file: File):
    # Insert the given file
    query = """INSERT INTO files (userID, fileName, fileUUID) VALUES (%s, %s, %s)"""
    result = __write_prep_statement(query, (file.userID, file.fileName, file.fileUUID))
    return result


def delete_file(userID, fileUUID):
    # delete file with given userid and fileuuid
    query = """DELETE FROM files WHERE userID = %s AND fileUUID = %s"""
    result = __write_prep_statement(query, (userID, fileUUID))
    return result


def file_exists(userID, fileUUID):
    # Returns true if the given fileuuid exists in the database
    query = """SELECT * FROM files WHERE userID = %s AND fileUUID = %s"""
    result = __read_prep_statement(query, (userID, fileUUID))
    return len(result) > 0


def user_exists(userID):
    # Returns true of the given userID exists in the database
    query = """SELECT * FROM files WHERE userID = %s"""
    result = __read_prep_statement(query, (userID))
    return len(result) > 0


def __write_prep_statement(query, values):
    connection = mysql.connect(**write_config)
    return __execute_prep_statement(connection, query, values)    


def __read_prep_statement(query, values):
    connection = mysql.connect(**read_config)
    return __execute_prep_statement(connection, query, values)  


def __execute_prep_statement(connection, query, values):
    cursor = connection.cursor(prepared=True)
    response = cursor.execute(query, values)
    result = list(response)
    cursor.close()
    connection.close()
    return result
