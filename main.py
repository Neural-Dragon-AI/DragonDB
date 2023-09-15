from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from active_instances import *
from models import  *
""" from configBabyDragon import * """
from pathlib import Path
import json
import zipfile
import pkg_resources
from fastapi.responses import StreamingResponse
from babydragon.memory.threads.base_thread import BaseThread
from babydragon.utils.chatml import mark_answer
from pipelines.jobs import EmbeddingsPipeline
import polars as pl

app = FastAPI()

origins = [
    "localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/getRows/{user_id}/{conversation_id}")
async def get_rows(user_id: str, conversation_id: str):

    try:
        
        user_thread = BaseThread()
        user_thread.load(f'users/{user_id}/memory.parquet')
        response = user_thread.memory_thread.lazy().filter(pl.col("conversation_id") == conversation_id).collect().to_dicts()
        print(len(response))
        return response
   
    except Exception as e: 
        print(e) 
        return {"status":"error",  "error":str(e)} 


@app.get("/getInfo/{user_id}/")
async def get_Info(user_id: str):

    try:
        
        user_thread = BaseThread()
        user_thread.load(f'users/{user_id}/memory.parquet')
        num_messages = user_thread.memory_thread.shape[0]
        num_conversations = user_thread.memory_thread.select("conversation_id").unique().shape[0]
        info = {"num_messages":num_messages, "num_conversations": num_conversations}
        return info
   
    except Exception as e: 
        print(e) 
        return {"status":"error",  "error":str(e)} 


@app.post("/embeddingsRequest/{user_id}")
async def embeddingsRequest(user_id: str):

    try:
        user_thread = BaseThread()
        user_thread.load(f'users/{user_id}/memory.parquet')
        pipeline = EmbeddingsPipeline(raw_thread=user_thread.memory_thread)

        return {
                "status":"success",
                "name":pipeline.generator.name,
                "total_token":pipeline.generator.total_tokens,
                "total_estimated_cost":pipeline.generator.total_estimated_cost
                }
   
    except Exception as e: 
        print(e) 
        return {"status":"error",  "error":str(e)} 



@app.post("/embeddingsFinalize/{user_id}")
async def embeddingsFinalize(body:EmbeddingsFinalize, user_id: str):
    try:

        user_thread = BaseThread()
        user_thread.load(f'users/{user_id}/memory.parquet')
        new_pipeline = EmbeddingsPipeline(restore=body.name,raw_thread=user_thread.memory_thread, open_api_api_key=body.openai_api_key) 
        output = new_pipeline.start()

        if output is not None:

            merged_data = user_thread.memory_thread.with_row_count('id')\
                                                    .join(output.with_columns(pl.col('id')\
                                                    .cast(pl.UInt32)).select('output','id')\
                                                    .sort('id'), on="id")\
                                                    .rename({"output":f'embeddings_{new_pipeline.generator.name}'})\
                                                    .drop('id')

            user_thread.memory_thread = merged_data
            user_thread.save(f'users/{user_id}/memory.parquet')
            return { "status":"success", "new_column": f'embeddings_{new_pipeline.generator.name}' }

        else:
            return {"status":"error",  "error":"No embeddings job output find."}



            
    except Exception as e: 
        print(e) 
        return {"status":"error",  "error":str(e)} 






@app.post("/importFromUrl/{user_id}")
async def append_user_defined_ids(body: Url, user_id: str):
    print(body.url)
    try:
        
        new_thread = BaseThread(save_path=f'users/{user_id}/')
        new_thread.load_from_gpt_url(body.url)
        print(new_thread.memory_thread[0]['conversation_id'][0])
        new_thread.save()

        return {"id":new_thread.memory_thread[0]['conversation_id'][0], "name":new_thread.memory_thread[0]['conversation_title'][0]}
   
    except Exception as e: 
        print(e) 
        return {"status":"error",  "error":str(e)} 


@app.get("/stashMapping/{user_id}")
async def chatbot_reply(user_id: str):
    try:

        file_path = Path(f"./users/{user_id}/stash_mapping.json")
        

        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="User ID not found")
        

        with open(file_path, "r") as f:
            data = json.load(f)

        return data
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/stashMapping/{user_id}")
async def update_stash_mapping(user_id: str, body: Stash):
    print(body.stash_mapping)
    try:
        # Costruisce il percorso del file JSON
        file_path = Path(f"./users/{user_id}/stash_mapping.json")

        # Controlla se il file esiste
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="User ID not found")
        """ print(json.dumps(body.stash_mapping)) """
        # Sovrascrive il file con il nuovo contenuto
        with open(file_path, "w") as f:
            json.dump(body.stash_mapping, f)

        return {"status": "success", "message": "File content updated"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")




@app.delete("/stashMapping/{user_id}")
async def delete_stash_mapping(user_id: str):
    try:

        file_path = Path(f"./users/{user_id}/stash_mapping.json")
        
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="User ID not found")
        
        with open(file_path, "w") as f:
            f.write("[]")


        user_thread = BaseThread()
        user_thread.load(f'users/{user_id}/memory.parquet')
        user_thread.memory_thread = pl.DataFrame(schema=user_thread.memory_schema)
        user_thread.save(f'users/{user_id}/memory.parquet')
        
        return {"status": "success", "message": "File content deleted"}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/uploadfile/{user_id}")
async def upload_file(user_id: str, file: UploadFile = File(...) ):

    file_ext = ''
    print(file.filename)
    if file.filename is not None:
        file_ext = file.filename.split('.')[-1]  # Ottieni l'estensione del file

    if file_ext == 'zip':
        # Processa il file ZIP
        try:
            with zipfile.ZipFile(file.file) as z:
                # Elenco dei file all'interno del file ZIP
                list_of_file_names = z.namelist()

                # Stampa il contenuto di ciascun file
                """ for file_name in list_of_file_names: """
                """     with z.open(file_name) as f: """
                """         file_content = f.read() """
                """         print(f"Contenuto del file {file_name}: {file_content}") """
        
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Bad ZIP file")
        
        return {"status": "success", "message": "File ZIP processato correttamente"}

    elif file_ext == 'json':
        # Processa il file JSON
        try:
            json_content = json.load(file.file)
            thread = BaseThread()
            thread.load_from_backup(json_content)
            thread.save(f'users/{user_id}/memory.parquet')
            new_mappings = thread.memory_thread.select("conversation_id","conversation_title").unique().to_dicts()
            """ print(f"Contenuto del file JSON: {json_content}") """

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Bad JSON file")
        
        return {"status": "success", "content": new_mappings}

    else:
        raise HTTPException(status_code=400, detail="Tipo di file non supportato")


















""" OLD CALLS I KEEP THEM HERE FOR MEMO """

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




@app.delete("/deletebabydragon/{instance_key}")
async def delete_Chat(instance_key: str):
    if instance_key.encode("utf-8") in instances.keys():
        print(f'BEFORE ------>{len(instances.keys())}')
        del instances[instance_key.encode("utf-8")]
        print(f'AFTER ------>{len(instances.keys())}')

        return {"status":"deleted", "instance_key": instance_key}
    else:
        return {"status":"failed", "message": f"No instance with key {instance_key} found."}



  
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
