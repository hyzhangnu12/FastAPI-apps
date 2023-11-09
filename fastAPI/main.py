from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from psycopg.rows import dict_row
import psycopg
import time

app = FastAPI()

"""
    database connections
"""
while True:
  try:
    conn_uri = f'postgresql://dbuser:ewq123@localhost:5432/fastapi'
    conn = psycopg.connect(conn_uri, row_factory=dict_row)
    cursor = conn.cursor()
    print("Database connection was successfully!")
    break
  except Exception as error:
    print("Connecting to database failed!")
    print(f"Error: {error}")
    time.sleep(5)

"""
    models
"""

class Post(BaseModel):
  title: str
  content: str
  published: bool = False
  rating: Optional[str] = None

"""
    routes
"""

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
  return {"data": "Hello, World!"}

@app.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts():
  cursor.execute(""" SELECT * FROM public."Posts" """)
  return {"data": cursor.fetchall()}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
  cursor.execute(""" INSERT INTO public."Posts" (title, content, published) VALUES (%s, %s, %s) RETURNING * """, \
    (post.title, post.content, post.published))
  new_post = cursor.fetchone()
  conn.commit()
  return {"data": new_post}

@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
async def get_post(id: int):
  cursor.execute(""" SELECT * FROM public."Posts" WHERE id = %s """, (str(id),))
  post = cursor.fetchone()
  if post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  return {"data": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
  cursor.execute(""" DELETE FROM public."Posts" WHERE id = %s RETURNING * """, (str(id),))
  deleted_post = cursor.fetchone()
  conn.commit()
  if deleted_post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  print(deleted_post)
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_205_RESET_CONTENT)
async def update_post(id: int, post: Post):
  cursor.execute(""" UPDATE public."Posts" SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, \
    (post.title, post.content, post.published, str(id)))
  new_post = cursor.fetchone()
  conn.commit()
  if new_post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  return {"data": new_post}
