# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


from aiohttp import web

async def web_server():
    async def handle(request):
        return web.Response(text="bot is running!")

    app = web.Application()
    app.router.add_get("/", handle)
    return app


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat