<template>
  <div class="widget-race-results">
    <events-calendar-widget></events-calendar-widget>
  </div>
</template>

<script>
import EventsCalendarWidget from "@/views/public/EventsCalendarWidget";
export default {
  components: {EventsCalendarWidget},
  setup() {
    return {
    }
  }
}
</script>
