import json
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

GLOBAL_SESSION_ID = "global_default"

def handler(request):
    if request.method == "GET":
        # Verificar se sessão existe
        session_data = supabase.table("user_sessions").select("*").eq("session_id", GLOBAL_SESSION_ID).execute()
        
        if not session_data.data:
            # Criar sessão e playlist padrão
            supabase.table("user_sessions").insert({
                "session_id": GLOBAL_SESSION_ID
            }).execute()
            
            supabase.table("playlists").insert({
                "name": "default",
                "user_id": GLOBAL_SESSION_ID,
                "items": []
            }).execute()
            
            session_data = supabase.table("user_sessions").select("*").eq("session_id", GLOBAL_SESSION_ID).execute()
        
        # Buscar playlists
        playlists_data = supabase.table("playlists").select("*").eq("user_id", GLOBAL_SESSION_ID).execute()
        
        playlists_dict = {}
        for p in playlists_data.data:
            try:
                items = p["items"] if isinstance(p["items"], list) else json.loads(p["items"])
            except:
                items = []
            playlists_dict[p["name"]] = items
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "success": True,
                "playlists": playlists_dict,
                "current_playlist": session_data.data[0]["current_playlist"]
            })
        }
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
        except:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid JSON"})
            }
        
        # Extrair playlist_name da URL (ex: /api/global-playlists/minha-playlist)
        path = request.url.split("/")[-1]
        if not path or path == "global-playlists":
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Playlist name is required"})
            }
        playlist_name = path
        
        items = data.get("items", [])
        
        # Verificar se playlist existe
        playlist_data = supabase.table("playlists").select("*").eq("user_id", GLOBAL_SESSION_ID).eq("name", playlist_name).execute()
        
        if not playlist_data.data:
            # Criar nova playlist
            new_playlist = supabase.table("playlists").insert({
                "name": playlist_name,
                "user_id": GLOBAL_SESSION_ID,
                "items": items
            }).execute()
            playlist = new_playlist.data[0]
        else:
            # Atualizar existente
            updated = supabase.table("playlists").update({
                "items": items
            }).eq("user_id", GLOBAL_SESSION_ID).eq("name", playlist_name).execute()
            playlist = updated.data[0]
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "playlist": {
                    "id": playlist["id"],
                    "name": playlist["name"],
                    "user_id": playlist["user_id"],
                    "items": playlist["items"],
                    "created_at": playlist["created_at"],
                    "updated_at": playlist["updated_at"]
                }
            })
        }
    
    elif request.method == "DELETE":
        path = request.url.split("/")[-1]
        if not path or path == "global-playlists":
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Playlist name is required"})
            }
        playlist_name = path
        
        if playlist_name == "default":
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Cannot delete default playlist"})
            }
        
        # Verificar se existe
        playlist_data = supabase.table("playlists").select("*").eq("user_id", GLOBAL_SESSION_ID).eq("name", playlist_name).execute()
        if not playlist_data.data:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Playlist not found"})
            }
        
        # Deletar
        supabase.table("playlists").delete().eq("user_id", GLOBAL_SESSION_ID).eq("name", playlist_name).execute()
        
        # Verificar se era a playlist atual
        session_data = supabase.table("user_sessions").select("*").eq("session_id", GLOBAL_SESSION_ID).execute()
        if session_data.data and session_data.data[0]["current_playlist"] == playlist_name:
            supabase.table("user_sessions").update({
                "current_playlist": "default"
            }).eq("session_id", GLOBAL_SESSION_ID).execute()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "message": "Playlist deleted successfully"
            })
        }
    
    elif request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method not allowed"})
    }