<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({ result: { type: Object, required: true }, selectedPlaceId: { type: String, default: null } })
const emit = defineEmits(['select'])
const container = ref(null)
const tileFailed = ref(false)
const selected = computed(() => props.result.hotels.find(hotel => hotel.place_id === props.selectedPlaceId))
let map
let radius
let observer
const markers = new Map()
function resetView() { map?.fitBounds(radius.getBounds(), { padding: [16, 16], animate: false }) }
function reveal() { container.value?.scrollIntoView({ block: 'nearest', behavior: 'instant' }) }
defineExpose({ reveal, updateSelection })

function updateSelection() {
  for (const [id, marker] of markers) {
    const active = id === props.selectedPlaceId
    const element = marker.getElement()
    element?.classList.toggle('is-selected', active)
    element?.setAttribute('aria-pressed', String(active))
    marker.setZIndexOffset(active ? 1000 : 0)
    if (active) map.panTo(marker.getLatLng(), { animate: false })
  }
}

onMounted(() => {
  const center = props.result.center
  map = L.map(container.value, { scrollWheelZoom: false }).setView([center.latitude, center.longitude], 12)
  // Keyless, viewport-only tiles; browser cache and Referer are left intact.
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, keepBuffer: 0,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  }).on('tileerror', () => { tileFailed.value = true }).addTo(map)
  radius = L.circle([center.latitude, center.longitude], {
    radius: props.result.radius_meters, color: '#245b50', weight: 2, fillOpacity: 0.06,
  }).addTo(map)
  L.marker([center.latitude, center.longitude], {
    icon: L.divIcon({ className: 'zip-center', html: '<span aria-hidden="true">■</span>', iconSize: [20, 20] }),
    keyboard: false, interactive: false, title: `ZIP ${center.postcode} center`,
  }).addTo(map)
  props.result.hotels.forEach((hotel, index) => {
    const label = `${index + 1}. ${hotel.name || 'Name not provided'} — select hotel`
    const marker = L.marker([hotel.latitude, hotel.longitude], {
      icon: L.divIcon({ className: 'hotel-marker', html: String(index + 1), iconSize: [44, 44], iconAnchor: [22, 22] }),
      keyboard: true, title: label, alt: label,
    }).addTo(map).on('click', () => emit('select', hotel.place_id))
    const element = marker.getElement()
    element.setAttribute('aria-label', label)
    element.setAttribute('aria-pressed', 'false')
    element.addEventListener('keydown', event => {
      if (event.key === ' ' || event.key === 'Enter') { event.preventDefault(); emit('select', hotel.place_id) }
    })
    markers.set(hotel.place_id, marker)
  })
  resetView()
  updateSelection()
  observer = new ResizeObserver(() => map.invalidateSize({ pan: false }))
  observer.observe(container.value)
})
watch(() => props.selectedPlaceId, updateSelection)
onBeforeUnmount(() => { observer?.disconnect(); map?.remove(); markers.clear() })
</script>

<template>
  <section
    class="map-panel"
    aria-label="Live hotel map"
  >
    <div class="map-heading">
      <h3>Within 5 km</h3><button
        type="button"
        @click="resetView"
      >
        Show search area
      </button>
    </div>
    <p>■ ZIP center · numbered markers match the hotel list. Use Tab and Enter or Space to select.</p>
    <div
      ref="container"
      class="hotel-map"
      aria-label="Hotel map; arrow keys pan, plus and minus zoom"
    />
    <p
      v-if="tileFailed"
      class="tile-warning"
      role="status"
    >
      Map imagery could not fully load. Hotel results and markers remain available; use the list for hotel details.
    </p>
    <p class="map-detail">
      {{ selected ? `Selected: ${selected.name || 'Name not provided'}` : 'Select a hotel in the list or on the map.' }}
    </p>
  </section>
</template>

<style scoped>
.map-panel { min-width: 0; padding: 16px; background: #edf0e9; border: 1px solid #c6d2cb; border-radius: 16px; align-self: start; position: sticky; top: 16px; }
.map-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
h3 { margin: 0; }
button { background: white; color: #17332d; border: 1px solid #61716c; min-height: 44px; cursor: pointer; }
p { font-size: .9rem; line-height: 1.5; margin: 12px 0; overflow-wrap: anywhere; }
.hotel-map { height: 450px; width: 100%; border-radius: 8px; z-index: 0; background: #e0e5df; }
.map-detail { margin-bottom: 0; padding: 12px; background: white; border-radius: 8px; }
.tile-warning { padding: 12px; background: #fff0d1; color: #674714; }
:deep(.hotel-marker) { display: grid; place-items: center; border: 2px solid #245b50; border-radius: 50%; background: white; color: #17332d; font: bold 16px sans-serif; }
:deep(.hotel-marker.is-selected) { background: #245b50; color: white; box-shadow: 0 0 0 4px white, 0 0 0 6px #245b50; }
:deep(.hotel-marker:focus-visible), :deep(.leaflet-container:focus-visible) { outline: 3px solid #b85b13; outline-offset: 6px; }
:deep(.zip-center) { color: #17332d; font-size: 22px; text-shadow: 0 0 3px white; }
:deep(.leaflet-control-attribution) { background: white; color: #17332d; }
:deep(.leaflet-control-attribution a) { color: #245b50; }
:deep(.leaflet-control-zoom a) { width: 44px; height: 44px; line-height: 44px; }
@media (max-width: 760px) { .map-panel { position: static; } .hotel-map { height: 310px; } }
</style>
