<template>
  <div id="public-org-profile-view">
    <v-row v-if="organization.id">
      <v-col
        md="12"
        sm="12"
        cols="12"
      >
        <v-card class="banner">
          <img
            class="white--text align-end banner-img"
            :src="organization.prefs.banner_image || require(`@/assets/images/misc/public-banner-bg-light.jpeg`)"
          />
          <v-card-text class="position-relative">
            <v-avatar
              size="60"
              color="white"
              class="avatar-center"
            >
              <v-img :src="organization.logo || require('@/assets/images/misc/no-profile.png')"></v-img>
            </v-avatar>
            <!-- Title, Subtitle & Action Button -->
            <div class="d-flex justify-space-between flex-wrap pt-12">
              <div class="me-2 mb-2">
                <h2 class="pt-0 px-0">
                  {{organization.name}}
                  <v-chip
                    label
                    class="ml-1"
                    :color="($const.ORGANIZATION_TYPE_MAP[organization.type] || {}).css"
                    :class="`v-chip-light-bg text-sm font-weight-semibold ${($const.ORGANIZATION_TYPE_MAP[organization.type] || {}).css}--text text-capitalize`"
                  >
                    {{($const.ORGANIZATION_TYPE_MAP[organization.type] || {}).title || organization.type}}
                  </v-chip>

                </h2>
                <v-card-subtitle class="text-xs pa-0">
                  {{ organization.country || '' }}{{ organization.state? `, ${organization.state}`:'' }}{{organization.city? `, ${organization.city}`:'' }}
                </v-card-subtitle>
                <v-card-subtitle class="text-xs pa-0 pt-1" v-if="organization.address">
                  {{ organization.address }}
                </v-card-subtitle>
              </div>
              <div class="d-flex me-8 mb-4">
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
                    {{ icons.mdiAccountMultipleOutline }}
                  </v-icon>
                </v-avatar>

                <div>
                  <h3 class="text-xl font-weight-medium mb-n1">
                    {{ orgSummary.members_count || 0 }}
                  </h3>
                  <span>Members</span>
                </div>
              </div>

              <div class="d-flex mb-4 me-4">
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
                    {{ orgSummary.races_count || 0 }}
                  </h3>
                  <span>Races</span>
                </div>
              </div>

              <v-btn color="primary" v-if="$store.getters.isAuthenticated && (organization.my_level.is_admin || organization.my_level.is_member)"
                     :to="{name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params: {record_id: organization.id}}">
                Manage <v-icon right>{{icons.mdiOfficeBuildingCog}}</v-icon>
              </v-btn>
              <v-tooltip bottom v-else>
                <template #activator="{ on, attrs }">
                  <v-btn color="success" v-on="on" v-bind="attrs" @click="$refs.joinDialogRef.show()">
                    Join <v-icon right>{{icons.mdiAccountPlus}}</v-icon>
                  </v-btn>
                </template>
                <span>Join to Organization</span>
              </v-tooltip>

            </div>

            <div class="mt-4">
              <div v-html="organization.about"></div>
            </div>
            <div class="d-flex justify-space-between flex-wrap align-center mt-8 pa-0">
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiWeb }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="organization.website" target="_blank" v-if="organization.website">
                  {{organization.website}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiEmail }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="`mailto:${organization.email}`" target="_blank" v-if="organization.email">
                  {{organization.email}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiPhone }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="`tel:${organization.phone}`" target="_blank" v-if="organization.phone">
                  {{organization.phone}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
              <div class="v-avatar-group" :class="rootThemeClasses">
                <v-avatar size="40">
                  <v-btn v-if="organization.social_media.youtube" link :href="organization.social_media.youtube">
                    <v-img src="@/assets/images/logos/youtube.png"></v-img>
                  </v-btn>
                  <v-img v-else class="disabled" src="@/assets/images/logos/youtube.png"></v-img>
                </v-avatar>
                <v-avatar size="40">
                  <v-btn v-if="organization.social_media.instagram" link :href="organization.social_media.instagram">
                    <v-img src="@/assets/images/logos/instagram.png"></v-img>
                  </v-btn>
                  <v-img v-else class="disabled" src="@/assets/images/logos/instagram.png"></v-img>
                </v-avatar>
                <v-avatar size="40">
                  <v-btn v-if="organization.social_media.facebook" link :href="organization.social_media.facebook">
                    <v-img src="@/assets/images/logos/facebook.png"></v-img>
                  </v-btn>
                  <v-img v-else class="disabled" src="@/assets/images/logos/facebook.png"></v-img>
                </v-avatar>
              </div>

            </div>

          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <recent-race-results-widget :api-params="{organization: organization.id}" class="home-widget"></recent-race-results-widget>
      </v-col>
      <v-col cols="12" md="6">
        <upcoming-events-widget :api-params="{organization: organization.id}" class="home-widget"></upcoming-events-widget>
      </v-col>
    </v-row>
    <join-organization-dialog :organization="organization"
                              v-if="organization.my_level && !organization.my_level.is_member"
                              ref="joinDialogRef" @join-successed="$router.push({name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params: {record_id: organization.id}})">
    </join-organization-dialog>
  </div>
</template>

<script>
import { ref } from '@vue/composition-api'

// eslint-disable-next-line object-curly-newline
import {
  mdiFlagCheckered,
  mdiAccountPlus,
  mdiOfficeBuildingCog,
  mdiAccountMultipleOutline,
  mdiCalendar,
  mdiEmail,
  mdiPhone,
  mdiWeb,
} from '@mdi/js'
import OrganizationBioPanel from "../dashboard/organizationProfile/OrganizationBioPanel";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import useVuetify from '@core/utils/vuetify'
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationRaceResultsTab from "../dashboard/organizationProfile/OrganizationRaceResultsTab";
import {useRouter} from "@core/utils";
import RecentRaceResultsWidget from "@/views/public/RecentRaceResultsWidget";
import UpcomingEventsWidget from "@/views/public/UpcomingEventsWidget";
import JoinOrganizationDialog from "./JoinOrganizationDialog"

export default {
  components: {
    UpcomingEventsWidget,
    RecentRaceResultsWidget,
    OrganizationRaceResultsTab,
    OrganizationBioPanel,
    JoinOrganizationDialog,
  },
  setup() {
    const { rootThemeClasses } = useVuetify();
    const { route } = useRouter();
    const tab = ref(null);
    const orgSummary = ref({});

    const organization = ref({});
    const orgId = route.value.params.record_id;
    const loadOrganization = () => {
      axios.get(`bycing_org/public/organization/${orgId}`, {params: {exfields: 'my_level'}}).then((response) => {
        const org = response.data;
        if (!org.social_media) {
          org.social_media = {};
        }
        if (!org.my_level) {
          org.my_level = {};
        }
        organization.value = org;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const loadOrgSummary = () => {
      axios.get(`bycing_org/organization/${orgId}/summary`).then((response) => {
        orgSummary.value = response.data;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    onMounted(() => {
      tab.value = route.value.params.tab !== undefined? route.value.params.tab: 0 ;
      loadOrganization();
      loadOrgSummary();
    });

    return {
      rootThemeClasses,
      organization,
      orgSummary,
      loadOrganization,
      tab,
      icons: {
        mdiFlagCheckered,
        mdiAccountPlus,
        mdiOfficeBuildingCog,
        mdiAccountMultipleOutline,
        mdiCalendar,
        mdiEmail,
        mdiPhone,
        mdiWeb,
      }
    }
  },
}
</script>

<style lang="scss">
//@import '@core/preset/preset/apps/user.scss';
@import '@core/preset/preset/mixins.scss';
@import '@core/preset/preset/variables.scss';
@import '@core/preset/preset/mixins.scss';

// user view
#public-org-profile-view {
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
    height: 300px;
    object-fit: cover;
  }

  .public-org-profile-tabs {
    &.v-tabs:not(.v-tabs--vertical) {
      box-shadow: none !important;
      .v-tabs-bar {
        background-color: transparent !important;
      }
    }
  }

  // tab content
  #public-org-profile-tabs-content {
    background-color: transparent;
  }

  // bio panel
  .public-org-profile-bio-panel {
    .user-plan {
      border: 2px solid var(--v-primary-base) !important;
    }
  }
  .v-avatar-group > .v-avatar .v-btn .v-btn__content{
    width: 20px;
  }
  .v-avatar-group > .v-avatar .v-image.disabled {
    opacity: 0.5;
  }
  .v-avatar-group > .v-avatar {
    margin-right: 20px;
  }
}

</style>
