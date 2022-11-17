<template>
  <div class="widget-race-results">
    <events-calendar-widget  :api-params="{organization: $route.params.org_id}"></events-calendar-widget>
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
