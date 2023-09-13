async def wss_close_ignore_exception(websocket):
    try:
        await websocket.close()
    except Exception:
        pass
