<script setup>
defineProps({ hotels: { type: Array, required: true }, selectedPlaceId: { type: String, default: null },
  savedIds: { type: Set, required: true }, pendingIds: { type: Set, required: true }, local: Boolean })
defineEmits(['select', 'save', 'remove'])
const buttons = new Map()
function reveal(id) { buttons.get(id)?.scrollIntoView({ block: 'nearest', behavior: 'instant' }) }
defineExpose({ reveal })
</script>

<template>
  <section
    aria-label="Live hotel results"
    class="hotel-list"
  >
    <h3>Hotels returned</h3>
    <ol>
      <li
        v-for="(hotel, index) in hotels"
        :key="hotel.place_id"
      >
        <button
          :ref="el => el ? buttons.set(hotel.place_id, el) : buttons.delete(hotel.place_id)"
          :aria-pressed="selectedPlaceId === hotel.place_id"
          @click="$emit('select', hotel.place_id)"
        >
          <strong>{{ index + 1 }}. {{ hotel.name || 'Name not provided' }}</strong>
          <span>{{ hotel.address || 'Address not provided' }}</span>
          <span class="selection">{{ selectedPlaceId === hotel.place_id ? 'Selected · shown on map' : 'Show on map' }}</span>
        </button>
        <div class="local-actions">
          <button
            type="button"
            :disabled="savedIds.has(hotel.place_id) || pendingIds.has(hotel.place_id)"
            @click="$emit('save', hotel)"
          >
            {{ savedIds.has(hotel.place_id) ? 'Saved locally' : pendingIds.has(hotel.place_id) ? 'Saving…' : 'Add to Local' }}
          </button>
          <button
            v-if="savedIds.has(hotel.place_id)"
            type="button"
            :disabled="pendingIds.has(hotel.place_id)"
            @click="$emit('remove', hotel)"
          >
            {{ pendingIds.has(hotel.place_id) ? 'Removing…' : 'Remove from Local' }}
          </button>
        </div>
        <div
          v-if="local"
          class="demo-nights"
        >
          <p><strong>Simulated classroom data</strong> — not API rates or availability.</p>
          <ul v-if="hotel.nights?.length">
            <li
              v-for="night in hotel.nights"
              :key="night.stay_date"
            >
              {{ night.stay_date }} · ${{ (night.nightly_rate_cents / 100).toFixed(2) }}/night · {{ night.rooms_available }} rooms available
            </li>
          </ul>
          <p v-else>
            No demo nights stored.
          </p>
        </div>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.local-actions { display: flex; gap: 8px; margin-top: 8px; }
.local-actions button { min-height: 44px; padding: 10px; text-align: center; }
button:disabled { cursor: default; opacity: .65; }
.demo-nights { padding: 0 12px; font-size: .9rem; line-height: 1.6; overflow-wrap: anywhere; }
h3 { font-size: 1.25rem; }
ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
button { width: 100%; text-align: left; color: #17332d; border: 1px solid #b7c7bf; background: white; padding: 18px; cursor: pointer; overflow-wrap: anywhere; }
button[aria-pressed=true] { border: 2px solid #245b50; padding: 17px; background: #e4eee8; }
strong, span { display: block; }
strong { font-size: 1.05rem; }
span { margin-top: 8px; line-height: 1.5; }
.selection { font-size: .85rem; color: #245b50; }
</style>
