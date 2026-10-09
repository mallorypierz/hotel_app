<script setup>
defineProps({ hotels: { type: Array, required: true }, intent: { type: Object, default: null } })
const money = (cents) => Number.isSafeInteger(cents) ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100) : 'Not enough data'
</script>

<template>
  <div class="hotel-facts">
    <article
      v-for="hotel in hotels"
      :key="hotel.hotel_id"
      class="hotel-fact"
    >
      <p class="match">
        {{ hotel.eligible ? 'Matching saved hotel' : 'Does not meet all requirements' }}
      </p>
      <h4>{{ hotel.name || 'Name not provided' }}</h4>
      <dl>
        <dt>Stay dates</dt><dd>{{ intent?.check_in }} → {{ intent?.check_out }} (checkout excluded)</dd>
        <dt>Total simulated cost</dt><dd>{{ money(hotel.total_cents) }} for {{ hotel.rooms_requested }} room(s)</dd>
        <dt>Available rooms</dt><dd>{{ hotel.complete ? hotel.min_rooms_available : 'Not verified for every night' }}{{ hotel.complete ? ' minimum each night' : '' }}</dd>
      </dl>
      <p v-if="hotel.missing_dates?.length">
        Missing nightly data: {{ hotel.missing_dates.join(', ') }}. Availability cannot be assumed.
      </p>
      <p v-else-if="!hotel.enough_rooms">
        Not enough rooms on every requested night.
      </p>
      <p v-else-if="!hotel.within_budget">
        Outside the requested budget.
      </p>
    </article>
  </div>
</template>

<style scoped>
.hotel-facts { display: grid; gap: 16px; margin-top: 24px; }
.hotel-fact { padding: 20px; border: 1px solid #cad8d1; border-radius: 14px; background: #f7faf7; overflow-wrap: anywhere; }
h4 { margin: 0 0 8px; font-size: 1.15rem; }
.match { color: #245b50; font-weight: 700; }
dl { margin-bottom: 0; } dt { font-weight: 700; margin-top: 12px; } dd { margin: 4px 0 0; }
</style>
