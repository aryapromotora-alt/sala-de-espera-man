import json
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

GLOBAL_SESSION_ID = "global_default"

def handler(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
        except:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid JSON"})
            }
        
        playlist_name = data.get("playlist_name")
        if not playlist_name:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Playlist name is required"})
            }
        
        # Verificar se playlist existe
        playlist_data = supabase.table("playlists").select("*").eq("user_id", GLOBAL_SESSION_ID).eq("name", playlist_name).execute()
        if not playlist_data.data:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Playlist not found"})
            }
        
        # Atualizar sessão
        supabase.table("user_sessions").update({
            "current_playlist": playlist_name
        }).eq("session_id", GLOBAL_SESSION_ID).execute()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "current_playlist": playlist_name
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