from atom.user.token import router as user_token_router
from atom.user.public import router as user_public_router
from atom.chat.token import router as chat_token_router

from atom.action.bookmark.token import router as bookmark_token_router
from atom.action.like.token import router as like_token_router
from atom.action.comment.token import router as comment_token_router
from atom.action.spam.token import router as spam_token_router
from atom.action.block.token import router as block_token_router
from atom.action.rating.token import router as rating_token_router

from atom.option.token import router as option_token_router
from atom.option.public import router as option_public_router

# post section import
from atom.post.token import router as post_token_router
from atom.feed.post.token import router as post_master_token_router
from atom.feed.post.public import router as post_master_public_router
from atom.feed.comment.token import router as comment_master_token_router


from fastapi import FastAPI

# set openapi_url = "" in production
app = FastAPI(openapi_url = "/openapi.json", title = "chatbook backend", version = "1.0")

# include routers
app.include_router(user_token_router)
app.include_router(user_public_router)
app.include_router(chat_token_router)

app.include_router(bookmark_token_router)
app.include_router(like_token_router)
app.include_router(spam_token_router)
app.include_router(comment_token_router)
app.include_router(block_token_router)
app.include_router(rating_token_router)

# include admin
app.include_router(option_public_router)
app.include_router(option_token_router)

# post section
app.include_router(post_token_router)
app.include_router(post_master_token_router)
app.include_router(post_master_public_router)
app.include_router(comment_master_token_router)