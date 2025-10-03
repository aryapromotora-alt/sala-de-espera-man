import json
import os
from supabase import create_client, Client

# Inicializa o cliente Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def handler(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            data = {}
        
        global_session_id = data.get('global_session_id', 'global_default')
        
        # Verificar se sessão existe
        session_data = supabase.table("user_sessions").select("*").eq("session_id", global_session_id).execute()
        
        if not session_data.data:
            # Criar sessão
            supabase.table("user_sessions").insert({
                "session_id": global_session_id
            }).execute()
            
            # Criar playlist padrão
            supabase.table("playlists").insert({
                "name": "default",
                "user_id": global_session_id,
                "items": []
            }).execute()
            
            # Buscar sessão criada
            session_data = supabase.table("user_sessions").select("*").eq("session_id", global_session_id).execute()
        
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
                "session": session_data.data[0]
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