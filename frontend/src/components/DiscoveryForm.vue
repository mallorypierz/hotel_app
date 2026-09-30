<script setup>
defineProps({ postcode: { type: String, required: true }, busy: Boolean, invalid: Boolean,
  retrySeconds: { type: Number, default: 0 } })
defineEmits(['edit', 'search'])
</script>

<template>
  <form
    class="discovery-form"
    novalidate
    @submit.prevent="$emit('search')"
  >
    <label for="discovery-zip">U.S. ZIP code</label>
    <div class="discovery-inputs">
      <input
        id="discovery-zip"
        :value="postcode"
        type="text"
        inputmode="numeric"
        autocomplete="postal-code"
        placeholder="e.g. 02108"
        required
        :aria-invalid="invalid"
        aria-describedby="discovery-hint discovery-feedback"
        @input="$emit('edit', $event.target.value)"
      >
      <button
        type="submit"
        :disabled="busy || retrySeconds > 0"
      >
        {{ busy ? 'Searching…' : 'Search hotels' }}
      </button>
    </div>
    <p id="discovery-hint">
      Use five digits, including leading zeros. Search within 5 km of the returned ZIP point.
    </p>
    <p v-if="retrySeconds">
      Please wait {{ retrySeconds }} seconds before searching again.
    </p>
  </form>
</template>

<style scoped>
label { display: block; font-weight: 700; margin-bottom: 8px; }
.discovery-inputs { display: flex; flex-wrap: wrap; gap: 12px; }
input { width: 210px; max-width: 100%; min-height: 48px; padding: 12px; border: 1px solid #61716c; border-radius: 8px; }
button { min-height: 48px; background: #245b50; color: white; border: 0; cursor: pointer; }
p { margin: 12px 0 0; color: #50625d; line-height: 1.5; }
</style>
