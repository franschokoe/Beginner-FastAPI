from annotated_types import T
from fastapi import Depends, FastAPI, HTTPException
from datetime import datetime, timezone
from typing import Annotated, Any, Generic, TypeVar
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel, Session, select


class Campaign(SQLModel , table= True):
    campaign_id: int | None = Field(default=None , primary_key=True)
    name: str = Field(index=True)
    region : str = Field(index=True)
    due_date: datetime | None= Field(default=None , index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

class CampaignCreate(SQLModel):
    name: str
    due_date : datetime | None = None
    region : str 

# connection to database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread" : False}
engine = create_engine(sqlite_url , connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
    
SessionDep = Annotated[Session,Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                # Campaign(name="Summer Luanch" , due_date = datetime.now()),
                # Campaign(name="Black Friday" , due_date = datetime.now())
            ])
            session.commit()
    yield


# app = FastAPI()
app = FastAPI(root_path="/api/v1" , lifespan=lifespan)

"""
This is a generic api endpoint that return any data type & it can be used for being inherited inside the calls 
e.g get("/campaings" , response_model = Responce[main class to inherit])
"""
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T

@app.get("/campaigns" , response_model=Response[Campaign])
async def read_campaign(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data": data}


@app.get("/campaigns/{id}" , response_model=Response[Campaign])
async def read_campaign(id:int , session: SessionDep):
    data = session.get(Campaign , id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}


@app.post("/campaigns" , status_code=201 , response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate , session :SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data" : db_campaign}



@app.put("/campaigns/{id}" , response_model=Response[Campaign])
async def update_campaign(id : int , campaign: CampaignCreate , session: SessionDep):
    data = session.get(Campaign , id)
    if not data :
        raise HTTPException(status_code=404)
    data.name = campaign.name
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data" : data}

@app.delete("/campaigns/{id}" , status_code=201)
async def delete_campaign(id:int , session: SessionDep):
    data = session.get(Campaign , id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    return {"data" : "Deleted"}










# @app.get("/")
# async def root():
#     return {"massege": "Hello from fast api"}

# data = [
#     {
#         "campaign_id":1,
#         "name":"Summer Launch",
#         "due_date" : datetime.now(),
#         "created_at": datetime.now()
#     },
#     {
#         "campaign_id":2,
#         "name":"Black Friday",
#         "due_date" : datetime.now(),
#         "created_at": datetime.now()
#     },
#     {
#         "campaign_id":3,
#         "name":"Macro deal",
#         "due_date" : datetime.now(),
#         "created_at": datetime.now()
#     },
# ]
# """
# Campaigns
# - campaign_id
# - name
# - due_date
# - created_at 
# """
# @app.get("/campaigns")
# async def read_campaigns():
#     return {"Campaigns" : data}

# @app.get("/campaigns/{id}")
# async def read_campaign(id:int):
#     for campaign in data:
#         if campaign.get("campaign_id")== id:
#             return {"campaign": campaign }
        
#     raise HTTPException(status_code=404)

# @app.post("/campaigns")
# async def create_campaign(body:dict[str,Any]):
#     # body = await request.json()

#     new = {
#         "campaign_id":randint(100 , 1000),
#         "name": body.get("name"),
#         "due_date" : body.get("due_date"),
#         "created_at": datetime.now()
#     }

#     data.append(new)
#     return {"campaign" : new}


# # updating data
# @app.put("/campaigns/{id}")
# async def update_campaign(id: int ,body: dict[str,Any]):
    
#     for index , campaign in enumerate(data):
#         if campaign.get("campaign_id") == id:
#             updated = {
#                 "campaign_id":id,
#                 "name": body.get("name"),
#                 "due_date" : body.get("due_date"),
#                 "created_at": campaign.get("created_at")
#             }
#             data[index] = updated
#             return {"Messsage" : "Updated"}
    
#     raise HTTPException(status_code=404)

# # for delete
# @app.delete("/campaigns/{id}")
# async def delete_campaign(id: int):

#     for index , campaign in enumerate(data):
#         if campaign.get("campaign_id") == id:
#             data.pop(index)
#             return Response(status_code=204)
        
#     raise HTTPException(status_code=404)