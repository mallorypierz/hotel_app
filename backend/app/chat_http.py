"""Bound request bytes before JSON parsing, only for the chatbot endpoint."""
from starlette.responses import JSONResponse

MAX_CHAT_BODY = 16 * 1024


class ChatBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['path'].rstrip('/') != '/api/chat' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body = message.get('body', b'')
            size += len(body)
            if size > MAX_CHAT_BODY:
                response = JSONResponse({'detail': {'code': 'question_too_large',
                                         'message': 'The chat request is too large.'}}, status_code=413)
                return await response(scope, receive, send)
            chunks.append(body)
            if not message.get('more_body', False):
                break
        pending = True

        async def bounded_receive():
            nonlocal pending
            if pending:
                pending = False
                return {'type': 'http.request', 'body': b''.join(chunks), 'more_body': False}
            return {'type': 'http.disconnect'}

        await self.app(scope, bounded_receive, send)
