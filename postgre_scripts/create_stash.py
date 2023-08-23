
import os
from dotenv import load_dotenv
import openai
import json
from pydantic import BaseModel
from typing import List, Union


class Node(BaseModel):
    name: str
    type: str
    childrens: List[Union["Node", None]] = []


class Stash(BaseModel):
    nodes: List[Node]

load_dotenv()

openai.api_key = os.getenv('OPENAI_KEY')

example_data = [
    {
        "name": "Stash",
        "type": "folder",
        "childrens": [
            {
                "name": "Categoria 1",
                "type": "folder",
                "childrens": [
                    {"name": "Conversazione 1", "type": "file"},
                    {"name": "Conversazione 2", "type": "file"}
                ]
            },
            {"name": "Conversazione 3", "type": "file"},
            {"name": "Conversazione 4", "type": "file"}
        ]
    },
    {"name": "Conversazione 0", "type": "file"}
]

def create_stash(description):

    completion = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=[{"role": "user", "content": description}],
    functions=[{
            "name": "convert_description_to_stash_object",
            "description": f'convert the description to an object called "stash" with a structure similar to the following {example_data} \
            but with an arbitrary number of files, folders and subfiles and subfolders. Each file MUST have unique name. Add also a field called "id" for each file, which can be just a unique number',
            "parameters": {
                "type": "object",
                "properties":{
                    "stash": {          
                        "type": "array",
                        "items": {
                            "node": {
                                "type": "object",
                                "description": "Can be both a file or a folder containing another stash array."
                                }
                        },
                    "description" : "List of nodes componing the stash"
                    }
                },
                "required": ["node"]
            }
        }],
    function_call={"name": "convert_description_to_stash_object"},
    )
    reply_content = completion["choices"][0]["message"]
    stash = reply_content.to_dict()['function_call']['arguments']
    stash = json.loads(stash)['stash']
    return json.dumps(stash, indent=4)




output = create_stash("A simple stash containing 2 wmpty folders")
print(output)






""" output =  create_stash("A stash containing 3 main folders, called 'Coding', 'Writing' and 'Other'.\ """
""" Each folder should contain at least 3 files. The Other folder must contain 2 subfolders called Film\ """
""" and Books. Put in them at least 3 files. The Book subfolder should contain another subfolder called Work which contains just 1 file called mybook  ") """


""" validated_data = Stash(nodes=data) """
""" print(validated_data)    """
