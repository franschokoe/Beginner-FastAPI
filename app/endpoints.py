from fastapi import APIRouter , Path
from typing import Optional
from pydantic import BaseModel  #Creating the user
from . import schemas
from ..minidb import students

router = APIRouter(
    tags=["Sub branch"]
)

# we use get to access from the database
# @app.get("/")
# def index():
#     return {"name": "First Data"}

@router.get("/students/{student_id}")
def get_students(student_id:int = Path(description="The id of a student to view." , gt = 0)):

    if student_id not in students:

        return {"Error" : "Student not found"}
    else:
        
        return students[student_id]

# @app.get("/get-by-name")
# def get_students(name:str):
#     for student_id in students:
#         if students[student_id]["name"] == name:
#             return students[student_id]
        
#     return {"data": "not found"}
# We use Post to create in the database
@router.post("/create-student/{student_id}")
def create_student(student_id : int , student: schemas.Student):
    if student_id in students:
        return {"Error": "Student exists"}
    
    students[student_id] = student
    return students[student_id]


# Put methods
@router.put("/update-student/{student_id}")
def update_student(student_id: int , student: schemas.UpdateStudent):
    if student_id not in students:
        return {"Error" : "Student does not exist"}
    
    if student.name != None:
        students[student_id].name = student.name

    if student.age != None:
        students[student_id].age = student.age

    if student.year != None:
        students[student_id].year = student.year

    students[student_id] = student

    return students[student_id]

# this is how we delete from the base

@router.delete("/delete-students/{student_id}")
def delete_student(student_id:int):
    if student_id not in students:
        return {"Error" : "Student not found"}
    
    del students[student_id]
    return {"Massege":"Student deleted successfully"}