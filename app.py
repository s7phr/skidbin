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
        self.cf = json.load(open("helpers/config/settings.json", encoding="utf-8"))
        self.db = connect("helpers/schemas/db.db")
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
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pastes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL
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
            site = self.cf.get("site")
            return render_template(
                template_name_or_list="index.html",
                total=0,
                pastes=0,
                user=site.get("created-by"),
                added_by=site.get("added-by"),
                url=site.get("url"),
                title=site.get("title"),
                views=site.get("views"),
            )

        @self.app.route("/upload")
        def upload():
            return render_template(
                template_name_or_list="upload.html",
            )

        @self.app.route("/api/paste", methods=["POST"])
        def uploads():
            data = request.json
            title = data.get("title")
            content = data.get("content")

            if not title or not content:
                return jsonify({"error": "Title and content are required"}), 400

            paste_id = str(uuid4())

            self.cursor.execute(
                """
                INSERT INTO pastes (
                    id, 
                    title, 
                    content
                ) 
                VALUES (?, ?, ?)
                """,
                (
                    paste_id,
                    title,
                    content,
                ),
            )
            self.db.commit()

            return jsonify({"paste_id": paste_id}), 201

    def run(self):
        self.app.run(
            host="0.0.0.0",
            port=80,
            debug=True,
        )
