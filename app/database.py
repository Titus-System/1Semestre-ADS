import sqlite3

#Operação para lincar a base de dados ao programa (E criar uma se nao houver)
con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

#Operação para criar uma tabela caso nao houver
res = cur.execute("SELECT name FROM sqlite_master WHERE name='registro'")
if res.fetchone() is None:
    cur.execute('''CREATE TABLE registro(
        cpf varchar(11) NOT NULL UNIQUE,
        nome varchar(100) NOT NULL,
        nota tinyint(225) NOT NULL, 
        feedback float(1),
        comment varchar(500),
        PRIMARY KEY (cpf)
        )''')

#Inserir uma nota aou final da prova            
def insertgrade(cpf, nome, nota):
    data = (cpf, )
    res = cur.execute("SELECT FROM registro WHERE cpf='?'", data)
    if res.fetchone() != None:
        data = (nota, cpf)
        res = cur.execute("UPDATE registro SET nota='?' WHERE cpf='?'", data)
    else:
        data = (cpf, nome, nota)
        res = cur.execute("INSERT INTO registro (cpf, nome, nota) VALUES(?, ?, ?)", data)
        
#inserir um feedback ao final do curso
def insertfeedback(cpf, feedback, comment):
    data = (cpf, )
    res = cur.execute("SELECT FROM registro WHERE cpf='?'", cpf) #ve se a pessoa fez a prova
    if res.fetchone() == None:
        return False #retorna o bool False se nao foi feita a prova
    else:
        data = (feedback, cpf)
        res = cur.execute("UPDATE registro SET feedback='?' WHERE cpf='?'", data)
        if comment:
            data = (comment, cpf)
            res = cur.execute("UPDATE registro SET comment='?' WHERE cpf='?'", data)