"""Small HTTP adapter; no SQL or provider networking here."""
from fastapi import HTTPException
from . import chat_controller
from .chat_contracts import ChatRequest, ChatResponse


def post_chat(payload: ChatRequest):
    try:
        return chat_controller.chat(payload)
    except chat_controller.ChatFailure as error:
        status = 503 if error.code in {'unconfigured', 'configuration', 'access_denied', 'quota_exceeded',
                                       'provider_limited', 'storage_unavailable'} else 504 if error.code == 'provider_timeout' else 502
        headers = {'Retry-After': str(error.retry_after)} if error.retry_after is not None else None
        raise HTTPException(status, {'code': error.code, 'message': error.message,
                                     'stage': error.stage, 'evidence': error.evidence}, headers=headers) from None


def register(app):
    app.add_api_route('/api/chat', post_chat, methods=['POST'], response_model=ChatResponse)
