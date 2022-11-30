<style scoped>
</style>

<template>
  <div>
    <v-card flat class="banner d-flex align-center justify-center text-center mb-7" v-if="defaultOrg">
      <img :src="$store.state.sitePrefs.site_ui__banner_image || require(`@/assets/images/misc/public-banner-bg-light.jpeg`)">
      <v-card-text class="pb-0 content-text">
        <p class="kb-title text-2xl font-weight-semibold primary--text mb-2">
          WRH, We Race Here!
        </p>
        <p>
          Manage bycing races, race series for organizations!
        </p>
        <h3 class="mb-5">
          Create Your Account, Select Your Region, Find a Team or Club!
        </h3>
        <div>
          <span class="subtitle-1 font-weight-bold">Step 1, Create a user account: </span>
          <v-btn outlined color="error" :to="{name: $rns.AUTH, query:{page: 'Register'}}" large class="action-btn"
                 :disabled="$store.getters.isAuthenticated">
            Sign Up
            <v-icon right>{{icons.mdiAccount}}</v-icon>
          </v-btn>
        </div>
        <div class="mt-1">
          <span class="subtitle-1 font-weight-bold">Step 2, Join {{defaultOrg.name}}: </span>
          <v-btn outlined color="primary" large class="action-btn"
                 :disabled="!$store.getters.isAuthenticated" @click="$refs.joinDialogRef.show()">
            Join
            <v-icon right>{{icons.mdiAccountPlus}}</v-icon>
          </v-btn>
        </div>
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
    <join-organization-dialog :organization="defaultOrg" ref="joinDialogRef" v-if="defaultOrg"
                              @join-duplicated="navigateToDefaultOrg()"
                              @join-successed="navigateToDefaultOrg()">
    </join-organization-dialog>
  </div>
</template>

<script>

import RecentRaceResultsWidget from "@/views/public/RecentRaceResultsWidget";
import UpcomingEventsWidget from "@/views/public/UpcomingEventsWidget";
import TwitterFeedsWidget from "@/views/public/TwitterFeedsWidget";
import OrganizationsWidget from "@/views/public/OrganizationsWidget";
import {mdiApps, mdiAccount, mdiAccountPlus} from "@mdi/js";
import JoinOrganizationDialog from "@/views/public/JoinOrganizationDialog";
import {onMounted, ref, set} from "@vue/composition-api";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {useRouter} from "@core/utils";
import {routeNames} from "@/router";
export default {
  components: {
    JoinOrganizationDialog,
    OrganizationsWidget, TwitterFeedsWidget, UpcomingEventsWidget, RecentRaceResultsWidget},
  setup() {
    const { router } = useRouter();
    const defaultOrg = ref(null);

    const loadDefaultOrg = () => {
      axios.get(`bycing_org/organization/default_org`).then((response) => {
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

  .banner {
    padding: 3.5rem;
    border: 1px solid #e9e9e9;
  }
  .banner .content-text {
    z-index: 10;
  }
  .banner img {
    position: absolute;
    opacity: 0.25;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .home-widget {
    min-height: 425px;
  }
  .banner .v-btn.action-btn {
    width: 130px;
  }
</style>
