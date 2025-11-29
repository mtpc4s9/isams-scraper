from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str

class ScrapeRequest(BaseModel):
    category_url: str

class Article(BaseModel):
    module_name: str
    category_level_1: str
    category_level_2: str
    article_name: str
    article_url: str
    content: str
    related_articles: List[str]

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    articles: List[Article] = []
    markdown_content: str = ""
