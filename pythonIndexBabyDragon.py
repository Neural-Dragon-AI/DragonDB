import pandas as pd
from typing import Callable, List, Optional, Union
from babydragon.memory.indexes.memory_index import MemoryIndex
from babydragon.memory.indexes.python_index import PythonIndex
from babydragon.chat.memory_chat import FifoChat
import babydragon
import os
import openai
from active_instances import *
from cryptography.fernet import Fernet
import cryptography.fernet as fernet
from datetime import datetime
from pydantic import BaseModel
import json



async def new_PythonIndexesBabydragon( instance_key: Union[str,None], key: str, config:str):
    
    config = json.loads(config)
    if instance_key in instances.keys():
        
        return False

    elif len(key)==51:
        try:
            openai.api_key = key
            babydragon_path = os.path.dirname(os.path.abspath(babydragon.__file__))
            fernet_path = os.path.dirname(os.path.abspath(fernet.__file__))
            pandas_path = os.path.dirname(os.path.abspath(pd.__file__))

            path_dict= { "babyindex": babydragon_path,
                          "pandas": pandas_path,
                          "fernet": fernet_path
            }

            index_dict = {}
            for k in path_dict:
                tmp = PythonIndex(path_dict[k],
                        name=f'{k}_index_parallel',
                        minify_code=False,
                        load=True,
                        max_workers=16,
                        backup=False,
                        filter='class')

                index_dict[k] = tmp
            print(index_dict)
            chatbot = FifoChat(model="gpt-3.5-turbo",
                   index_dict=index_dict,
                   name="babyd_chatbot",
                   max_fifo_memory=2500,
                   max_index_memory=2500,
                   max_output_tokens=500)

            chatbot.set_current_index(None)
           
            crypto_key = Fernet.generate_key()
            cipher_suite = Fernet(crypto_key)
            openaikey = key+datetime.now().strftime("%H:%M:%S")
            encrypted_key = cipher_suite.encrypt(openaikey.encode('utf-8'))
            instances[encrypted_key] = chatbot
            print(len(instances))
            print(path_dict)

            return encrypted_key.decode('utf-8')

        except Exception as e:
            print(str(e))
            return False
    else:
        return False
