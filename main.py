from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from active_instances import *
from models import  ChatBackUp, ChatApi, Message
from configBabyDragon import *
import json
import pkg_resources
from fastapi.responses import StreamingResponse

from babydragon.utils.chatml import mark_answer

app = FastAPI()

origins = [
    "localhost:5173",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/getnewbabydragon/{chatType}/{apikey}/{instance_key}")
async def get_new_Chat(instance_key: str, chatType:str, apikey: str, body: ChatApi):
    print(f'"\n\n"{body}"\n\n"')
    print("")
    try:
        this_instance_key = await create_Chat(instance_key, apikey, chatType, config=body) 
        indexes = list(instances[str(this_instance_key).encode('utf-8')].index_dict.keys())
        return {"status":"created" , "instance_key": this_instance_key, "indexes": indexes  }

    except Exception as e:
        print("Request body: ", body.dict())
        print("Error: ", e)
        return {"status":"failed", "instance_key": str(e), "index_dict": {}}

@app.get("/welcome")
async def welcome():
    try:
        welcome_openai_function()
        

    except Exception as e:
        print(str(e))




@app.get("/getvenvmodules")
async def get_venv_modules():
    try:
        installed_packages = [f'{d.project_name} {d.version}' for d in pkg_resources.working_set]
        print(installed_packages)
        return installed_packages
    except Exception as e:
        print(e)

@app.post("/updatebackup/{instance_key}")
async def updatebackup(instance_key: str, chat_backup: ChatBackUp):

    backup_path = f"./backup/{chat_backup.config.name}-****{instance_key[-4:]}.json"
    backup_data = { **chat_backup.dict()}

    try:
        with open(backup_path, 'w') as backup_file:
            json.dump(backup_data, backup_file)
        return {"status": "success", "message": "Chat backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/append_user_defined_ids/{key}/{index}")
async def append_user_defined_ids(key: str, index:str, data: List[int]):
    
    try: 
        chatbot = instances[key.encode('utf-8')] 
        chatbot.add_user_defined_ids({index: data}) 
        current_user_defined_ids = chatbot.user_defined_ids
        print(current_user_defined_ids)
        instances[key.encode('utf-8')] = chatbot 
    

        return {"status":"correct" , "current_user_defined_ids": current_user_defined_ids } 
   
    except Exception as e: 
        print(e) 
        return {"status":"error", "current_user_defined_ids": str(e)} 

@app.delete("/deletebabydragon/{instance_key}")
async def delete_Chat(instance_key: str):
    if instance_key.encode("utf-8") in instances.keys():
        print(f'BEFORE ------>{len(instances.keys())}')
        del instances[instance_key.encode("utf-8")]
        print(f'AFTER ------>{len(instances.keys())}')

        return {"status":"deleted", "instance_key": instance_key}
    else:
        return {"status":"failed", "message": f"No instance with key {instance_key} found."}


@app.get("/reply/{key}/{question}")
async def chatbot_reply(key: str, question: str):
        
    try:
        reply = instances[key.encode('utf-8')].reply(question)  
        return {"status":"correct" , "reply": reply}

    except Exception as e:
        print(e)
        if "KeyError" in str(type(e)):
            error = "Sorry, your chatbot no longer exists in the backend :( Restore the conversation from the backup file! "
        else:
            error = str(e)
        return {"status":"error", "reply": error}
  
@app.get("/streamreply/{key}/{question}")
async def stream_reply(key: str, question: str):
    try:
        chatbot = instances[key.encode('utf-8')]
        def chatbot_generator(): 
            for chunk in chatbot.reply(message=question, stream=True)[0]:
                yield f"data: {json.dumps(chunk)}\n\n"
            yield f"data: {json.dumps({'end': True})}\n\n" 
        return StreamingResponse(chatbot_generator(), media_type="text/event-stream")
    except Exception as e:
        if "KeyError" in str(type(e)):
            error = "Sorry, your chatbot no longer exists in the backend :( Restore the conversation from the backup file! "
        else:
            error = str(e) 
        def chatbot_generator():
            yield f"data: {json.dumps({'error': error})}\n\n"
        return StreamingResponse(chatbot_generator(), media_type="text/event-stream") 

@app.post("/addlastanswer/{instancekey}")
async def add_last_answer(instancekey: str, data: Message):
    
    try: 
        chatbot = instances[instancekey.encode('utf-8')] 
        chatbot.add_message(mark_answer(data.content))
        instances[instancekey.encode('utf-8')] = chatbot 
    

        return {"status":"correct" } 
   
    except Exception as e: 
        print(e) 
        return {"status": str(e)} 


@app.get("/setcurrentindex/{key}/{index}")
async def set_current_index(key: str, index: str):
    print(index)         
    try:
        chatbot = instances[key.encode('utf-8')]

        if index == "None":
            chatbot.set_current_index(None)
        else:
            chatbot.set_current_index(index)
            chatbot.user_defined_ids = []

        instances[key.encode('utf-8')] = chatbot
        return {"status":"correct" , "new_index": index}

    except Exception as e:
        print(e)
        return {"status":"error", "new_index": str(e)}






@app.get("/querycurrentindex/{key}/{query}")
async def query_current_index(key: str, query: str):
       
    try:
        chatbot = instances[key.encode('utf-8')]
        current_index = chatbot.current_index
        query_res = chatbot.index_dict[current_index].faiss_query(query)
        values = query_res[0] 
        scores = list(map(float, query_res[1]))
        indexes = query_res[2].flatten().tolist()
        reshaped_data = list(zip(values, scores, indexes))
        
        return {"status":"correct" , "current_index":  current_index, "values": reshaped_data }

    except Exception as e:
        print(e)
        if "None" in str(e):
            error = "Select an index!"
            print(error)
        elif "KeyError" in str(type(e)):
            error = "Sorry, your chatbot no longer exists in the backend :( Restore the conversation from the backup file! "
            print(error)
        else:
            error = str(e)
        return {"status":"error", "current_index": "unknown", "values": [[error]]}
