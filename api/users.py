from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL para obter parâmetros
        parsed_url = urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) == 2 and path_parts[1].isdigit():
            # GET /api/users/{id}
            user_id = int(path_parts[1])
            user = self.get_user_by_id(user_id)
            if user:
                self.send_json_response(user)
            else:
                self.send_error_response(404, "User not found")
        else:
            # GET /api/users
            users = self.get_all_users()
            self.send_json_response(users)
    
    def do_POST(self):
        # POST /api/users
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        user = self.create_user(data)
        self.send_json_response(user, 201)
    
    def do_PUT(self):
        # PUT /api/users/{id}
        parsed_url = urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) == 2 and path_parts[1].isdigit():
            user_id = int(path_parts[1])
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user = self.update_user(user_id, data)
            if user:
                self.send_json_response(user)
            else:
                self.send_error_response(404, "User not found")
        else:
            self.send_error_response(400, "Invalid request")
    
    def do_DELETE(self):
        # DELETE /api/users/{id}
        parsed_url = urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) == 2 and path_parts[1].isdigit():
            user_id = int(path_parts[1])
            if self.delete_user(user_id):
                self.send_response(204)
                self.end_headers()
            else:
                self.send_error_response(404, "User not found")
        else:
            self.send_error_response(400, "Invalid request")
    
    def get_db_connection(self):
        # Usar um banco de dados temporário para o Vercel
        db_path = '/tmp/app.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Criar tabela se não existir
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()
        return conn
    
    def get_all_users(self):
        conn = self.get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    def get_user_by_id(self, user_id):
        conn = self.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    def create_user(self, data):
        conn = self.get_db_connection()
        cursor = conn.execute(
            'INSERT INTO users (username, email) VALUES (?, ?)',
            (data['username'], data['email'])
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': user_id,
            'username': data['username'],
            'email': data['email']
        }
    
    def update_user(self, user_id, data):
        conn = self.get_db_connection()
        
        # Verificar se o usuário existe
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            conn.close()
            return None
        
        # Atualizar usuário
        conn.execute(
            'UPDATE users SET username = ?, email = ? WHERE id = ?',
            (data.get('username', user['username']), data.get('email', user['email']), user_id)
        )
        conn.commit()
        
        # Buscar usuário atualizado
        updated_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        return dict(updated_user)
    
    def delete_user(self, user_id):
        conn = self.get_db_connection()
        cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {'error': message}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
