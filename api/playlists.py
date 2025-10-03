from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if 'global-playlists' in self.path:
            # GET /api/global-playlists
            playlists = self.get_global_playlists()
            self.send_json_response(playlists)
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_POST(self):
        if 'global-session' in self.path:
            # POST /api/global-session
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            session = self.create_or_get_global_session(data)
            self.send_json_response(session)
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_PUT(self):
        parsed_url = urlparse(self.path)
        
        if 'global-playlists' in self.path:
            # PUT /api/global-playlists/{playlist_name}
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                playlist_name = path_parts[-1]
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                playlist = self.update_global_playlist(playlist_name, data)
                self.send_json_response(playlist)
            else:
                self.send_error_response(400, "Invalid request")
        elif 'global-current-playlist' in self.path:
            # PUT /api/global-current-playlist
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            result = self.set_global_current_playlist(data)
            if result['success']:
                self.send_json_response(result)
            else:
                self.send_error_response(400, result['error'])
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        
        if 'global-playlists' in self.path:
            # DELETE /api/global-playlists/{playlist_name}
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                playlist_name = path_parts[-1]
                result = self.delete_global_playlist(playlist_name)
                if result['success']:
                    self.send_json_response(result)
                else:
                    self.send_error_response(400, result['error'])
            else:
                self.send_error_response(400, "Invalid request")
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def get_db_connection(self):
        db_path = '/tmp/app.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Criar tabelas se não existirem
        conn.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                items TEXT NOT NULL DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                current_playlist TEXT DEFAULT 'default',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_accessed TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        return conn
    
    def create_or_get_global_session(self, data):
        global_session_id = data.get('global_session_id', 'global_default')
        
        conn = self.get_db_connection()
        
        # Verificar se a sessão existe
        session = conn.execute(
            'SELECT * FROM user_sessions WHERE session_id = ?',
            (global_session_id,)
        ).fetchone()
        
        if not session:
            # Criar nova sessão
            conn.execute(
                'INSERT INTO user_sessions (session_id) VALUES (?)',
                (global_session_id,)
            )
            
            # Criar playlist padrão
            conn.execute(
                'INSERT INTO playlists (name, user_id, items) VALUES (?, ?, ?)',
                ('default', global_session_id, '[]')
            )
            
            conn.commit()
            
            # Buscar sessão criada
            session = conn.execute(
                'SELECT * FROM user_sessions WHERE session_id = ?',
                (global_session_id,)
            ).fetchone()
        
        conn.close()
        
        return {
            'success': True,
            'session': dict(session)
        }
    
    def get_global_playlists(self):
        global_session_id = 'global_default'
        conn = self.get_db_connection()
        
        # Verificar se a sessão existe
        session = conn.execute(
            'SELECT * FROM user_sessions WHERE session_id = ?',
            (global_session_id,)
        ).fetchone()
        
        if not session:
            # Criar sessão e playlist padrão
            conn.execute(
                'INSERT INTO user_sessions (session_id) VALUES (?)',
                (global_session_id,)
            )
            
            conn.execute(
                'INSERT INTO playlists (name, user_id, items) VALUES (?, ?, ?)',
                ('default', global_session_id, '[]')
            )
            
            conn.commit()
            
            session = conn.execute(
                'SELECT * FROM user_sessions WHERE session_id = ?',
                (global_session_id,)
            ).fetchone()
        
        # Buscar playlists
        playlists = conn.execute(
            'SELECT * FROM playlists WHERE user_id = ?',
            (global_session_id,)
        ).fetchall()
        
        conn.close()
        
        # Converter para formato de dicionário
        playlists_dict = {}
        for playlist in playlists:
            try:
                items = json.loads(playlist['items'])
            except:
                items = []
            playlists_dict[playlist['name']] = items
        
        return {
            'success': True,
            'playlists': playlists_dict,
            'current_playlist': session['current_playlist']
        }
    
    def update_global_playlist(self, playlist_name, data):
        global_session_id = 'global_default'
        items = data.get('items', [])
        
        conn = self.get_db_connection()
        
        # Verificar se a playlist existe
        playlist = conn.execute(
            'SELECT * FROM playlists WHERE user_id = ? AND name = ?',
            (global_session_id, playlist_name)
        ).fetchone()
        
        if not playlist:
            # Criar nova playlist
            conn.execute(
                'INSERT INTO playlists (name, user_id, items) VALUES (?, ?, ?)',
                (playlist_name, global_session_id, json.dumps(items))
            )
        else:
            # Atualizar playlist existente
            conn.execute(
                'UPDATE playlists SET items = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND name = ?',
                (json.dumps(items), global_session_id, playlist_name)
            )
        
        conn.commit()
        
        # Buscar playlist atualizada
        updated_playlist = conn.execute(
            'SELECT * FROM playlists WHERE user_id = ? AND name = ?',
            (global_session_id, playlist_name)
        ).fetchone()
        
        conn.close()
        
        return {
            'success': True,
            'playlist': {
                'id': updated_playlist['id'],
                'name': updated_playlist['name'],
                'user_id': updated_playlist['user_id'],
                'items': json.loads(updated_playlist['items']),
                'created_at': updated_playlist['created_at'],
                'updated_at': updated_playlist['updated_at']
            }
        }
    
    def set_global_current_playlist(self, data):
        global_session_id = 'global_default'
        playlist_name = data.get('playlist_name')
        
        if not playlist_name:
            return {
                'success': False,
                'error': 'Nome da playlist é obrigatório'
            }
        
        conn = self.get_db_connection()
        
        # Verificar se a playlist existe
        playlist = conn.execute(
            'SELECT * FROM playlists WHERE user_id = ? AND name = ?',
            (global_session_id, playlist_name)
        ).fetchone()
        
        if not playlist:
            conn.close()
            return {
                'success': False,
                'error': 'Playlist não encontrada'
            }
        
        # Atualizar sessão
        conn.execute(
            'UPDATE user_sessions SET current_playlist = ?, last_accessed = CURRENT_TIMESTAMP WHERE session_id = ?',
            (playlist_name, global_session_id)
        )
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'current_playlist': playlist_name
        }
    
    def delete_global_playlist(self, playlist_name):
        if playlist_name == 'default':
            return {
                'success': False,
                'error': 'Não é possível deletar a playlist padrão'
            }
        
        global_session_id = 'global_default'
        conn = self.get_db_connection()
        
        # Verificar se a playlist existe
        playlist = conn.execute(
            'SELECT * FROM playlists WHERE user_id = ? AND name = ?',
            (global_session_id, playlist_name)
        ).fetchone()
        
        if not playlist:
            conn.close()
            return {
                'success': False,
                'error': 'Playlist não encontrada'
            }
        
        # Deletar playlist
        conn.execute(
            'DELETE FROM playlists WHERE user_id = ? AND name = ?',
            (global_session_id, playlist_name)
        )
        
        # Se era a playlist atual, mudar para default
        session = conn.execute(
            'SELECT * FROM user_sessions WHERE session_id = ?',
            (global_session_id,)
        ).fetchone()
        
        if session and session['current_playlist'] == playlist_name:
            conn.execute(
                'UPDATE user_sessions SET current_playlist = ? WHERE session_id = ?',
                ('default', global_session_id)
            )
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Playlist deletada com sucesso'
        }
    
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
