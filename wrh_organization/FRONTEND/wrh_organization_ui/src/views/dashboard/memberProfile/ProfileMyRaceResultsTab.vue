<template>
  <div class="profile-my-race-results-tab">
    <race-results-cmp :api-params="{my: true}"></race-results-cmp>
  </div>
</template>

<script>
import RaceResultsCmp from "@/views/public/RaceResultsCmp";
export default {
  components: {RaceResultsCmp},
  props: {
  },
  setup(props, context) {
    return {
    }
  }
}
</script>

<style lang="scss">
.profile-my-race-results-tab {
  td.race-td {
    max-width: 250px;
  }
}
</style>
