from fastapi import FastAPI
import auth
import users
import files


app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(files.router)


@app.get("/", tags=["Root"])
async def index():
    return {"message": "Hello FastAPI"}