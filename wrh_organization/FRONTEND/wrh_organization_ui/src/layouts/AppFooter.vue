<template>
  <div class="d-flex justify-space-between">
    <span>COPYRIGHT &copy; {{ new Date().getFullYear() }}
      <a href="https://www.weracehere.org" class="text-decoration-none" target="_blank">
        WeRaceHere
      </a>
      <span class="d-none d-md-inline">, All rights Reserved</span>
    </span>
    <div class="align-center d-none d-md-flex">
      <v-chip small label class="ml-1 v-chip-light-bg secondary--text" color="secondary">
        Version: {{$appVersion}}
      </v-chip>
      <span class="pl-1 pr-1">|</span>
      <a href="javascript:" class="text-decoration-none" @click="$refs.termsOfServiceDialogRef.show()">
        Terms Of Service
      </a>
    </div>
    <terms-of-service-dialog ref="termsOfServiceDialogRef"></terms-of-service-dialog>
  </div>
</template>

<script>
import {mdiHeartOutline} from '@mdi/js'
import TermsOfServiceDialog from "@/views/public/TermsOfServiceDialog.vue";

export default {
  components: {TermsOfServiceDialog},
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
