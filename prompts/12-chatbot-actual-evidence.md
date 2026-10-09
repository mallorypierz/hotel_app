# Actual chatbot prompt excerpts — October 8, 2026

These are selected verbatim excerpts from the student's messages in this task,
not reconstructed ideal prompts or claims of independent student authorship.
The linked artifacts show the resulting work and tests; code remains uncommitted.

| Actual excerpt | Work/evidence |
| --- | --- |
| “Use Open AI API as this project's single chatbot provider.” | [Dated research](../docs/chatbot-research.md), fixed model/transport in [llm_provider.py](../backend/app/llm_provider.py); no other provider fallback |
| “Before implementing the chatbot, create and save an early desktop/mobile mockup image and a short design explanation under docs/.” | [Original desktop](../docs/chatbot-desktop-v1.png), [mobile](../docs/chatbot-mobile-v1.png), [design](../docs/chatbot-design.md), preserved v1 hashes |
| “Do not rely only on regex or a SELECT prefix.” | [Restricted executor](../backend/app/chat_queries.py), [90 query-boundary cases](../backend/tests/test_chat_queries.py), [rejection evidence](../docs/chatbot-verification-evidence/rejected-queries.json) |
| “For multi-night stays, include check-in and exclude checkout; require a record for every requested night and sufficient rooms on every night; sum nightly_rate_cents for the stay.” | [Independent stay checks](../backend/app/chat_stays.py), [two-request tests](../backend/tests/test_chat.py), [$260/$300 comparison trace](../docs/chatbot-verification-evidence/mock-success.json) |
| “Prevent duplicate submissions and stale responses. Render model output safely without raw HTML injection.” | [Vue composable](../frontend/src/composables/useChat.js), [view](../frontend/src/components/HotelChat.vue), [browser results](../docs/chatbot-verification-evidence/chatbot-browser.json) |
| “Run a verification-only pass. Do not change source code; report failures with focused repair prompts.” | [Verification](../docs/chatbot-verification.md), [source/data preservation](../docs/chatbot-verification-evidence/preservation.json); no configured key, live status incomplete |
| “Do not invent failures, successful calls, recordings, model identities, or access verification.” | [Revised report](../report.md) explicitly identifies missing live trace, video, assessed commit and instructor access |

Genuine corrections are documented in the [AI evidence log](../docs/chatbot-ai-evidence.md),
including the native-disabled Send focus failure and its aria-disabled/guard revision.
