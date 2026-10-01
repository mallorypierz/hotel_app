<script setup>
import { nextTick, ref } from 'vue'
import { useDiscovery } from '../composables/useDiscovery'
import DiscoveryForm from './DiscoveryForm.vue'
import DiscoveryList from './DiscoveryList.vue'
import DiscoveryMap from './DiscoveryMap.vue'

const { postcode, state, result, message, selectedPlaceId, retrySeconds, busy, edit, search, savedIds, pendingIds, storageFeedback, changeLocal, mapVersion } = useDiscovery()
const list = ref(null)
const map = ref(null)
async function select(id, source) {
  selectedPlaceId.value = id
  await nextTick()
  if (source === 'map') list.value?.reveal(id)
  else {
    map.value?.updateSelection()
    if (window.matchMedia('(max-width: 760px)').matches) map.value?.reveal()
  }
}
</script>

<template>
  <section
    id="discovery"
    class="discovery"
    aria-labelledby="discovery-title"
  >
    <p class="eyebrow">
      Live hotel discovery
    </p>
    <h1 id="discovery-title">
      Find hotels near a U.S. ZIP
    </h1>
    <p class="discovery-intro">
      Look up a U.S. ZIP and explore nearby hotels. For practice reservations, visit <a href="#search">Sample stays &amp; bookings</a>.
    </p>
    <DiscoveryForm
      :postcode="postcode"
      :busy="busy || pendingIds.size > 0"
      :invalid="state === 'invalid'"
      :retry-seconds="retrySeconds"
      @edit="edit"
      @search="search"
    />
    <div
      id="discovery-feedback"
      class="discovery-feedback"
      role="status"
      aria-live="polite"
    >
      <p v-if="state === 'initial'">
        Enter a ZIP to discover nearby hotels.
      </p>
      <p v-else-if="busy">
        Finding hotels near ZIP {{ postcode }}…
      </p>
      <template v-else-if="message">
        <p>{{ message }}</p>
        <button
          v-if="state === 'failure'"
          type="button"
          :disabled="retrySeconds > 0"
          @click="search"
        >
          Retry search
        </button>
      </template>
      <p v-else-if="state === 'empty' && result.source === 'local'">
        No saved hotels remain for this ZIP. Search again to check API results.
      </p>
      <p v-else-if="state === 'empty'">
        No nearby hotels were returned for ZIP {{ result.center.postcode }}. Coverage varies; this does not mean no hotels exist.
      </p>
      <p v-else-if="state === 'results'">
        {{ result.count }} {{ result.count === 1 ? 'hotel' : 'hotels' }} returned for ZIP {{ result.center.postcode }}.
      </p>
    </div>
    <template v-if="result">
      <p role="status">
        {{ storageFeedback }}
      </p>
      <div class="discovery-summary">
        <h2>{{ result.source === 'local' ? 'Saved locally' : 'API results' }}</h2>
        <p v-if="result.source === 'local'">
          Only hotels saved for this ZIP are shown. This is not a complete list of hotels in the area.
        </p>
        <h2>Returned ZIP center: {{ result.center.postcode }}<span v-if="result.center.locality"> · {{ result.center.locality }}</span> · US</h2>
        <p>{{ result.center.latitude }}, {{ result.center.longitude }} · Within 5 km of this postcode point, not the whole ZIP area or your location.</p>
        <p v-if="result.source !== 'local'">
          Up to {{ result.limit }} hotels per search. Coverage varies. Results are not a complete hotel inventory.<span v-if="result.limit_reached"> Additional places may exist.</span>
        </p>
        <p v-if="result.omitted_count || result.duplicates_removed">
          {{ result.omitted_count }} unusable records omitted · {{ result.duplicates_removed }} duplicate records removed.
        </p>
      </div>
      <div class="discovery-grid">
        <DiscoveryList
          v-if="result.hotels.length"
          ref="list"
          :hotels="result.hotels"
          :saved-ids="savedIds"
          :pending-ids="pendingIds"
          :local="result.source === 'local'"
          :selected-place-id="selectedPlaceId"
          @save="changeLocal($event)"
          @remove="changeLocal($event, true)"
          @select="select($event, 'list')"
        />
        <DiscoveryMap
          :key="mapVersion"
          ref="map"
          :result="result"
          :selected-place-id="selectedPlaceId"
          @select="select($event, 'map')"
        />
      </div>
      <p
        class="selection-announcement"
        role="status"
      >
        {{ selectedPlaceId ? `Selected: ${result.hotels.find(h => h.place_id === selectedPlaceId)?.name || 'Name not provided'}` : '' }}
      </p>
    </template>
    <p class="discovery-credit">
      Hotel information only · no booking service. <a href="https://www.geoapify.com/">Powered by Geoapify</a>
    </p>
  </section>
</template>

<style scoped>
.discovery { max-width: 1240px; margin: 0 auto 48px; padding: 40px 32px; scroll-margin-top: 16px; }
h1 { font-size: clamp(2rem, 4vw, 3.3rem); max-width: 900px; line-height: 1.1; }
.eyebrow { color: #80501e; }
a { color: #245b50; text-underline-offset: 3px; }
.discovery-intro { line-height: 1.6; margin-bottom: 28px; }
.discovery-feedback { margin: 24px 0; padding: 18px; border: 1px solid #c6d2cb; border-radius: 12px; background: white; }
.discovery-feedback p { margin: 0; }
.discovery-feedback button { margin-top: 12px; min-height: 44px; background: #245b50; color: white; border: 0; cursor: pointer; }
.discovery-summary { line-height: 1.6; overflow-wrap: anywhere; }
h2 { font-family: inherit; font-size: 1.25rem; }
.discovery-grid { display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: 24px; margin-top: 28px; }
.discovery-grid > :only-child { grid-column: 1 / -1; }
.discovery-credit { margin: 24px 0 0; line-height: 1.6; font-size: .9rem; }
.selection-announcement { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
@media (max-width: 760px) { .discovery { padding: 24px 20px; } .discovery-grid { display: flex; flex-direction: column; } .discovery-grid > :last-child { order: -1; width: 100%; } }
</style>
