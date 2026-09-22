<script setup>
defineEmits(['book'])
defineProps({
  hotels: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <p class="table-hint">
    Scroll the table sideways on smaller screens to see all columns and select a stay.
  </p>
  <div
    class="table-wrap"
    role="region"
    aria-label="Available stays; scroll horizontally for booking actions"
    tabindex="0"
  >
    <table>
      <thead>
        <tr>
          <th scope="col">
            Hotel
          </th>
          <th scope="col">
            City
          </th>
          <th scope="col">
            State
          </th>
          <th scope="col">
            Nightly rate
          </th>
          <th scope="col">
            Trip
          </th>
          <th scope="col">
            Check in
          </th>
          <th scope="col">
            Check out
          </th>
          <th scope="col">
            Book a stay
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="hotel in hotels"
          :key="hotel.trip_id"
        >
          <th scope="row">
            {{ hotel.name }}
          </th>
          <td>{{ hotel.city }}</td>
          <td>{{ hotel.state }}</td>
          <td>${{ hotel.nightly_price.toFixed(0) }}</td>
          <td>{{ hotel.trip_name }}</td>
          <td>{{ hotel.check_in }}</td>
          <td>{{ hotel.check_out }}</td>
          <td>
            <button
              type="button"
              @click="$emit('book', hotel)"
            >
              Select stay
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
