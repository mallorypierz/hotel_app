import { computed, onBeforeUnmount, ref } from 'vue'

export function useDiscovery() {
  const postcode = ref('')
  const state = ref('initial')
  const result = ref(null)
  const message = ref('')
  const selectedPlaceId = ref(null)
  const retrySeconds = ref(0)
  const busy = computed(() => state.value === 'loading')
  let version = 0
  let controller
  let countdown

  function clearSearch() {
    version++
    controller?.abort()
    result.value = null
    selectedPlaceId.value = null
    message.value = ''
    state.value = 'initial'
  }

  function edit(value) {
    clearSearch()
    postcode.value = value
  }

  async function search() {
    if (busy.value || retrySeconds.value) return
    clearSearch()
    const zip = postcode.value.trim()
    postcode.value = zip
    if (!/^[0-9]{5}$/.test(zip)) {
      state.value = 'invalid'
      message.value = 'Enter a five-digit U.S. ZIP code, including any leading zero.'
      return
    }
    const current = version
    const requestController = new AbortController()
    controller = requestController
    const timeout = setTimeout(() => requestController.abort(), 25000)
    state.value = 'loading'
    try {
      const response = await fetch('/api/discovery/hotels?' + new URLSearchParams({ postcode: zip }), {
        signal: requestController.signal,
      })
      const data = await response.json()
      if (current !== version) return
      if (!response.ok) {
        if (response.status === 422) {
          state.value = 'invalid'
          message.value = 'Enter a five-digit U.S. ZIP code.'
        } else if (response.status === 404) {
          state.value = 'unresolved'
          message.value = `The requested U.S. ZIP ${zip} could not be located. Check the ZIP and try again.`
        } else {
          state.value = 'failure'
          message.value = data.detail?.code === 'service_unconfigured'
            ? 'Hotel search is not configured. Please try again after the service is configured.'
            : data.detail?.code === 'provider_limited'
              ? 'Hotel search is temporarily limited. Please try again later.'
              : 'Hotel search could not be completed. Please try again.'
          const delay = response.headers.get('Retry-After')
          if (response.status === 503 && /^[0-9]{1,6}$/.test(delay || '')) {
            const until = Date.now() + Number(delay) * 1000
            clearInterval(countdown)
            retrySeconds.value = Number(delay)
            countdown = setInterval(() => {
              retrySeconds.value = Math.max(0, Math.ceil((until - Date.now()) / 1000))
              if (!retrySeconds.value) clearInterval(countdown)
            }, 1000)
          }
        }
        return
      }
      if (data.center?.postcode !== zip || !Array.isArray(data.hotels) || data.count !== data.hotels.length) {
        throw new Error('Invalid response')
      }
      result.value = data
      state.value = data.hotels.length ? 'results' : 'empty'
    } catch {
      if (current !== version) return
      state.value = 'failure'
      message.value = 'Hotel search could not be completed. Check your connection and try again.'
    } finally {
      clearTimeout(timeout)
    }
  }

  onBeforeUnmount(() => { clearSearch(); clearInterval(countdown) })
  return { postcode, state, result, message, selectedPlaceId, retrySeconds, busy, edit, search }
}
