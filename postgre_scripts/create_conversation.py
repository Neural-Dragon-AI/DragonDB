from postgresql import *








tuples = create_conversation_data('https://chat.openai.com/share/7f9bdb65-732f-433d-8be2-6a891f613591')
conn = connect_to_supabase()
create_conversation(conn,  'conversazione4')
bulk_insert(conn,  'conversazione4', tuples)
