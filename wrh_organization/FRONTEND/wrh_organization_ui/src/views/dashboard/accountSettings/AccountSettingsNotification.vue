<template>
  <v-card
    flat
    class="pa-3"
  >
    <v-card-title>
      <v-icon
        size="26"
        class="text--primary me-3"
      >
        {{ icons.mdiChartTimelineVariant }}
      </v-icon>
      <span>Activity</span>
    </v-card-title>

    <!-- Activity -->
    <v-card-text>
      <v-switch
        v-model="notificationsData.email_on_new_upcoming_event"
        hide-details
        class="mt-0"
      >
        <template #label>
          <span class="text-sm ms-2">Email me when new upcoming event</span>
        </template>
      </v-switch>

      <v-switch
        v-model="notificationsData.email_on_joined_organization"
        hide-details
        class="mt-3"
      >
        <template #label>
          <span class="text-sm ms-2">Email me when I joined to an organization</span>
        </template>
      </v-switch>

      <v-switch
        v-model="notificationsData.followMe"
        hide-details
        class="mt-3"
      >
        <template #label>
          <span class="text-sm ms-2">Email me when someone follows me</span>
        </template>
      </v-switch>
    </v-card-text>

    <v-card-title class="mt-2">
      <v-icon
        size="26"
        class="text--primary me-3"
      >
        {{ icons.mdiEmailOutline }}
      </v-icon>
      <span>Application</span>
    </v-card-title>

    <!-- Application -->
    <v-card-text>
      <v-switch
        v-model="notificationsData.newsAnnouncements"
        hide-details
        class="mt-0"
      >
        <template #label>
          <span class="text-sm ms-2">News and announcements</span>
        </template>
      </v-switch>

      <v-switch
        v-model="notificationsData.productUpdates"
        hide-details
        class="mt-3"
      >
        <template #label>
          <span class="text-sm ms-2">Weekly product updates</span>
        </template>
      </v-switch>

      <v-switch
        v-model="notificationsData.blogDigest"
        hide-details
        class="mt-3"
      >
        <template #label>
          <span class="text-sm ms-2">Weekly blog digest</span>
        </template>
      </v-switch>
    </v-card-text>

    <v-card-text>
      <v-btn
        color="primary"
        class="me-3 mt-5"
      >
        Save changes
      </v-btn>
      <v-btn
        color="secondary"
        outlined
        class="mt-5"
      >
        Cancel
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiChartTimelineVariant, mdiEmailOutline } from '@mdi/js'
import { ref } from '@vue/composition-api'

export default {
  setup(props) {
    const notificationsData = ref({});

    return {
      notificationsData,
      icons: { mdiChartTimelineVariant, mdiEmailOutline },
    }
  },
}
</script>
