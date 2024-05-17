import sqlite3, bcrypt

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
        
        cur.execute("CREATE TABLE IF NOT EXISTS registro ( username VARCHAR(11) NOT NULL UNIQUE, nome VARCHAR(225) NOT NULL, mail VARCHAR(20) UNIQUE, password BLOB NOT NULL, PRIMARY KEY (username))")
        cur.execute("CREATE TABLE IF NOT EXISTS academico ( id INT NULL UNIQUE, nota_prova INT, nota_quiz INT, posicao INT, username VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id), FOREIGN KEY (username) REFERENCES registro (username))")
        cur.execute("CREATE TABLE IF NOT EXISTS opiniao ( id INT NULL UNIQUE, feedback INT, comment VARCHAR(225), date TIMESTAMP DEFAULT CURRENT_DATE, username VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id), FOREIGN KEY (username) REFERENCES registro (username))")
        
        con.commit()
        
        return True
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
        
    finally:
        con.close()
        
    
def signup(username: str, nome: str, password: str, mail: str) -> bool:
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
            cur.execute("INSERT INTO registro VALUES (?, ?, ?, ?)", (username, nome, mail, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())))
            con.commit()
            return True
        
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        con.close()

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
            hashed_password, nome = cur.execute("SELECT password, nome FROM registro WHERE username=?", (username, )).fetchone()
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                return (True, nome)
            else:
                return False
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
 
    finally:
        con.close()

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
        
        if cur.execute("SELECT username FROM registro WHERE username=?", (username, )).fetchone():
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
        con.close()
        
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
        
        if cur.execute("SELECT nota_prova FROM academico WHERE username=?", (username, )).fetchone():
            if cur.execute("SELECT username FROM opiniao WHERE username=?", (username, )).fetchone():
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
        con.close()
        
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
        
        if cur.execute("SELECT username FROM registro WHERE username=?", (username, )).fetchone():
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
        con.close()

#def retrieve_data(table: str, columns: str | list[str], username: str) -> str | list[dict]:
    """
    Retrieve data from the specified table in the database based on the provided username and columns.

    Args:
        table (str): The name of the table from which to retrieve data.
        columns (Union[str, List[str]]): Either a single column name or a list of column names to retrieve.
        username (str): The username of the employee whose data is to be retrieved.

    Returns:
        [str, list[dict]]: If a single column name is provided, returns a string representing the value of
        the selected column for the specified username. If a list of column names is provided, returns a list of dictionaries,
        where each dictionary represents a row of data for the specified username. If the username is not found in the registro table,
        an empty string is returned. If an error occurs during database access, an empty string is returned.    
    """
#    try:
#        con = sqlite3.connect("database.db")
#        cur = con.cursor()
        
#        if isinstance(columns, list):
#            columns_str = ", ".join(columns)
#            query = f"SELECT {columns_str} FROM {table} WHERE username=?"
#            cur.execute(query, (username,))
#            data = cur.fetchall()
            # Transformar o resultado em uma lista de dicionários
#            result = []
#            for row in data:
#                row_dict = {}
#                for idx, col in enumerate(columns):
#                    row_dict[col] = row[idx]
#                result.append(row_dict)
#        else:
#            cur.execute(f"SELECT {columns} FROM {table} WHERE username=?", (username,))
#            data = cur.fetchone()
#            result = data[0] if data else ""

#       return result
    
#    except sqlite3.Error as e:
#        print("SQLite error:", e)
        
#    finally:
#        con.close()

def retrieve_data(table: str, columns: str | list[str], username: str) -> str | list[dict]:   
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        if isinstance(columns, list):
            data = cur.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE username=?", (username,)).fetchall()
            if data:
                result = {col: val for col, val in zip(columns, data)}
            else:
                result = ''
        else:
            data = cur.execute(f"SELECT {columns} FROM {table} WHERE username=?", (username,)).fetchone()
            if data:
                result = data[0]
            else:
                result = ''

        return result

    except sqlite3.Error as e:
        print("SQLite error:", e)
       
    finally:
        con.close()