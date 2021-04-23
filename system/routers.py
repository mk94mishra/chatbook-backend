from user.private import router as user_private_router
from user.public import router as user_public_router
from atom.chat.private import router as chat_private_router
from atom.action.private import router as action_private_router

from atom.option.private import router as option_private_router
from atom.option.public import router as option_public_router

# post section import
from atom.home.post.private import router as post_private_router
from atom.home.card_post.private import router as card_post_private_router
from atom.home.card_post.public import router as card_post_public_router
from atom.home.card_comment.private import router as card_comment_private_router


from fastapi import FastAPI

# set openapi_url = "" in production
app = FastAPI(openapi_url = "/openapi.json", title = "chatbook backend", version = "1.0")

# include routers
app.include_router(user_private_router)
app.include_router(user_public_router)
app.include_router(chat_private_router)
app.include_router(action_private_router)

# include admin
app.include_router(option_public_router)
app.include_router(option_private_router)

# post section
app.include_router(post_private_router)
app.include_router(card_post_private_router)
app.include_router(card_post_public_router)
app.include_router(card_comment_private_router)