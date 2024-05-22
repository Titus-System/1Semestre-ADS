import sqlite3

from bcrypt import hashpw, checkpw, gensalt
from json import loads, dumps

def initialize_database() -> bool:
    """
    Connect to the database file 'database.db'. Creates one if none is found.
    Ensures the database contains all the required tables. If not, creates them.
        
    Returns:
        bool: True if database initialization was successful, False otherwise.
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        cur.execute("CREATE TABLE IF NOT EXISTS registro ( username VARCHAR(11) NOT NULL UNIQUE, nome VARCHAR(225) NOT NULL, mail VARCHAR(20) UNIQUE, password BLOB NOT NULL, is_admin BOOLEAN NOT NULL DEFAULT 0, PRIMARY KEY (username))")
        cur.execute("CREATE TABLE IF NOT EXISTS academico ( id INT NULL UNIQUE, nota_prova INT, nota_quiz INT, posicao INT, respostas , username VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id), FOREIGN KEY (username) REFERENCES registro (username))")
        cur.execute("CREATE TABLE IF NOT EXISTS opiniao ( id INT NULL UNIQUE, feedback INT, comment VARCHAR(225), date TIMESTAMP DEFAULT CURRENT_DATE, username VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id), FOREIGN KEY (username) REFERENCES registro (username))")
        
        con.commit()
        
        return True
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
        
    finally:
        if con: con.close()
        
    
def signup(username: str, nome: str, password: str, mail: str, is_admin) -> bool:
    """
    Function Designed to veryfy if the guest already has an account on the site, once a unique username has been provided it will add that to the database.
    
    Args:
        username (str): The username of the employee.
        nome (str): The name of the employee
        password (str): The passowrd desired
        mail (str): The email address of the employee

    Returns:
        bool: True if the account has been successfuly saved.
              False if the username is already associated with another account.
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if not cur.execute("SELECT username FROM registro WHERE username=?", (username,)).fetchone():
            cur.execute("INSERT INTO registro VALUES (?, ?, ?, ?, ?)", (username, nome, mail, hashpw(password.encode("utf-8"), gensalt()), is_admin))
            con.commit()
            return True
        
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        if con: con.close()

def login(username: str, password: str) -> bool:
    """
    Login function, checks credentials against database.
    
    Args:
        username (str): Employee's username
        password (str): Employee's password

    Returns:
        bool: False if username not found or password wrong.
        tupple: Returns True and the username name if the password and username match an entry on the database. Ex.:(True, "John Doe")
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if cur.execute("SELECT username FROM registro WHERE username=?", (username,)).fetchone():
            hashed_password, nome = cur.execute("SELECT password, nome FROM registro WHERE username=?", (username,)).fetchone()
            if checkpw(password.encode("utf-8"), hashed_password):
                return (True, nome)
            else:
                return False
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
 
    finally:
        if con: con.close()

def insert_grade(username: str, nota_prova: int) -> bool:
    """
    Insert or update an employee's grade into the 'academico' table in the database.

    Args:
        username (str): The username of the employee.
        nota_prova (int): The grade of the employee.

    Returns:
        bool: True if the grade has been saved successfully
              False if the grade has not been saved to the database
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if cur.execute("SELECT username FROM registro WHERE username=?", (username,)).fetchone():
            if cur.execute("SELECT username FROM academico WHERE username=?", (username,)).fetchone():
                cur.execute("UPDATE academico SET nota_prova=? WHERE username=?", (nota_prova, username))
                con.commit()
                return True
            else:
                cur.execute("INSERT INTO academico (nota_prova, username) VALUES (?, ?)", (nota_prova, username))
                con.commit()
                return True
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
    
    finally:
        if con: con.close()
        
def insert_feedback(username: str, feedback: int, comment: str | None) -> bool:
    """
    Insert or update feedback for an employee in the 'opiniao' table of the database.

    Args:
        username (str): The username of the employee.
        feedback (float): The feedback value.
        comment (str): Optional comment associated with the feedback.

    Returns:
        bool: True if the feedback was successfully inserted or updated.
              False if the emplyee with the given username does not have an entry in the database.
    """    
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if cur.execute("SELECT nota_prova FROM academico WHERE username=?", (username,)).fetchone():
            if cur.execute("SELECT username FROM opiniao WHERE username=?", (username,)).fetchone():
                cur.execute("UPDATE opiniao SET feedback=?, comment=? WHERE username=?", (feedback, comment, username))
                con.commit()
                return True
            else:
                cur.execute("INSERT INTO opiniao (feedback, comment, username) VALUES (?, ?, ?)", (feedback, comment, username))
                con.commit()
                return True
        else:
            return False
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        if con: con.close()
        
