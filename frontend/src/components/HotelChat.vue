<script setup>
import { computed, ref } from 'vue'
import { useChat } from '../composables/useChat'
import ChatEvidence from './ChatEvidence.vue'
import ChatHotelCards from './ChatHotelCards.vue'

const { question, loading, result, error, evidence, retrySeconds, canSend, edit, send } = useChat()
const field = ref(null)
const label = 'Simulated course rates and availability—not real booking information'
const titles = { answer: 'Your saved-hotel answer', clarification: 'A little more detail', no_matches: 'No matching saved hotels', insufficient_data: 'Not enough saved data' }
const status = computed(() => loading.value ? 'Checking saved hotels…' : error.value ? 'Request failed' : result.value ? titles[result.value.status] : 'Ready for your question')
const answer = computed(() => result.value?.answer.startsWith(label + '\n') ? result.value.answer.slice(label.length + 1) : result.value?.answer)
</script>

<template>
  <section
    id="chatbot"
    class="chatbot"
    aria-labelledby="chat-title"
  >
    <p class="eyebrow">
      Your saved hotels
    </p>
    <h2 id="chat-title">
      Ask about your stay.
    </h2>
    <p class="simulation-label">
      {{ label }}
    </p>
    <div class="chat-layout">
      <form
        class="question-panel"
        @submit.prevent="send"
      >
        <label for="hotel-question">Your question</label>
        <textarea
          id="hotel-question"
          ref="field"
          :value="question"
          maxlength="2000"
          rows="6"
          aria-describedby="question-help question-privacy"
          placeholder="Include ZIP, check-in and checkout dates with year, rooms, and a nightly or total budget."
          @input="edit($event.target.value)"
        />
        <p id="question-help">
          Up to 2,000 characters. Enter adds a line; Tab to Send, then press Enter. Editing cancels the current request.
        </p>
        <p id="question-privacy">
          Your question and relevant saved hotel records are sent to OpenAI through our backend. Do not include private personal information.
        </p>
        <button
          type="submit"
          :aria-disabled="!canSend"
        >
          {{ loading ? 'Sending…' : 'Send' }}
        </button>
        <p
          v-if="retrySeconds"
          role="status"
        >
          Please wait {{ retrySeconds }} seconds before sending again.
        </p>
      </form>
      <div
        class="answer-panel"
        :aria-busy="loading"
      >
        <p
          class="status"
          role="status"
          aria-live="polite"
        >
          {{ status }}
        </p>
        <template v-if="error">
          <p role="alert">
            {{ error }}
          </p>
          <p>Check the question or private backend configuration as appropriate, then use Send to retry.</p>
        </template>
        <template v-else-if="result">
          <p class="answer">
            {{ answer }}
          </p>
          <ChatHotelCards
            :hotels="result.hotels"
            :intent="evidence?.intent"
          />
          <button
            type="button"
            class="edit-button"
            @click="field.focus()"
          >
            Edit question or dates
          </button>
        </template>
        <p v-else-if="loading">
          Reading local simulated data and preparing a grounded answer. This may take a moment.
        </p>
        <p v-else>
          Compare hotels you have saved with Add to Local. Ask about dates, room counts and a budget.
        </p>
        <p class="limitations">
          Coverage is limited to saved hotels and stored nights. Missing nights are unknown. No real availability or booking is offered.
        </p>
      </div>
    </div>
    <ChatEvidence
      v-if="evidence"
      :evidence="evidence"
      :status="result?.status"
    />
  </section>
</template>

<style scoped>
.chatbot { max-width: 1240px; padding: 48px 32px; margin: auto; line-height: 1.55; scroll-margin-top: 24px; }
h2 { font-size: clamp(2rem, 4vw, 3rem); margin-bottom: 20px; }
.eyebrow { color: #245b50; }
.simulation-label { padding: 14px 18px; background: #e9e1cd; border: 1px solid #b8a57a; border-radius: 10px; font-weight: 700; }
.chat-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); gap: 24px; align-items: start; }
.question-panel, .answer-panel { min-width: 0; padding: 24px; border-radius: 18px; background: white; border: 1px solid #d7dedb; overflow-wrap: anywhere; }
label, .status { font-weight: 700; }
textarea { display: block; width: 100%; resize: vertical; min-height: 150px; margin: 12px 0; padding: 14px; border: 1px solid #61716c; border-radius: 10px; font: inherit; color: inherit; }
textarea:focus-visible { outline: 3px solid #d66f3d; outline-offset: 4px; }
#question-help, #question-privacy, .limitations { color: #50625d; font-size: .9rem; }
button { min-height: 44px; background: #245b50; color: white; border: 0; cursor: pointer; }
button[aria-disabled="true"] { cursor: not-allowed; opacity: .55; }
.edit-button { margin-top: 20px; background: #e6eee8; color: #17332d; }
.answer { white-space: pre-wrap; }
.limitations { margin-top: 24px; margin-bottom: 0; }
@media (max-width: 760px) { .chatbot { padding: 32px 20px; } .chat-layout { grid-template-columns: 1fr; } .question-panel, .answer-panel { padding: 20px; } button { width: 100%; } }
</style>
