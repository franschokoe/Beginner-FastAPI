from fastapi import FastAPI , Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer ,OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime , timedelta
from jose import JWTError ,jwt 
from passlib.context import CryptContext


SECRET_KEY = "99711c4a5d779a776324970ddb1fbff934fb0bb35b1a795dfbd992ccb36f38a3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



fake_db = {

    "kai":{
        "username" : "general_kai",
        "full_name" : "Suprime Kai",
        "email" : "kai@gmail.com",
        "hashed_passwords": "$2b$12$zmn9sDMLwYwqY60XDlGnFOfT1zu63KabH1fOIYvB9K9msGPM3Jyjm",
        "strength" : 6,
        "disabled" : False ,
    }
}


class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username: str or None = None # type: ignore

class User(BaseModel):
    username: str
    full_name: str
    email: str or None = None # type: ignore
    strength: int or None = None # type: ignore 
    disabled: bool 


class UserInDB(User):
    hashed_password : str

# Hashing the passwords Algo

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated = "auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_passwords , hashed_password):
    return pwd_context.verify(plain_passwords , hashed_password)
# 
def get_passwords_hash(password):
    return pwd_context.hash(password)

def get_user(fake_db, username: str):
    if username in fake_db : 
        user_data = fake_db[username]
        
    return UserInDB(**user_data) #kwargs & args
    
    # Authentication

def authenticate_user(fake_db , username: str,password:str):
    user = get_user(fake_db, username)

    if not user:
        return False
    if not verify_password(password , user.hashed_password):
        return False
    
    return user


# Creating the access token
def create_access_token(data: dict , expire_delta: timedelta or None = None ): # type: ignore
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode ,key= SECRET_KEY ,algorithm= ALGORITHM)

    return encoded_jwt



async def get_current_user(token:str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , 
                                         detail="Could not validate credentials" , 
                                         headers= {"WWW-Authenticate": "Bearer"}
                                         )


    try:
        payload = jwt.decode(token=token , key= SECRET_KEY , algorithms= [ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception

    user = get_user(db=fake_db,username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400 , detail= "Inactive user")
    
    return current_user

@app.post("/token" , response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_db , username=form_data.username , password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , 
                            detail="Incorrect username or password" , 
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub" : user.username} , expire_delta= access_token_expires)

    return {"access_token" : access_token , "token_type" : "bearer" }



@app.get("/users/me/" , response_model=User)
async def read_user_me(current_user:User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items" , response_model=User)
async def read_own_items(current_user:User = Depends(get_current_active_user)):

    return [{"item_id": 1 , "owner":current_user}]





# pwd = get_passwords_hash("kai32")
# print(pwd)





























# class Data(BaseModel):
#     name: str

# @app.post("/create/")
# async def create(data : Data):
#     return {"data" : data}

# @app.get("/test/{item_id}/")
# async def test(item_id:str , query: int = 1):
#     return {"hello" : item_id}