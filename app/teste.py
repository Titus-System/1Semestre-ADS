import database
import sqlite3
from json import loads, dumps
import json
answers = {'resposta_1': 'D', 'resposta_2': 'B'}


# con = sqlite3.connect("database.db")
# cur = con.cursor()

# data = cur.execute("SELECT respostas FROM academico WHERE username=?",("zeca paugordinho",)).fetchone()
# if data:
#     print(loads(data[0]))
# else:
#     print(False)

data = database.retrieve_quiz_answers("gaiola")
print(data != None)

if data != None:
    data.update(answers)
    new_data = data
else:
    new_data = answers

print(data)

database.save_quiz_answers(new_data, "gaiola")