import sqlite3
def initialize_database():
    """
        Connect to the database file 'database.db'. Creates one if none is found.
        Ensure the database contains a 'registro' table. If not, create one with the following schema:

        TABLE "registro"
            "cpf" TEXT NOT NULL UNIQUE,
            "nome" TEXT NOT NULL,
            "nota" INT NOT NULL,
            "feedback" FLOAT,
            "comment" TEXT,
            PRIMARY KEY ("cpf")

        This function initializes the database connection and cursor globally.
        
        Returns:
        None
    """
    global con; con = sqlite3.connect("database.db")
    global cur; cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE name='registro'")
    if not res.fetchone(): #Creates the 'registro' table if it doesn't exist.
        cur.execute('''CREATE TABLE "registro" 
                    ("cpf" TEXT NOT NULL UNIQUE,
                    "nome" TEXT NOT NULL,
                    "nota" INT NOT NULL,
                    "feedback" FLOAT,
                    "comment" TEXT,
                    PRIMARY KEY ("cpf")
                    )
                    ''')
def insert_grade(cpf, nome, nota):
    """
    Insert or update a grade record into the 'registro' table in the database.

    Parameters:
    cpf (str): The CPF of the employee.
    nome (str): The name of the employee.
    nota (int): The grade of the employee.

    Returns:
    None
    """
    global con, cur
    data = (cpf, )
    res = cur.execute("SELECT cpf FROM registro WHERE cpf=?", data)
    if res.fetchone() is not None: #Determines if the employee already has a cpf entry, only altering the grade instead of adding a new entry. (It'll be useful if we implement an user login system... Honestly I'd just borrow peoples IDs and make them get 0 at the test hehehe)
        data = (nota, cpf)
        cur.execute("UPDATE registro SET nota=? WHERE cpf=?", data)
    else:
        data = (cpf, nome, nota)
        cur.execute("INSERT INTO registro (cpf, nome, nota) VALUES(?, ?, ?)", data)
    con.commit()
def insert_feedback(cpf, feedback, comment):
    """
    Insert or update feedback for a student in the 'registro' table of the database.

    Parameters:
    cpf (str): The CPF of the employee.
    feedback (float): The feedback value.
    comment (str): Optional comment associated with the feedback.

    Returns:
    bool: True if the feedback was successfully inserted or updated.
          False if the emplyee with the given CPF does not have an entry in the database.
    """
    global con, cur
    data = (cpf, )
    res = cur.execute("SELECT cpf FROM registro WHERE cpf=?", data)
    if res.fetchone() is None: #Determines if the employee has a cpf entry in the database (essentilay if they did the test)
        return False
    elif comment: #Determines if the optional comment was provided (It's ugly don't look at it)
        data = (feedback, comment , cpf)
        cur.execute("UPDATE registro SET feedback=? comment=? WHERE cpf=?", data)
    else:
        data = (feedback, cpf)
        cur.execute("UPDATE registro SET feedback=? WHERE cpf=?", data)
    con.commit() 
def deactivate_database():
    """
    This fuction saves any uncommited changes and closes the database connection.
    It is useful for security reasons to always close a database connection when done using it.
    
    Returns:
    None
    """
    con.commit()
    con.close()