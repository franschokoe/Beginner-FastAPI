from fastapi import FastAPI 
from . import endpoints

app = FastAPI()


# endpoints in main
app.include_router(endpoints)