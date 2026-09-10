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
      <span>City</span>
      <input
        v-model="city"
        type="search"
        placeholder="Try Boston or State College"
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
