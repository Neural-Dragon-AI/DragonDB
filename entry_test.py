import os
from dotenv import load_dotenv
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions


load_dotenv()
url: str|None = os.environ.get("SUPABASE_URL")
key: str|None = os.environ.get("SUPABASE_KEY")


supabase = None


if (url is not None) and (key is not None):
    try:
        opts = ClientOptions().replace(schema="conversations")
        supabase: Client|None = create_client(url, key, options=opts)
        print(f"Supabase initialized with:\n url:    {url} \n\n\n key:    {key} \n\n\n options:    {opts}\n\n\n")

    except Exception as e:
        print(e)
else:
    print("Missing env variables")


""" if supabase is not None: """
""""""
"""     try: """
""""""
"""         data = supabase.table('test_test').select("*").execute() """
"""         print(data) """
"""     except Exception as e: """
"""         print(f"Error in query: {e}") """
""""""


def insert():

    if supabase is not None:

        try:
            data, count = supabase.table('test_test').insert({"role": 1, "content": "Denmark", "timestamp": 0, "tokens_count": 0}).execute()
            print(data)
            print(count)
        except Exception as e:
            print(f"Error in query: {e}")

""" insert() """
    
