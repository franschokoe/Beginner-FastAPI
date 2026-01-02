from typing import Union , Generic ,TypeVar
from fastapi import FastAPI 
from pydantic import BaseModel , Field 


app = FastAPI()
# class one for creating models

class Register(BaseModel):
    register_id : int | None = Field(default=None , primary_key = True)
    name : str | None = Field(index = True)


# Implementing the generic
B = TypeVar("B")
# Generic class 
class Response(BaseModel , Generic[B]):
    data : B

@app.get("/register" , response_model = Response[Register])
async def register():
    
    user_register = Register(register_id= 55 , name = "Master Oogway" )

    return Response(data = user_register)

# @app.get("/")
# def read_root():
#     return {"hello" : "World",
#             "Mzanzi" : "Africa"
#             }

# @app.get("/items/{item_id}")
# def read_item(item_id: int , q: Union[str,None] = None):
#     return {"item_id": item_id, "q": q}
