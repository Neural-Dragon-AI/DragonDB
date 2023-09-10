from postgresql import *
from babydragon.memory.threads.base_thread import BaseThread






thread = BaseThread()
thread.load_from_gpt_url("https://chat.openai.com/share/7f9bdb65-732f-433d-8be2-6a891f613591")
tuples = create_conversation_data(thread)
conn = connect_to_supabase()
create_conversation(conn,  'conversazione4')
bulk_insert(conn,  'conversazione4', tuples)
