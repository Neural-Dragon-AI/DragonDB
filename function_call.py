
from active_instances import *
import openai
import json
from fastapi.responses import StreamingResponse



def welcome_openai_function():
    try:
        openai.api_key = "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"

        generator = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                prompt="Give me a random quote from a random sci-fy book",
                max_tokens=4097,
                stream=True
            )

        def chatbot_generator(): 
            for chunk in generator:
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
