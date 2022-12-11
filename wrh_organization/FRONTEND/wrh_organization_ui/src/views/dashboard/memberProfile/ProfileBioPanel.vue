<template>
  <v-row class="member-profile-bio-panel">
    <!-- user profile -->
    <v-col cols="12">
      <v-card class="pt-10">
        <v-card-title class="justify-center flex-column">
          <v-avatar
            :color="memberData.user && memberData.user.avatar ? '' : 'primary'"
            :class="memberData.user && memberData.user.avatar ? '' : 'v-avatar-light-bg primary--text'"
            size="120"
            rounded
            class="mb-4"
          >
            <v-img
              v-if="memberData.user && memberData.user.avatar"
              :src="memberData.user && memberData.user.avatar"
            ></v-img>
            <span
              v-else
              class="font-weight-semibold text-5xl"
            >{{ avatarText(memberData.first_name) }}</span>
          </v-avatar>

          <span>{{ memberData.first_name }} {{ memberData.last_name }}</span>

        </v-card-title>

        <v-card-text class="d-flex justify-center flex-wrap mt-2 pe-sm-0">
          <div class="d-flex align-center me-8 mb-4">
            <v-avatar
              size="40"
              rounded
              color="primary"
              class="v-avatar-light-bg primary--text me-3"
            >
              <v-icon
                color="primary"
                size="22"
              >
                {{ icons.mdiCalendar }}
              </v-icon>
            </v-avatar>

            <div>
              <h3 class="text-xl font-weight-medium mb-n1">
                {{ (memberData.summary || {}).events_count }}
              </h3>
              <span>Events</span>
            </div>
          </div>

          <div class="d-flex align-center mb-4 me-4">
            <v-avatar
              size="40"
              rounded
              color="primary"
              class="v-avatar-light-bg primary--text me-3"
            >
              <v-icon
                color="primary"
                size="22"
              >
                {{ icons.mdiBike }}
              </v-icon>
            </v-avatar>

            <div>
              <h3 class="text-xl font-weight-medium mb-n1">
                {{ (memberData.summary || {}).race_results_count }}
              </h3>
              <span>Results</span>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="d-flex justify-center social-accounts">
          <v-tooltip bottom v-for="s in $const.SOCIAL_ACCOUNTS" :key="s.name">
            <template #activator="{ on, attrs }">
              <span v-on="on" class="mr-1">
                <v-btn :href="(memberData.social_media || {})[s.name]" :key="s.name" icon class="ms-1" fab x-large
                       target="_blank"
                       v-bind="attrs" :disabled="!(memberData.social_media || {})[s.name]">
                  <v-avatar size="40" rounded>
                    <v-img :src="require(`@/assets/images/logos/${s.img}`)"></v-img>
                  </v-avatar>
                </v-btn>
              </span>
            </template>
            <span>{{s.title}}</span>
          </v-tooltip>
        </v-card-actions>

        <v-card-text>
          <h2 class="text-xl font-weight-semibold mb-2">
            Details
          </h2>

          <v-divider></v-divider>

          <v-list>
            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.email">
              <span class="font-weight-medium text-no-wrap me-2">E-mail:</span>
              <span class="text--secondary">{{ memberData.email }}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.phone">
              <span class="font-weight-medium me-2">Phone:</span>
              <span class="text--secondary">{{ memberData.phone? $utils.formatPhone(memberData.phone): '-' }}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.gender">
              <span class="font-weight-medium me-2">Gender:</span>
              <span class="text--secondary">{{($const.GENDER_MAP[memberData.gender] || {}).title}}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.birth_date">
              <span class="font-weight-medium me-2">Racing Age:</span>
              <span class="text--secondary">
                <template v-if="memberData.age">
                  {{ memberData.age || '-'}} years
                </template>
                <template v-else>-</template>
              </span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.height">
              <span class="font-weight-medium me-2">Height:</span>
              <span class="text--secondary">{{ $utils.removeTrailingZero(memberData.height) || '-' }} m</span>
            </v-list-item>
            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.weight">
              <span class="font-weight-medium me-2">Weight:</span>
              <span class="text--secondary">{{ $utils.removeTrailingZero(memberData.weight) || '-' }} kg</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.country">
              <span class="font-weight-medium me-2">Country:</span>
              <span class="text--secondary">{{($const.COUNTRY_MAP[memberData.country] || {}).name || memberData.country || '-'}}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.state">
              <span class="font-weight-medium me-2">State:</span>
              <span class="text--secondary">{{ memberData.state || '-' }}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.city">
              <span class="font-weight-medium me-2">City:</span>
              <span class="text--secondary">{{ memberData.city || '-' }}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.address1">
              <span class="font-weight-medium me-2">Address 1:</span>
              <span class="text--secondary">{{ memberData.address1 || '-' }}</span>
            </v-list-item>

            <v-list-item dense class="px-0 mb-n2" v-if="!hiddenFields.address1 && memberData.address2">
              <span class="font-weight-medium me-2">Address 2:</span>
              <span class="text--secondary">{{ memberData.address2 }}</span>
            </v-list-item>

          </v-list>
        </v-card-text>
        <v-card-actions class="justify-center">
          <v-btn v-if="!readOnly" color="warning" outlined class="me-3" :to="{name: $rns.DASHBOARD_ACCOUNT_SETTINGS}">
            <v-icon dark left>
              {{ icons.mdiAccountEditOutline }}
            </v-icon>Edit
          </v-btn>
        </v-card-actions>
      </v-card>

    </v-col>

  </v-row>
</template>

<script>
import { mdiBike, mdiCalendar, mdiCheckboxBlankCircle, mdiAccountEditOutline } from '@mdi/js';
import { avatarText } from '@core/utils/filter';

export default {
  props: {
    memberData: {
      type: Object,
      required: true
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    hiddenFields: {
      type: Object,
      default: () => ({})
    }
  },
  components: {
  },
  setup() {
    return {
      avatarText,
      icons: {
        mdiBike,
        mdiCalendar,
        mdiCheckboxBlankCircle,
        mdiAccountEditOutline,
      },
    }
  },
}
</script>

<style scoped>
.social-accounts .v-btn--disabled {
  opacity: 0.3;
}
</style>
