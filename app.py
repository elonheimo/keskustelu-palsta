from flask import Flask
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import routes

#päräyttää suoraan toimintaan 
if __name__ == "__main__":
    app.run(debug=True)

"""
export FLASK_ENV=development
flask run
"""