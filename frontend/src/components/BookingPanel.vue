<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({ stay: { type: Object, default: null } })
const emit = defineEmits(['close'])
const travelers = ref([])
const traveler = ref(localStorage.getItem('wayfinder-traveler') || '')
const bookings = ref([])
const busy = ref(false)
const message = ref('')
const error = ref('')
const pending = ref(null)
const panel = ref(null)
const historyLoaded = ref(false)

async function request(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) throw new Error('The request could not be completed. Please try again.')
  return response.status === 204 ? null : response.json()
}
async function loadHistory() {
  historyLoaded.value = false
  bookings.value = []
  bookings.value = await request(`/api/bookings?user_id=${encodeURIComponent(traveler.value)}`)
  historyLoaded.value = true
}
async function run(action) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try { await action() } catch (e) { error.value = e.message } finally { busy.value = false }
}
onMounted(() => run(async () => {
  travelers.value = await request('/api/users')
  if (!travelers.value.some(user => user.user_id === traveler.value)) traveler.value = travelers.value[0]?.user_id || ''
  if (traveler.value) await loadHistory()
}))
async function changeTraveler() {
  localStorage.setItem('wayfinder-traveler', traveler.value)
  message.value = ''
  pending.value = null
  await run(loadHistory)
}
watch(() => props.stay, stay => {
  if (stay) {
    message.value = ''
    panel.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
})
watch(pending, value => {
  if (value) panel.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
})
async function book() {
  await run(async () => {
    const booking = await request('/api/bookings', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: traveler.value, trip_id: props.stay.trip_id }),
    })
    message.value = `Booking confirmed. Reference: ${booking.booking_id}. This is a simulated reservation.`
    emit('close')
    await loadHistory()
  })
}
async function mutate() {
  const { booking, action } = pending.value
  await run(async () => {
    await request(`/api/bookings/${booking.booking_id}${action === 'cancel' ? '/cancel' : ''}`, { method: action === 'cancel' ? 'PATCH' : 'DELETE' })
    message.value = action === 'cancel' ? 'Booking cancelled. The record remains in your history.' : 'Test booking deleted.'
    pending.value = null
    await loadHistory()
  })
}
</script>

<template>
  <section
    id="bookings"
    ref="panel"
    class="booking-section"
    :aria-busy="busy"
  >
    <p class="eyebrow">
      Your travel plans
    </p>
    <h2>Bookings & history</h2>
    <p>Choose a demo traveler. All reservations are simulated; no payment is required.</p>
    <label class="traveler-label">Demo traveler
      <select
        v-model="traveler"
        :disabled="busy"
        @change="changeTraveler"
      >
        <option
          v-for="user in travelers"
          :key="user.user_id"
          :value="user.user_id"
        >{{ user.display_name }}</option>
      </select>
    </label>
    <p
      v-if="error"
      role="alert"
      class="error-state"
    >
      {{ error }}
    </p>
    <p
      v-if="message"
      role="status"
      class="notice"
    >
      {{ message }}
    </p>
    <p
      v-if="busy"
      role="status"
    >
      Updating your travel plans…
    </p>
    <form
      v-if="stay"
      class="booking-card"
      @submit.prevent="book"
    >
      <h3>Review your stay</h3>
      <p><strong>{{ stay.name }}</strong> · {{ stay.city }}, {{ stay.state }}</p>
      <p>{{ stay.trip_name }} · {{ stay.check_in }} to {{ stay.check_out }}</p>
      <p>${{ stay.nightly_price }} per night. These are the fixed dates for this offered stay.</p>
      <button
        :disabled="busy || !traveler"
        type="submit"
      >
        Confirm simulated booking
      </button>
      <button
        :disabled="busy"
        type="button"
        @click="emit('close')"
      >
        Back to results
      </button>
    </form>
    <div
      v-if="pending"
      class="booking-card"
      role="alert"
    >
      <h3>{{ pending.action === 'cancel' ? 'Cancel this booking?' : 'Delete this test booking?' }}</h3>
      <p>{{ pending.booking.hotel_name }} · {{ pending.booking.booking_id }}</p>
      <p>{{ pending.action === 'cancel' ? 'The booking will remain in history with cancelled status.' : 'This permanently removes the record from booking history.' }}</p>
      <button
        :disabled="busy"
        type="button"
        @click="mutate"
      >
        {{ pending.action === 'cancel' ? 'Confirm cancellation' : 'Confirm deletion' }}
      </button>
      <button
        :disabled="busy"
        type="button"
        @click="pending = null"
      >
        Keep booking
      </button>
    </div>
    <p v-if="historyLoaded && !bookings.length && !busy">
      No bookings yet. Select a stay from the search results to get started.
    </p>
    <article
      v-for="booking in bookings"
      :key="booking.booking_id"
      class="booking-card"
    >
      <div class="booking-title">
        <h3>{{ booking.hotel_name }}</h3><span class="status-pill">{{ booking.status }}</span>
      </div>
      <p>{{ booking.city }}, {{ booking.state }} · {{ booking.trip_name }}</p>
      <p>{{ booking.check_in }} → {{ booking.check_out }} · ${{ booking.nightly_rate_usd }} / night</p>
      <p class="reference">
        Reference: {{ booking.booking_id }} · Booked {{ booking.booked_on }}
      </p>
      <button
        v-if="booking.status === 'confirmed'"
        :disabled="busy"
        type="button"
        @click="pending = { booking, action: 'cancel' }"
      >
        Cancel booking
      </button>
      <button
        :disabled="busy"
        type="button"
        @click="pending = { booking, action: 'delete' }"
      >
        Delete test booking
      </button>
    </article>
  </section>
</template>
