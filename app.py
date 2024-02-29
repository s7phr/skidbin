import json
import os
import random
import string
from sqlite3 import connect
from uuid import uuid4

import terminut
from flask import Flask, jsonify, redirect, render_template, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
        self.jwt = JWTManager(self.app)
        self.log = terminut.log()
        self.db = connect("helpers/schemas/users.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                token TEXT NOT NULL
            )
            """
        )
        self.db.commit()

        @property
        def db(self):
            return self.db

        @property
        def cursor(self):
            return self.cursor

        @property
        def log(self):
            return self.log

        @property
        def jwt(self):
            return self.jwt

        @self.app.route("/")
        def index():
            return render_template("index.html")

    def run(self):
        self.app.run(
            host="0.0.0.0",
            port=80,
            debug=True,
        )
