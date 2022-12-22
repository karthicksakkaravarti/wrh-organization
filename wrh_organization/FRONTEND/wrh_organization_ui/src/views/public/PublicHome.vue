<style scoped>
</style>

<template>
  <div class="public-home">
    <v-card class="banner mb-4" v-if="defaultOrg">
      <img class="white--text align-end banner-img"
          :src="$store.state.sitePrefs.site_ui__banner_image || require(`@/assets/images/misc/public-banner-bg-light.jpeg`)">
      <v-card-text class="position-relative">
        <v-avatar
          size="60"
          color="white"
          class="avatar-center"
        >
          <v-img :src="appLogo"></v-img>
        </v-avatar>
        <div class="text-center pt-6">
            <p class="text-3xl font-weight-semibold primary--text mb-2">
              {{appName}}
            </p>
          <div>
            <v-btn outlined color="primary" :to="{name: $rns.AUTH, query:{page: 'Register'}}" class="action-btn ma-1"
                   :disabled="$store.getters.isAuthenticated">
              Create a user account
              <v-icon right>{{icons.mdiAccount}}</v-icon>
            </v-btn>
            <v-btn outlined color="success" class="action-btn ma-1"
                   :to="{name: $rns.PUBLIC_SIGNUP_AND_JOIN_ORG, params:{record_id: defaultOrg.id}}">
              Join {{defaultOrg.name}}
              <v-icon right>{{icons.mdiAccountPlus}}</v-icon>
            </v-btn>

          </div>
          <div class="mt-1">
          </div>
        </div>
      </v-card-text>
    </v-card>
    <v-row>
      <v-col cols="12" v-if="$store.state.sitePrefs.site_ui__home_information_board">
        <v-card class="d-flex">
          <v-card-text v-html="$store.state.sitePrefs.site_ui__home_information_board" class="ck-content"></v-card-text>
        </v-card>
      </v-col>
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
import {mdiApps, mdiAccount, mdiAccountPlus} from "@mdi/js";
import {onMounted, ref, set} from "@vue/composition-api";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {useRouter} from "@core/utils";
import {routeNames} from "@/router";
import themeConfig from '@themeConfig'

export default {
  components: {
    OrganizationsWidget, TwitterFeedsWidget, UpcomingEventsWidget, RecentRaceResultsWidget},
  setup() {
    const { router } = useRouter();
    const defaultOrg = ref(null);

    const loadDefaultOrg = () => {
      axios.get(`cycling_org/organization/default_org`).then((response) => {
        defaultOrg.value = response.data;
      }, (error) => {
        notifyDefaultServerError(error, true);
      });
    };

    const navigateToDefaultOrg = () => {
      router.push({name: routeNames.DASHBOARD_ORGANIZATION_PROFILE, params: {record_id: defaultOrg.value.id}})
    };

    onMounted(() => {
      loadDefaultOrg();
    });

    return {
      defaultOrg,
      navigateToDefaultOrg,
      appLogo: themeConfig.app.logo,
      appName: themeConfig.app.name,
      appShortName: themeConfig.app.shortName,
      icons: {
        mdiApps,
        mdiAccount,
        mdiAccountPlus
      }
    }
  },
}
</script>

<style lang="scss" scoped>
.public-home {
  .avatar-center {
    top: -2rem;
    left: 1rem;
    border: 3px solid white;
    position: absolute;
  }
  .banner-img {
    left: 0;
    top: 0;
    width: 100%;
    //height: 300px;
    object-fit: cover;
  }
  .home-widget {
    min-height: 425px;
  }
  .banner .v-btn.action-btn {
    width: 230px;
  }
}

</style>
