import json 
from models import ResumeResponseModel,ResumeCompareModel
from groq import Groq
from pydantic import ValidationError
def analyze_resume(client:Groq,model:str,prompt:str,response_format:dict)->ResumeResponseModel:

    role="user"
    message={
        "role":role,
        "content":prompt
    }
    
    messages=[message]
    response=client.chat.completions.create(model=model,messages=messages,response_format=response_format)

    content=response.choices[0].message.content
    print(content)
    try:
        data=json.loads(content)
        resume=ResumeResponseModel.model_validate(data)
    except json.JSONDecodeError as e:
        raise ValueError("LLM returned invalid JSON") from e
    except ValidationError as e:
        raise ValueError(
        "LLM response does not match ResumeCompareModel schema."
    ) from e
    
    return resume