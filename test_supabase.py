from backend.supabase_client import supabase

try:
    result = supabase.table("users").select("*").limit(1).execute()

    print("✅ Connected to Supabase!")
    print(result.data)

except Exception as e:
    print("❌ Connection failed:")
    print(e)