from user.private import router as user_private_router
from user.public import router as user_public_router
from rating.private import router as rating_private_router
from chat.private import router as chat_private_router

from admin.option.private import router as option_private_router
from admin.option.public import router as option_public_router

from admin.orderby.public import router as orderby_public_router
from admin.faq.public import router as faq_public_router
from admin.official.public import router as official_public_router

# post section import
from home.post.private import router as post_private_router
from home.comment.private import router as comment_private_router
from home.like.private import router as like_private_router
from home.bookmark.private import router as bookmark_private_router
from home.spam.private import router as spam_private_router
from home.card.post.public import router as card_post_public_router
from home.card.post.private import router as card_post_private_router
from home.card.comment.public import router as card_comment_public_router
from home.card.comment.private import router as card_comment_private_router


from fastapi import FastAPI

# set openapi_url = "" in production
app = FastAPI(openapi_url = "/openapi.json", title = "chatbook backend", version = "1.0")

# include routers
app.include_router(user_private_router)
app.include_router(user_public_router)
app.include_router(rating_private_router)
app.include_router(chat_private_router)

# include admin
app.include_router(option_public_router)
app.include_router(option_private_router)
app.include_router(orderby_public_router)
app.include_router(faq_public_router)
app.include_router(official_public_router)

# post section
app.include_router(post_private_router)
app.include_router(comment_private_router)
app.include_router(like_private_router)
app.include_router(bookmark_private_router)
app.include_router(spam_private_router)
app.include_router(card_post_public_router)
app.include_router(card_post_private_router)
app.include_router(card_comment_public_router)
app.include_router(card_comment_private_router)