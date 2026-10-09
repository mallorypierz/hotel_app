import { computed, onBeforeUnmount, ref } from 'vue'

const statuses = new Set(['answer', 'clarification', 'no_matches', 'insufficient_data'])

export function useChat() {
  const question = ref('')
  const loading = ref(false)
  const result = ref(null)
  const error = ref('')
  const evidence = ref(null)
  const retrySeconds = ref(0)
  let version = 0
  let controller
  let cooldown
  const canSend = computed(() => question.value.trim().length > 0 && !loading.value && !retrySeconds.value)

  function edit(value) {
    question.value = value
    version++
    controller?.abort()
    loading.value = false
    result.value = null
    evidence.value = null
    error.value = ''
  }

  async function send() {
    if (!canSend.value) return
    const current = ++version
    const original = question.value.trim()
    controller = new AbortController()
    const request = controller
    const timeout = setTimeout(() => request.abort(), 50000)
    loading.value = true
    result.value = null
    evidence.value = null
    error.value = ''
    try {
      const response = await fetch('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: original }), signal: request.signal,
      })
      const text = await response.text()
      if (current !== version) return
      if (text.length > 131072) throw new Error('The response was too large. Please try a more focused question.')
      let data
      try { data = JSON.parse(text) } catch { throw new Error('The server returned an unreadable response. Please try again.') }
      const trace = response.ok ? data.evidence : data.detail?.evidence
      if (trace?.question === original) evidence.value = trace
      if (!response.ok) {
        const delay = response.headers.get('Retry-After')
        if (/^\d{1,6}$/.test(delay || '')) {
          retrySeconds.value = Number(delay)
          clearInterval(cooldown)
          cooldown = setInterval(() => {
            retrySeconds.value = Math.max(0, retrySeconds.value - 1)
            if (!retrySeconds.value) clearInterval(cooldown)
          }, 1000)
        }
        throw new Error(typeof data.detail?.message === 'string' ? data.detail.message :
          response.status === 422 ? 'Enter a question of 1–2,000 characters.' : 'The assistant is unavailable. Please try again later.')
      }
      if (!statuses.has(data.status) || typeof data.answer !== 'string' || !Array.isArray(data.hotels) || trace?.question !== original) {
        evidence.value = null
        throw new Error('The server returned an incomplete response. Please try again.')
      }
      result.value = data
    } catch (failure) {
      if (current !== version) return
      error.value = failure.name === 'AbortError' ? 'The request timed out. Please try again.' :
        failure instanceof TypeError ? 'Could not reach the assistant. Check the connection and try again.' : failure.message
    } finally {
      clearTimeout(timeout)
      if (current === version) loading.value = false
    }
  }

  onBeforeUnmount(() => { version++; controller?.abort(); clearInterval(cooldown) })
  return { question, loading, result, error, evidence, retrySeconds, canSend, edit, send }
}
