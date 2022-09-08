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
        <v-btn outlined color="error" :to="{name: $rns.DASHBOARD_HOME, query:{page: 'Register'}}" x-large>
          Sign Up
        </v-btn>
      </v-card-text>
    </v-card>
    <v-row>
      <v-col cols="12" md="6">
        <recent-race-results-widget class="home-widget"></recent-race-results-widget>
      </v-col>
      <v-col cols="12" md="6">
        <next-events-widget class="home-widget"></next-events-widget>
      </v-col>
      <v-col cols="12" md="6">
        <team-orgs-widget class="home-widget"></team-orgs-widget>
      </v-col>
      <v-col cols="12" md="6">
        <twitter-feeds-widget class="home-widget"></twitter-feeds-widget>
      </v-col>
    </v-row>
  </div>
</template>

<script>

import RecentRaceResultsWidget from "@/views/public/RecentRaceResultsWidget";
import NextEventsWidget from "@/views/public/NextEventsWidget";
import TeamOrgsWidget from "@/views/public/TeamOrgsWidget";
import TwitterFeedsWidget from "@/views/public/TwitterFeedsWidget";
export default {
  components: {TwitterFeedsWidget, TeamOrgsWidget, NextEventsWidget, RecentRaceResultsWidget},
  setup() {
    return {
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
    height: 425px;
  }
</style>
