<template>
  <div class="widget-race-results">
    <race-results-cmp :rider-route="$rns.WIDGET_RIDER_PROFILE"></race-results-cmp>
  </div>
</template>

<script>
import RaceResultsCmp from "@/views/public/RaceResultsCmp";
export default {
  components: {RaceResultsCmp},
  setup() {
    return {
    }
  }
}
</script>
