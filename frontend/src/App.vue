<script setup>
import { ref } from 'vue'

import HotelTable from './components/HotelTable.vue'
import SearchBar from './components/SearchBar.vue'

const hotels = ref([])
const loading = ref(false)
const error = ref('')
const hasSearched = ref(false)

const searchHotels = async (city) => {
  loading.value = true
  error.value = ''
  hasSearched.value = true

  const params = new URLSearchParams({ city })

  try {
    const response = await fetch(`/api/hotels?${params}`)
    if (!response.ok) {
      const message = response.status === 422
        ? 'Enter a city to search for hotel stays.'
        : 'The hotel search is unavailable right now.'
      throw new Error(message)
    }
    const result = await response.json()
    hotels.value = result.hotels
  } catch (requestError) {
    hotels.value = []
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <header class="site-header">
    <a
      class="brand"
      href="#"
    >Wayfinder</a>
    <nav aria-label="Main navigation">
      <a href="#search">Find a stay</a>
      <span>Trips</span>
    </nav>
  </header>

  <main>
    <section
      id="search"
      class="hero"
    >
      <div class="hero-copy">
        <p class="eyebrow">
          Stay somewhere memorable
        </p>
        <h1>Your next favorite place is closer than you think.</h1>
        <p>Search sample trip data by city and compare matching hotel stays.</p>
      </div>
      <SearchBar @search="searchHotels" />
    </section>

    <section
      class="results"
      aria-live="polite"
      aria-busy="loading"
    >
      <div
        v-if="loading"
        class="status-card"
      >
        Finding your best matches…
      </div>
      <div
        v-else-if="error"
        class="status-card error-state"
      >
        <h2>We couldn’t complete that search</h2>
        <p>{{ error }}</p>
      </div>
      <div
        v-else-if="hasSearched && hotels.length === 0"
        class="status-card"
      >
        <h2>No stays matched</h2>
        <p>No results match that city. Check the spelling or try another city.</p>
      </div>
      <template v-else-if="hotels.length">
        <div class="results-heading">
          <div>
            <p class="eyebrow">
              Available stays
            </p>
            <h2>{{ hotels.length }} {{ hotels.length === 1 ? 'place' : 'places' }} to consider</h2>
          </div>
        </div>
        <HotelTable :hotels="hotels" />
      </template>
      <div
        v-else
        class="intro-card"
      >
        <p>Enter a city to find matching hotel stays.</p>
      </div>
    </section>
  </main>

  <footer>
    <p>Wayfinder is a sample booking experience. No real reservations are made.</p>
  </footer>
</template>
