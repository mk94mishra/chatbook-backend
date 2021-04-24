from atom.user.token import router as user_private_router
from atom.user.public import router as user_public_router
from atom.chat.token import router as chat_private_router
from atom.action.token import router as action_private_router

from atom.option.token import router as option_private_router
from atom.option.public import router as option_public_router

# post section import
from atom.home.post.token import router as post_private_router
from atom.home.post_master.token import router as post_master_private_router
from atom.home.post_master.public import router as post_master_public_router
from atom.home.comment_master.token import router as comment_master_private_router


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
app.include_router(post_master_private_router)
app.include_router(post_master_public_router)
app.include_router(comment_master_private_router)