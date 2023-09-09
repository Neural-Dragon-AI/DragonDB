from pydantic import BaseModel
from typing import List, Optional, Union

class IndexFlagPair(BaseModel):
    index: int
    flag: bool

class Index(BaseModel):
    category: str
    label: str
    source: str


class IndexFlagPairs(BaseModel):
    data: List[IndexFlagPair]

class ChatApi(BaseModel):
    model: str
    max_output_tokens: int
    system_prompt: str
    requested_index: list[Index]
    max_index_memory: int
    name: str
    max_fifo_memory: int
    longterm_thread: Optional[None] = None
    max_vector_memory: int
    max_memory: int
    longterm_frac: float



class Message(BaseModel):
    agent: str
    content: str
    timestamp: int
    status: str
    elapsed_time: int


    
class ChatBackUp(BaseModel):
    instancekey: str
    conversation: list[Message]
    config: ChatApi

class Node(BaseModel):
    name: str
    type: str
    id: str
    tags: str
    childrens: List[Union["Node", None]] = []


class Stash(BaseModel):
    stash: List[Node]


class Url(BaseModel):
    url: str
