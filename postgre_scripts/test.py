import json
from babydragon.memory.threads.base_thread import BaseThread
import polars as pl


pl.Config.set_tbl_cols(100)

with open('/home/j03h311/AI/Data/conversations.json', 'r') as file:
    data = json.load(file)



user_id = 'user1'



new_thread = BaseThread(name=user_id)

for c in data:
    for m in c['mapping']:

        if c['mapping'][m]['message'] is not None:
            try:
                new_row = {

                    'conversation_id': c['id'],
                    'conversation_title': c['title'],
                    'create_time': c['mapping'][m]['message']['create_time'],
                    'update_time': c['mapping'][m]['message']['update_time'],
                    'role': c['mapping'][m]['message']['author']['role'],
                    'content': c['mapping'][m]['message']['content']['parts'][0]
                }

                new_thread.add_dict_to_thread(new_row)
            except Exception as e:
                print(e)
                print( c['mapping'][m]['message'])
                print('\n\n')

""""""
""" print(new_thread.memory_thread)  """
print(new_thread.memory_thread.columns)

""" print(data[0]['mapping']['2d01e8dc-4b9b-4b43-ac12-a15c9ee20410']['message'].keys()) """
