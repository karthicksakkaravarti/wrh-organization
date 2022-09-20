<style scoped>
</style>

<template>
  <div>
    <v-card flat class="banner d-flex align-center justify-center text-center mb-7">
      <img :src="require(`@/assets/images/misc/public-banner-bg-light.jpeg`)">
      <v-card-text class="pb-0">
        <p class="kb-title text-2xl font-weight-semibold primary--text mb-2">
          WRH, We Race Here!
        </p>
        <p>
          Manage bycing races, race series for organizations!
        </p>
        <h3 class="mb-5">
          Create Your Account, Select Your Region, Find a Team or Club!
        </h3>
        <v-btn v-if="!$store.getters.isAuthenticated" outlined color="error" :to="{name: $rns.AUTH, query:{page: 'Register'}}" x-large>
          Sign Up
        </v-btn>
        <v-btn v-else outlined color="info" :to="{name: $rns.DASHBOARD_HOME}" x-large>
          <v-icon>
            {{icons.mdiApps}}
          </v-icon>
          Go to Panel
        </v-btn>
      </v-card-text>
    </v-card>
    <v-row>
      <v-col cols="12" md="6">
        <recent-race-results-widget class="home-widget"></recent-race-results-widget>
      </v-col>
      <v-col cols="12" md="6">
        <upcoming-events-widget class="home-widget"></upcoming-events-widget>
      </v-col>
      <v-col cols="12" md="6">
        <organizations-widget class="home-widget"></organizations-widget>
      </v-col>
      <v-col cols="12" md="6">
        <twitter-feeds-widget class="home-widget"></twitter-feeds-widget>
      </v-col>
    </v-row>
  </div>
</template>

<script>

import RecentRaceResultsWidget from "@/views/public/RecentRaceResultsWidget";
import UpcomingEventsWidget from "@/views/public/UpcomingEventsWidget";
import TwitterFeedsWidget from "@/views/public/TwitterFeedsWidget";
import OrganizationsWidget from "@/views/public/OrganizationsWidget";
import {mdiApps} from "@mdi/js";
export default {
  components: {OrganizationsWidget, TwitterFeedsWidget, UpcomingEventsWidget, RecentRaceResultsWidget},
  setup() {
    return {
      icons: {
        mdiApps
      }
    }
  },
}
</script>

<style lang="scss" scoped>
  .banner {
    padding: 3.5rem;
    border: 1px solid #e9e9e9;
  }
  .banner img {
    position: absolute;
    opacity: 0.15;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .home-widget {
    min-height: 425px;
  }
</style>
