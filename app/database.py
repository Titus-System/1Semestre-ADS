import sqlite3

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
        
        cur.execute("CREATE TABLE IF NOT EXISTS registro ( cpf VARCHAR(11) NOT NULL UNIQUE, nome VARCHAR(225) NOT NULL, passord BLOB NOT NULL, PRIMARY KEY (cpf))")
        cur.execute("CREATE TABLE IF NOT EXISTS academico ( id INT NULL UNIQUE, nota_prova INT, nota_quiz INT, posicao INT, cpf VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id))") #insert connection to registro later
        cur.execute("CREATE TABLE IF NOT EXISTS opiniao ( id INT NULL UNIQUE, feedback INT, comment VARCHAR(225), date TIMESTAMP DEFAULT CURRENT_DATE, cpf VARCHAR(11) NOT NULL UNIQUE, PRIMARY KEY (id))") #insert connection to registro later
        
        con.commit()
        
        return True
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
        
    finally:
        con.close()
    
#LOGIN FUNCTTION WILL GO HERE... EVENTUALLY

def insert_grade(cpf: str, nota_prova: int) -> bool:
    """
    Insert or update an employee's grade into the 'academico' table in the database.

    Args:
        cpf (str): The CPF of the employee.
        nota_prova (int): The grade of the employee.

    Returns:
        bool: True if the grade has been saved successfully
              False if the grade has not been saved to the database
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        res = cur.execute("SELECT cpf FROM academico WHERE cpf=?", (cpf, )).fetchone()
        
        if res:
            cur.execute("UPDATE academico SET nota_prova=? WHERE cpf=?", (nota_prova, cpf))
        else:
            cur.execute("INSERT INTO academico (nota_prova, cpf) VALUES (?, ?)", (nota_prova, cpf))
        
        con.commit()
        return True
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        con.close()
        
def insert_feedback(cpf: str, feedback: int, comment: str | None) -> bool:
    """
    Insert or update feedback for an employee in the 'opiniao' table of the database.

    Args:
        cpf (str): The CPF of the employee.
        feedback (float): The feedback value.
        comment (str): Optional comment associated with the feedback.

    Returns:
        bool: True if the feedback was successfully inserted or updated.
              False if the emplyee with the given CPF does not have an entry in the database.
    """    
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        res = cur.execute("SELECT cpf FROM opiniao WHERE cpf=?", (cpf, )).fetchone()
        
        if res:
            cur.execute("UPDATE opiniao SET feedback=?, comment=? WHERE cpf=?", (feedback, comment, cpf))
        else:
            cur.execute("INSERT INTO opiniao (feedback, comment, cpf) VALUES (?, ?, ?)", (feedback, comment, cpf))
        
        con.commit()
        return True
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        con.close()
        
def save_quiz_state(cpf: str, nota_quiz: int, posicao: int) -> bool:
    """
    Save the state of a quiz for an employee in the 'academico' table of the database.

    Args:
        cpf (str): The CPF of the employee.
        nota_quiz (int): The quiz score of the employee.
        posicao (int): The position of the employee in the quiz.

    Returns:
        bool: True if the quiz state was successfully saved, False otherwise.
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        res = cur.execute("SELECT cpf FROM academico WHERE cpf=?", (cpf, )).fetchone()
        
        if res:
            cur.execute("UPDATE academico SET nota_quiz=?, posicao=? WHERE cpf=?", (nota_quiz, posicao, cpf))
            con.commit()
        else:
            return False
        
    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        con.close()
        
def retrieve_data(table: str, columns: str | list[str], cpf: str) -> str | list[dict]:
    """
    Retrieve data from the specified table in the database based on the provided CPF and columns.

    Args:
        table (str): The name of the table from which to retrieve data.
        columns (Union[str, List[str]]): Either a single column name or a list of column names to retrieve.
        cpf (str): The CPF of the employee whose data is to be retrieved.

    Returns:
        Union[str, list[dict]]: If a single column name is provided, returns a string representing the value of
        the selected column for the specified CPF. If a list of column names is provided, returns a list of dictionaries,
        where each dictionary represents a row of data for the specified CPF. If the CPF is not found in the registro table,
        an empty string is returned. If an error occurs during database access, an empty string is returned.    
    """
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        
        res = cur.execute("SELECT cpf FROM registro WHERE cpf=?", (cpf, )).fetchone()
        
        if res:
            if isinstance(columns, list):
                for i in columns:
                    result = []
                    result.append(cur.execute("SELECT ? FROM ? WHERE cpf=?", (columns[i], table, cpf))).fetchone()
                    return result
            else:
                result = cur.execute("SELECT ? FROM ? WHERE cpf=?", (columns, table, cpf)).fetchone()
                return result
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
    
    finally:
        con.close