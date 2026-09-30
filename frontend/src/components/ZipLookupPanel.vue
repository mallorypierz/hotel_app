<script setup>
import { ref } from 'vue'

const postcode = ref('16802')
const requestedZip = ref('')
const loading = ref(false)
const location = ref(null)
const error = ref('')

const lookup = async () => {
  if (loading.value) return
  requestedZip.value = postcode.value.trim()
  if (!/^[0-9]{5}$/.test(requestedZip.value)) {
    location.value = null
    error.value = 'Enter a five-digit ZIP code.'
    return
  }
  loading.value = true
  location.value = null
  error.value = ''

  try {
    const response = await fetch('/api/demo/zip-location?' + new URLSearchParams({ postcode: requestedZip.value }))
    const result = await response.json()
    if (!response.ok) {
      error.value = typeof result.detail === 'string'
        ? result.detail
        : 'ZIP lookup is unavailable right now.'
      return
    }
    location.value = result
  } catch {
    error.value = 'Unable to complete the ZIP lookup. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section
    class="booking-section zip-panel"
    aria-labelledby="zip-lookup-heading"
  >
    <h2 id="zip-lookup-heading">
      ZIP lookup demonstration
    </h2>
    <p>Enter a U.S. ZIP code to look up its location with Geoapify.</p>
    <form @submit.prevent="lookup">
      <label for="zip-code">ZIP code</label>
      <input
        id="zip-code"
        v-model="postcode"
        type="text"
        inputmode="numeric"
        autocomplete="postal-code"
        pattern="[0-9]{5}"
        minlength="5"
        maxlength="5"
        required
        :disabled="loading"
        aria-describedby="zip-hint"
      >
      <button
        type="submit"
        :disabled="loading"
      >
        {{ loading ? 'Looking up…' : 'Look up ZIP' }}
      </button>
    </form>
    <p id="zip-hint">
      Use five digits, including any leading zero (for example, 02108).
    </p>
    <div
      class="zip-feedback"
      role="status"
      aria-live="polite"
      :aria-busy="loading"
    >
      <p v-if="loading">
        Looking up ZIP {{ requestedZip }}…
      </p>
      <p v-else-if="error">
        ZIP {{ requestedZip }}: {{ error }}
      </p>
      <div
        v-else-if="location"
        class="zip-table"
      >
        <table>
          <caption>Location for ZIP {{ location.postcode }}</caption>
          <thead>
            <tr>
              <th scope="col">
                ZIP code
              </th>
              <th scope="col">
                Locality
              </th>
              <th scope="col">
                Country
              </th>
              <th scope="col">
                Latitude
              </th>
              <th scope="col">
                Longitude
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ location.postcode }}</td>
              <td>{{ location.locality || 'Not provided' }}</td>
              <td>{{ location.country_code.toUpperCase() }}</td>
              <td>{{ location.latitude }}</td>
              <td>{{ location.longitude }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.zip-panel button {
  border: 0;
  background: #17332d;
  color: white;
  cursor: pointer;
}
.zip-panel button:disabled { cursor: wait; }
.zip-feedback { overflow-wrap: anywhere; }
.zip-feedback p { margin: 20px 0 0; }
form { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
label { font-weight: 700; }
input { width: 130px; padding: 12px; border: 1px solid #697d74; border-radius: 8px; font: inherit; }
.zip-table { overflow-x: auto; margin-top: 24px; }
table { width: 100%; border-collapse: collapse; text-align: left; }
caption { text-align: left; font-weight: 700; padding-bottom: 12px; }
th, td { padding: 12px; border-bottom: 1px solid #d6ddd8; white-space: nowrap; }
</style>
