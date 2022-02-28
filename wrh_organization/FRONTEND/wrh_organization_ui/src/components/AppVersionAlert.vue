<style scoped>
.app-version-alert {
  position: fixed;
  top: 0;
  z-index: 99999;
  color: white;
}
</style>

<template>
  <v-alert type="warning" shape dense :icon="icons.mdiAlert" dismissible class="app-version-alert">
    <span class="font-weight-semibold"> Current ui version is old!</span>
    A new version of ui <v-chip label color="primary" small>{{ newVersion }}</v-chip> is available.
    <v-btn color="info" x-small href="javascript:" onclick="location.reload()" class="btn btn-sm btn-info refresh-btn">
      <v-icon>{{icons.mdiRefresh}}</v-icon> Click here
    </v-btn> or refresh page to load new version or data loss will occur.
  </v-alert>
</template>

<script>
import {mdiAlert, mdiRefresh} from '@mdi/js';

export default {
  props: {
    newVersion: {
      type: String,
      default: null
    }
  },
  setup() {
    return {
      icons: {
        mdiAlert,
        mdiRefresh
      }
    }
  }
};
</script>
