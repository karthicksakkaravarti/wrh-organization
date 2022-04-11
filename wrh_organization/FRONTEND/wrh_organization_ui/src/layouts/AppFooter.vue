<template>
  <div class="d-flex justify-space-between">
    <span>COPYRIGHT &copy; {{ new Date().getFullYear() }}
      <a href="https://www.weracehere.com" class="text-decoration-none">
        WeRaceHere
      </a>
      <span class="d-none d-md-inline">, All rights Reserved</span>
    </span>
    <div class="align-center d-none d-md-flex">
      <v-chip small label class="ml-1 v-chip-light-bg secondary--text" color="secondary">
        Version: {{$appVersion}}
      </v-chip>
    </div>
  </div>
</template>

<script>
import {mdiHeartOutline} from '@mdi/js'

export default {
  setup() {
    return {
      icons: {
        mdiHeartOutline,
      },
    }
  }
}
</script>

<style scoped>

</style>
