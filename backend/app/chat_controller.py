"""Two model requests separated by checked local retrieval; no transport in routes."""
import json
import time
from . import database, llm_provider
from .chat_contracts import ChatRequest, ChatResponse, QueryDecision, AnswerDecision, SIMULATED_LABEL
from .chat_queries import execute_query, RetrievalError, MAX_ROWS, MAX_RESULT_BYTES
from .chat_prompts import QUERY_RULES, ANSWER_RULES
from .chat_stays import CANONICAL_SQL, CLARIFICATION, explicit_intent, verify_records, assess, render_answer


class ChatFailure(Exception):
    def __init__(self, error, stage, evidence):
        self.code = error.code
        self.message = str(error)
        self.stage = stage
        self.evidence = evidence
        self.retry_after = getattr(error, 'retry_after', None)
        super().__init__(self.message)


def retrieve(proposal):
    return execute_query(proposal, database.DATABASE)


def chat(request: ChatRequest) -> ChatResponse:
    deadline = time.monotonic() + 45
    question = request.question
    stage = 'query_model'
    evidence = {'question': question, 'provider': 'OpenAI', 'model': llm_provider.MODEL,
                'proposal': None, 'validation': 'not_reached', 'retrieved_records': [],
                'retrieval': {'row_limit': MAX_ROWS, 'byte_limit': MAX_RESULT_BYTES,
                              'row_count': None, 'truncated': False, 'complete': False},
                'model_calls': []}

    def call(instructions, payload, contract, name):
        record = {'stage': name, 'status': 'started'}
        evidence['model_calls'].append(record)
        try:
            reply = llm_provider.request_structured(instructions, payload, contract, name, deadline)
        except llm_provider.ModelError:
            record['status'] = 'failed'
            raise
        record.update(status='completed', response_id=reply.response_id, usage=reply.usage, model=reply.model)
        return reply.value

    try:
        decision = call(QUERY_RULES, {'question': question}, QueryDecision, 'hotel_query')
        if decision.kind == 'clarification':
            if decision.intent is not None or decision.proposal is not None or not decision.clarification:
                raise llm_provider.ModelError('invalid_model_response')
            return ChatResponse(status='clarification', answer=decision.clarification, hotels=[], evidence=evidence)
        if decision.intent is None or decision.proposal is None or decision.clarification is not None:
            raise llm_provider.ModelError('invalid_model_response')
        intent = explicit_intent(question)
        if intent is None:
            return ChatResponse(status='clarification', answer=CLARIFICATION, hotels=[], evidence=evidence)
        if intent != decision.intent:
            raise llm_provider.ModelError('invalid_model_response')
        evidence['intent'] = intent.model_dump()
        evidence['proposal'] = decision.proposal.model_dump()
        stage = 'retrieval'
        evidence['validation'] = 'checking'
        retrieved = retrieve(decision.proposal)
        # A separate trusted read verifies provenance and completeness, not a replacement
        # for the model-proposed SQL. Any mismatch fails closed, without answering.
        expected = retrieve({'sql': CANONICAL_SQL,
                             'parameters': [intent.check_in, intent.check_out, intent.postcode]})
        verify_records(retrieved, expected)
        status, facts = assess(intent, retrieved.records)
        evidence['validation'] = 'passed_read_only_and_record_verification'
        evidence['retrieved_records'] = retrieved.records
        evidence['retrieval'].update(row_count=retrieved.row_count, result_bytes=retrieved.result_bytes,
                                     complete=True, scope='All locally saved hotels associated with requested ZIP and stay dates')
        stage = 'answer_model'
        answer_decision = call(ANSWER_RULES, {'question': question, 'intent': intent.model_dump(),
                              'retrieved_records': retrieved.records, 'checked_hotels': facts,
                              'status': status, 'retrieval': evidence['retrieval'],
                              'simulated_label': SIMULATED_LABEL}, AnswerDecision, 'hotel_answer')
        try:
            answer = render_answer(answer_decision, status, facts, intent)
        except ValueError:
            raise llm_provider.ModelError('invalid_model_response') from None
        answer = SIMULATED_LABEL + '\n' + answer
        result = ChatResponse(status=status, answer=answer, hotels=facts, evidence=evidence)
        if len(result.model_dump_json().encode('utf-8')) > 96 * 1024:
            raise llm_provider.ModelError('invalid_model_response')
        return result
    except (llm_provider.ModelError, RetrievalError) as error:
        if stage == 'retrieval':
            evidence['validation'] = 'rejected_or_limit_exceeded'
        raise ChatFailure(error, stage, evidence) from None
