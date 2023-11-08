from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

"""
    models
"""

class Post(BaseModel):
  title: str
  content: str
  rating: Optional[str] = None


db_posts = [{"title": "favorite foods", "content": "banana, apple, orange", "id": 1},
            {"title": "sports", "content": "soccer ball, basketball, pingpong ball", "id": 2}]
curr_id = [2]

def find_post_idx(id):
  for i, p in enumerate(db_posts):
    if p['id'] == id:
      return i

"""
    routes
"""

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
  return {"data": "Hello, World!"}

@app.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts():
  return {"data": db_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
  post_dict = post.dict()
  curr_id[0] += 1
  post_dict['id'] = curr_id[0]
  db_posts.append(post_dict)
  return {"data": post_dict}

@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
async def get_post(id: int):
  idx = find_post_idx(id)
  if idx is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  return {"data": db_posts[idx]}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
  idx = find_post_idx(id)
  if idx is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  db_posts.pop(idx)
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_205_RESET_CONTENT)
async def update_post(id: int, post: Post):
  idx = find_post_idx(id)
  if idx is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'post with id: {id} was not found!')
  post_dict = post.dict()
  post_dict['id'] = id
  db_posts[idx] = post_dict
  return {"data": post_dict}
