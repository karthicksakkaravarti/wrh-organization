<template>
  <v-card id="account-setting-card">
    <!-- tabs -->
    <v-tabs v-model="tab" show-arrows>
      <v-tab v-for="tab in tabs" :key="tab.title">
        <v-icon size="20" class="me-3">
          {{ tab.icon }}
        </v-icon>
        <span>{{ tab.title }}</span>
      </v-tab>
    </v-tabs>

    <!-- tabs item -->
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <account-settings-member></account-settings-member>
      </v-tab-item>
      <v-tab-item>
        <account-settings-security></account-settings-security>
      </v-tab-item>
      <v-tab-item>
        <account-settings-notification></account-settings-notification>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
import {
  mdiAccountOutline,
  mdiLockOpenOutline,
  mdiInformationOutline,
  mdiBookmarkOutline,
  mdiBellOutline,
  mdiBike
} from '@mdi/js'
import { ref } from '@vue/composition-api'

// demos
import AccountSettingsMember from './AccountSettingsMember'
import AccountSettingsSecurity from './AccountSettingsSecurity'
import AccountSettingsNotification from './AccountSettingsNotification'

export default {
  components: {
    AccountSettingsMember,
    AccountSettingsSecurity,
    AccountSettingsNotification,
  },
  setup() {
    const tab = ref('');

    // tabs
    const tabs = [
      { title: 'Member Account', icon: mdiAccountOutline },
      { title: 'Security', icon: mdiLockOpenOutline },
      { title: 'Notifications', icon: mdiBellOutline },
    ];

    return {
      tab,
      tabs,
      icons: {
        mdiAccountOutline,
        mdiLockOpenOutline,
        mdiInformationOutline,
        mdiBookmarkOutline,
        mdiBellOutline,
        mdiBike
      },
    }
  },
}
</script>
