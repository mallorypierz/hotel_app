<script setup>
defineProps({
  hotels: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <div class="table-wrap">
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
        </tr>
      </tbody>
    </table>
  </div>
</template>