def save_quiz_state(username: str, nota_quiz: int, posicao: int) -> bool:
    """
    Save the state of a quiz for an employee in the 'academico' table of the database.

    Args:
        username (str): The username of the employee.
        nota_quiz (int): The quiz score of the employee.
        posicao (int): The position of the employee in the quiz.

    Returns:
        bool: True if the quiz state was successfully saved, False otherwise.
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if cur.execute("SELECT username FROM registro WHERE username=?", (username,)).fetchone():
            if cur.execute("SELECT username FROM academico WHERE username=?", (username,)).fetchone():
                cur.execute("UPDATE academico SET nota_quiz=?, posicao=? WHERE username=?", (nota_quiz, posicao, username))
                con.commit()
                return True
            else:
                cur.execute("INSERT INTO academico (nota_quiz, posicao, username) VALUES (?, ?, ?)", (nota_quiz, posicao, username))
                con.commit()
                return True
        else:
            return False
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False

    finally:
        if con: con.close()



def save_quiz_answers(answers: object, username: str) -> bool | object:
    '''
    Updates the quiz answers in the 'academico' table.
    If a username is provided it will instead return the data saved on said field
    
    Args:
        answers: The loaded JSON file, no dumping is required.
        username (str): The username of the employee. If you want the function to retrieve data.
        
    Returns:
        bool: True if the quiz answers were successfully saved, False if they were not found in the database.
        object: Returns the loaded JSON file on a python object if a username was provided for the query.
    '''
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
    
        if cur.execute("SELECT respostas FROM academico WHERE username=?",(username,)).fetchone():
            cur.execute("UPDATE academico SET respostas=? WHERE username=?", (dumps(answers), username))
        else:
            cur.execute("INSERT INTO academico (respostas, username) VALUES (?, ?)", (dumps(answers), username))
        con.commit()
        return True
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
    
    finally:
        if con: con.close()


def retrieve_quiz_answers(username: str):
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        data = cur.execute("SELECT respostas FROM academico WHERE username=?",(username,)).fetchone()
        if data:
            return loads(data[0])
        else:
            return False

    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        if con: con.close()


def retrieve_data(table: str, columns: str | list[str], username: str) -> str | list[dict]:   
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if isinstance(columns, list):
            data = cur.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE username=?", (username,)).fetchall()
            if data:
                result = {col: val for col, val in zip(columns, data)}
            else:
                result = ""
        else:
            data = cur.execute(f"SELECT {columns} FROM {table} WHERE username=?", (username,)).fetchone()
            if data:
                result = data[0]
            else:
                result = ""

        return result

    except sqlite3.Error as e:
        print("SQLite error:", e)
       
    finally:
        if con: con.close()


def retrieve_column(table, column):
    #function returns a list with all values of a single column
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
            
        fetch = cur.execute(f"SELECT {column} FROM {table}").fetchall()
        
        if fetch == []:
            return fetch
        
        return [i[0] for i in fetch if i != None]

    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        con.close()


def get_user_info():
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        query = """
        SELECT 
            registro.username, 
            academico.nota_prova, 
            academico.nota_quiz,  
            opiniao.feedback, 
            opiniao.comment
        FROM registro
        LEFT JOIN academico ON registro.username = academico.username
        LEFT JOIN opiniao ON registro.username = opiniao.username
        """
        
        result = cur.execute(query).fetchall()
        
        user_info = {}
        for row in result:
            username = row[0]
            attributes = list(row[1:])
            user_info[username] = attributes
        
        return user_info
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None
    finally:
        con.close()


def update_user_info(table, column, username, update):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    if cur.execute(f"SELECT {column} FROM {table} WHERE username=?",(username,)).fetchone():
        try:
            cur.execute(f"UPDATE {table} SET {column} = ? WHERE username = ?",(update, username))
            con.commit()
            return True
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return None
        finally:
            con.close()
    else:
        return False
