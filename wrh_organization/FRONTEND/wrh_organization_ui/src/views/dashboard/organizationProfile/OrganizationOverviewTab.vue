<template>
  <div class="member-profile-overview-tab">
    <!-- activity timeline -->
    <v-card class="mb-7">
      <v-card-title>
        Organization Activity Timeline
      </v-card-title>

      <v-card-text>
        <v-timeline
          dense
          class="timeline-custom-dense timeline-custom-dots"
        >
          <v-timeline-item
            color="error"
            small
          >
            <div class="d-flex justify-space-between align-center flex-wrap">
              <h4 class="font-weight-medium me-1">
                User login
              </h4>
              <small class="text-no-wrap">12 min ago</small>
            </div>
            <p class="mb-0">
              User login at 2:12pm
            </p>
          </v-timeline-item>

          <v-timeline-item
            color="primary"
            small
          >
            <div class="d-flex justify-space-between align-center flex-wrap">
              <h4 class="font-weight-medium me-1">
                Meeting with john
              </h4>
              <small class="text-no-wrap">45 min ago</small>
            </div>

            <p class="mb-1">
              React Project meeting with john @10:15am
            </p>

          </v-timeline-item>

          <v-timeline-item
            color="info"
            small
          >
            <div class="d-flex justify-space-between align-center flex-wrap">
              <h4 class="font-weight-medium me-1">
                Create a new react project for client
              </h4>
              <small class="text-no-wrap">2 day ago</small>
            </div>
            <p class="mb-0">
              Add files to new design folder
            </p>
          </v-timeline-item>

          <v-timeline-item
            color="success"
            small
          >
            <div class="d-flex justify-space-between align-center flex-wrap">
              <h4 class="font-weight-semibold me-1">
                Create invoices for client
              </h4>
              <small class="text-no-wrap">12 min ago</small>
            </div>
            <p class="mb-0">
              Create new invoices and send to Leona Watkins
            </p>
            <span class="d-flex align-center mt-2">
              <v-icon
                color="error"
                class="me-1"
              >
                {{ icons.mdiFilePdf }}
              </v-icon>
              <span class="text--primary font-weight-semibold text-sm">invoice.pdf</span>
            </span>
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
    </v-card>

  </div>
</template>

<script>
import { mdiDotsVertical, mdiFilePdf } from '@mdi/js'

export default {
  components: { },
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup() {

    return {
      icons: {
        mdiDotsVertical,
        mdiFilePdf,
      },
    }
  },
}
</script>

<style lang="scss" scoped>
</style>
