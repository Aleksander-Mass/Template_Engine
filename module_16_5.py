from fastapi import FastAPI, HTTPException, Request, Path
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Annotated

app = FastAPI()

# Создаем объект для работы с шаблонами
templates = Jinja2Templates(directory="templates")

# Модель пользователя
class User(BaseModel):
    id: int
    username: Annotated[str, Field(min_length=3, max_length=50, description="Имя пользователя")]
    age: Annotated[int, Field(ge=0, le=120, description="Возраст пользователя (от 0 до 120 лет)")]

# Список пользователей
users: List[Dict] = []

# Главная страница со списком пользователей
@app.get("/")
async def read_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

# Получение данных пользователя по ID
@app.get("/user/{user_id}")
async def read_user(
    request: Request,
    user_id: Annotated[int, Path(ge=1, description="ID пользователя, который нужно получить")]
):
    for user in users:
        if user["id"] == user_id:
            return templates.TemplateResponse("users.html", {"request": request, "user": user})
    raise HTTPException(status_code=404, detail="User not found")

# Удаление пользователя по ID
@app.delete("/user/{user_id}")
async def delete_user(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя, который нужно удалить")]
) -> User:
    for index, user in enumerate(users):
        if user["id"] == user_id:
            removed_user = users.pop(index)
            return User(**removed_user)
    raise HTTPException(status_code=404, detail="User was not found")

# Создание пользователя
@app.post("/user/{username}/{age}")
async def create_user(
    username: Annotated[str, Path(min_length=3, max_length=50, description="Имя пользователя")],
    age: Annotated[int, Path(ge=0, le=120, description="Возраст пользователя")]
):
    user_id = users[-1]["id"] + 1 if users else 1
    user = {"id": user_id, "username": username, "age": age}
    users.append(user)
    return User(**user)

# Обновление данных пользователя
@app.put("/user/{user_id}/{username}/{age}")
async def update_user(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя, который нужно обновить")],
    username: Annotated[str, Path(min_length=3, max_length=50, description="Новое имя пользователя")],
    age: Annotated[int, Path(ge=0, le=120, description="Новый возраст пользователя")]
) -> User:
    for user in users:
        if user["id"] == user_id:
            user["username"] = username
            user["age"] = age
            return User(**user)
    raise HTTPException(status_code=404, detail="User was not found")