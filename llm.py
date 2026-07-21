import json 
from groq import Groq
from pydantic import ValidationError,BaseModel
from typing import Type

def generate_with_llm(client:Groq,model:str,prompt:str,SYSTEM_PROMT:str,response_format:dict,output_model:Type[BaseModel]):
    messages=[]
    if SYSTEM_PROMT :
        system_message={
            "role":"system",
            "content":SYSTEM_PROMT
        }
        messages.append(system_message)
    role="user"
    message={
        "role":role,
        "content":prompt
    }
    messages.append(message)
    response=client.chat.completions.create(model=model,messages=messages,response_format=response_format)

    content=response.choices[0].message.content
    try:
        data=json.loads(content)
        result=output_model.model_validate(data)
    except json.JSONDecodeError as e:
        raise ValueError("LLM returned invalid JSON") from e
    except ValidationError as e:
        raise ValueError(
        f"LLM response does not match {output_model.__name__} schema."
    ) from e
    
    return result
