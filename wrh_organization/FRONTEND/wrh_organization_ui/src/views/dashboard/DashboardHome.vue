<style scoped>
</style>

<template>
  <v-card>
    <v-card-title>Dashboard Home Page!</v-card-title>
    <v-card-text>
      This is not implemented yet.
      <a is="router-link" :to="{name: $rns.DASHBOARD_MEMBER_PROFILE}" class="text-decoration-none font-weight-bold">
        <v-icon color="primary">{{icons.mdiAccountOutline}}</v-icon> Go to Profile
      </a>
    </v-card-text>
  </v-card>
</template>

<script>
import {mdiAccountOutline} from "@mdi/js"

export default {
  setup() {
    return {
      icons: {
        mdiAccountOutline,
      }
    }
  }
}
</script>
