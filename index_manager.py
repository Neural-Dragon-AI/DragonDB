from typing import  Union, List, Dict
from babydragon.models.embedders.cohere import CohereEmbedder
from babydragon.memory.indexes.memory_index import MemoryIndex
from babydragon.memory.indexes.python_index import PythonIndex
import pkg_resources
import os

import importlib



## Gonna create a class soon here

def create_wiki_index():

    dataset_url = "Cohere/wikipedia-22-12-simple-embeddings"
    index = MemoryIndex(name="wiki", load=True, is_batched=True,embedder=CohereEmbedder) # pyright: ignore
    if len(index.values)>0:
        return index
    else: 
        print("Index not found, creating new index")
        index = MemoryIndex.from_hf_dataset(dataset_url, ["title", "text"],embeddings_column= "emb", name="wiki", is_batched=True,embedder=CohereEmbedder) # pyright: ignore
        return index



def check_load(label: str) -> bool:
    load_directory = os.path.join("storage", label)
    if not os.path.exists(load_directory):
        return False

    print(f"Loading index from {load_directory}")

    index_filename = os.path.join(load_directory, f"{label}_index.faiss")

    values_filename = os.path.join(load_directory, f"{label}_values.json")
    if os.path.exists(index_filename) and os.path.exists(values_filename):
        return True
    else:
        return False


def create_local_python_index(label:str) -> Union[MemoryIndex,PythonIndex,bool]:
    
    """ if (check_load(label)): """
    """     return MemoryIndex(name=label, load=True, is_batched=True,max_workers=16,backup=False) """
    """ else: """
    try:
            module = importlib.import_module(label)
            if (module.__file__ is not None):
                path = os.path.dirname(os.path.abspath(module.__file__))
                return PythonIndex(path,
                                name=f'{label}_index_parallel',
                                minify_code=False,
                                load=True,
                                max_workers=16,
                                backup=False,
                                filter='class')
    except Exception as e:
            print(str(e))
            
    return False


def retrieve_index(requested_index: List) -> Dict[str,Union[MemoryIndex,PythonIndex]]:

    indexes = {'babydragon':create_local_python_index('babydragon')}
    if len(requested_index)>0:
        for k in requested_index:
            match (k.source, k.category, k.label):
                case ("local", _, _): 
                    if k.category == 'python':
                        indexes[k.label] = create_local_python_index(k.label)
                    elif (k.category == 'cohere') and (k.label == "wiki"):
                        indexes[k.label] = create_wiki_index()
    else:
        return {'babydragon':create_local_python_index('babydragon')} # pyright: ignore
    return {k: v for k, v in indexes.items() if v != False} # pyright: ignore

