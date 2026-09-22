<script setup>
import { ref } from 'vue'

const emit = defineEmits(['search'])
const city = ref('')

const submit = () => emit('search', city.value.trim())
</script>

<template>
  <form
    class="search-panel"
    @submit.prevent="submit"
  >
    <label class="field">
      <span>Hotel name or city</span>
      <input
        v-model="city"
        type="search"
        placeholder="Try Inn, Trail, or Boston"
        maxlength="80"
        required
      >
    </label>

    <button
      class="search-button"
      type="submit"
    >
      Search
    </button>
  </form>
</template>
