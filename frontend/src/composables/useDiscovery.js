import { computed, onBeforeUnmount, ref } from 'vue'

export function useDiscovery() {
  const postcode = ref('')
  const state = ref('initial')
  const result = ref(null)
  const message = ref('')
  const selectedPlaceId = ref(null)
  const retrySeconds = ref(0)
  const savedIds = ref(new Set())
  const pendingIds = ref(new Set())
  const storageFeedback = ref('')
  const mapVersion = ref(0)
  const busy = computed(() => state.value === 'loading')
  let version = 0
  let controller
  let countdown

  function clearSearch() {
    version++
    storageFeedback.value = ''
    mapVersion.value++
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
    if (busy.value || retrySeconds.value || pendingIds.value.size) return
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
    let stage = 'local'
    try {
      const localResponse = await fetch('/api/local-hotels?' + new URLSearchParams({ postcode: zip }), {
        signal: requestController.signal,
      })
      if (!localResponse.ok) throw new Error('Local request failed')
      const local = await localResponse.json()
      if (current !== version) return
      if (local.postcode !== zip || !Array.isArray(local.hotels) || local.count !== local.hotels.length
        || !Array.isArray(local.saved_ids) || (local.count && local.center?.postcode !== zip)) {
        throw new Error('Invalid local response')
      }
      savedIds.value = new Set(local.saved_ids)
      if (local.count) {
        result.value = local
        state.value = 'results'
        return
      }
      stage = 'api'
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
      result.value = { ...data, source: 'api' }
      state.value = data.hotels.length ? 'results' : 'empty'
    } catch {
      if (current !== version) return
      state.value = 'failure'
      message.value = stage === 'local'
        ? 'Saved hotels could not be checked. No API search was made. Check your connection and retry.'
        : 'Hotel search could not be completed. Check your connection and try again.'
    } finally {
      clearTimeout(timeout)
    }
  }

  async function changeLocal(hotel, remove = false) {
    const id = hotel.place_id
    if (pendingIds.value.has(id) || !result.value) return
    const current = version
    const center = result.value.center
    pendingIds.value.add(id)
    storageFeedback.value = ''
    const abort = new AbortController()
    const timeout = setTimeout(() => abort.abort(), 15000)
    try {
      const response = await fetch('/api/local-hotels' + (remove ? '?' + new URLSearchParams({ hotel_id: id }) : ''), {
        method: remove ? 'DELETE' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abort.signal,
        body: remove ? undefined : JSON.stringify({
          hotel: { place_id: id, name: hotel.name, address: hotel.address,
            latitude: hotel.latitude, longitude: hotel.longitude }, center,
        }),
      })
      if (!response.ok) throw new Error('Storage request failed')
      if (remove) savedIds.value.delete(id)
      else savedIds.value.add(id)
      if (current !== version) return
      if (remove && result.value.source === 'local') {
        result.value = { ...result.value, hotels: result.value.hotels.filter(h => h.place_id !== id),
          count: result.value.count - 1 }
        if (selectedPlaceId.value === id) selectedPlaceId.value = null
        mapVersion.value++
        state.value = result.value.count ? 'results' : 'empty'
      }
      storageFeedback.value = remove
        ? 'Removed from local storage, including all ZIP associations and demo nights.'
        : 'Saved locally. Demo nights are simulated classroom data.'
    } catch {
      if (current === version) storageFeedback.value = remove
        ? 'Removal could not be confirmed. Retry or search again to check database status.'
        : 'Save could not be confirmed. Retry or search again to check database status.'
    } finally {
      clearTimeout(timeout)
      pendingIds.value.delete(id)
    }
  }

  onBeforeUnmount(() => { clearSearch(); clearInterval(countdown) })
  return { postcode, state, result, message, selectedPlaceId, retrySeconds, busy, edit, search, savedIds, pendingIds, storageFeedback, changeLocal, mapVersion }
}
