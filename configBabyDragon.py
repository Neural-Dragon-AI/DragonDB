from typing import  Union, cast

from babydragon.chat.memory_chat import Chat, FifoChat, VectorChat, FifoVectorChat
from models import  ChatApi
import openai
from active_instances import *
from index_manager import *
from cryptography.fernet import Fernet
from datetime import datetime




## Gonna create a class here


def generate_instance_key(api_key: str) -> bytes:

        crypto_key = Fernet.generate_key()
        cipher_suite = Fernet(crypto_key)
        openaikey = api_key+datetime.now().strftime("%H:%M:%S")
        instance_key = cipher_suite.encrypt(openaikey.encode('utf-8'))
        return instance_key


async def create_Chat(instance_key: str, api_key: str, chatType: str, config:ChatApi ) -> str:
    
    if instance_key.encode("utf-8") in instances.keys():        
        return instance_key
    try:
        openai.api_key = api_key
        chatbot = '?'
        match str(chatType.strip()):
            case "Chat":
 
                chatbot = Chat(model=config.model,
                       max_output_tokens=config.max_output_tokens,
                       system_prompt=config.system_prompt,
                       max_index_memory=config.max_index_memory,
                       name=config.name,
                       index_dict=retrieve_index(config.requested_index)) 
            case "FifoChat":

                chatbot = FifoChat(model=config.model,
                       max_output_tokens=config.max_output_tokens,
                       system_prompt=config.system_prompt,
                       max_index_memory=config.max_index_memory,
                       name=config.name,
                       max_fifo_memory=config.max_fifo_memory,
	                   longterm_thread=None,
                       index_dict=retrieve_index(config.requested_index)) 
            case "VectorChat":

                chatbot = VectorChat(model=config.model,
                       max_output_tokens=config.max_output_tokens,
                       system_prompt=config.system_prompt,
                       max_index_memory=config.max_index_memory,
                       name=config.name,
                       max_vector_memory=config.max_vector_memory,
                       index_dict=retrieve_index(config.requested_index)) 
            case "FifoVectorChat":

                chatbot = FifoVectorChat(model=config.model,
                       max_output_tokens=config.max_output_tokens,
                       system_prompt=config.system_prompt,
                       max_index_memory=config.max_index_memory,
                       name=config.name,
                       max_memory=config.max_memory,
                       longterm_thread=None,
                       longterm_frac=config.longterm_frac,
                       index_dict=retrieve_index(config.requested_index))
            case _:
                print("No match found")
        
        if (chatbot != '?'):

            chatbot.set_current_index(None)           
            new_instance_key = generate_instance_key(api_key)
            instances[new_instance_key] = chatbot
            
            print(f'Chat number    {len(instances)}    succesfully created.')
 
            return new_instance_key.decode('utf-8')
        
        else:

            return "No chatbots"

    except Exception as e:
            
        return (f'Error during the chat creation: {str(e)}')
