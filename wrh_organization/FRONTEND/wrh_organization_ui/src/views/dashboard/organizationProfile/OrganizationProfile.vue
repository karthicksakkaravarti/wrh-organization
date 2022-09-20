<template>
  <div id="organization-profile-view">
    <v-row v-if="organization.id">
      <v-col cols="12" md="4" lg="3">
        <organization-bio-panel :organization="organization"
                                @edit-click="$refs.editDialogRef.show(organization)">
        </organization-bio-panel>
      </v-col>

      <v-col cols="12" md="8" lg="9">
        <v-tabs v-model="tab" show-arrows class="organization-profile-tabs">
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiAccountMultipleOutline }}</v-icon>
            <span>Members</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiHomeGroup }}</v-icon>
            <span>Member Orgs</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiFlagCheckered }}</v-icon>
            <span>Race Results</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiFlagCheckered }}</v-icon>
            <span>Race-Series Results</span>
          </v-tab>
          <v-tab class="pl-0 pr-0">
            <v-menu bottom left>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  text
                  class="align-self-center p-0 more-btn"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon size="20" class="mr-1">{{icons.mdiMenu}}</v-icon>
                  More
                </v-btn>
              </template>

              <v-list class="grey lighten-3">
                <v-list-item @click="tab=4; moreTab={id: 'races', name: 'Races'}">
                  <v-icon size="20" class="me-3">{{ icons.mdiCheckerboard }}</v-icon> Races
                </v-list-item>
                <v-list-item @click="tab=4; moreTab={id: 'race-series', name: 'Race-Series'}">
                  <v-icon size="20" class="me-3">{{ icons.mdiCheckerboard }}</v-icon> Race-Series
                </v-list-item>
                <v-list-item @click="tab=4; moreTab={id: 'race-series-standings', name: 'Race-Series Standings'}" v-if="organization.my_level.is_admin">
                  <v-icon size="20" class="me-3">{{ icons.mdiGold }}</v-icon> Race-Series Standings
                </v-list-item>
                <v-list-item @click="tab=4; moreTab={id: 'categories', name: 'Categories'}" v-if="organization.my_level.is_admin">
                  <v-icon size="20" class="me-3">{{ icons.mdiFamilyTree }}</v-icon> Categories
                </v-list-item>
                <v-list-item @click="tab=4; moreTab={id: 'member-fields', name: 'Member Fields'}" v-if="organization.my_level.is_admin">
                  <v-icon size="20" class="me-3">{{ icons.mdiFormatListText }}</v-icon> Member Fields
                </v-list-item>
              </v-list>
            </v-menu>

          </v-tab>
        </v-tabs>

        <v-tabs-items id="organization-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <organization-members-tab :organization="organization"></organization-members-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-member-orgs-tab :organization="organization"></organization-member-orgs-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-race-results-tab :organization="organization"></organization-race-results-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-race-series-results-tab :organization="organization"></organization-race-series-results-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-races-tab v-if="!moreTab.id || moreTab.id == 'races'" :organization="organization"></organization-races-tab>
            <organization-race-series-tab v-else-if="moreTab.id == 'race-series'" :organization="organization"></organization-race-series-tab>
            <organization-member-fields-tab v-else-if="moreTab.id == 'member-fields' && organization.my_level.is_admin"
                                            :organization="organization"></organization-member-fields-tab>
            <organization-race-series-standings-tab v-else-if="moreTab.id == 'race-series-standings' && organization.my_level.is_admin"
                                            :organization="organization"></organization-race-series-standings-tab>
            <organization-categories-tab v-else-if="moreTab.id == 'categories' && organization.my_level.is_admin"
                                            :organization="organization"></organization-categories-tab>
          </v-tab-item>
          <v-tab-item>
          </v-tab-item>
          <v-tab-item v-if="organization.my_level.is_admin">
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
    <profile-organization-form-dialog ref="editDialogRef"
                                      @save-successed="loadOrganization()">
    </profile-organization-form-dialog>
  </div>
</template>

<script>
import { ref } from '@vue/composition-api'

// eslint-disable-next-line object-curly-newline
import {
  mdiAccountMultipleOutline,
  mdiCalendarMultiple,
  mdiCheckerboard,
  mdiGold,
  mdiHomeGroup,
  mdiFormatListText,
  mdiFlagCheckered,
  mdiMenu,
  mdiFamilyTree,
} from '@mdi/js'
import OrganizationBioPanel from "./OrganizationBioPanel";
import OrganizationRacesTab from "./OrganizationRacesTab";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationMembersTab from "./OrganizationMembersTab";
import OrganizationRaceResultsTab from "./OrganizationRaceResultsTab";
import {useRouter} from "@core/utils";
import ProfileOrganizationFormDialog from "@/views/dashboard/memberProfile/ProfileOrganizationFormDialog";
import OrganizationMemberOrgsTab from "./OrganizationMemberOrgsTab";
import OrganizationMemberFieldsTab from "./OrganizationMemberFieldsTab";
import OrganizationRaceSeriesTab from "./OrganizationRaceSeriesTab";
import OrganizationRaceSeriesResultsTab from "./OrganizationRaceSeriesResultsTab";
import OrganizationRaceSeriesStandingsTab from "./OrganizationRaceSeriesStandingsTab";
import OrganizationCategoriesTab from "@/views/dashboard/organizationProfile/OrganizationCategoriesTab";

export default {
  components: {
    OrganizationCategoriesTab,
    OrganizationRaceSeriesResultsTab,
    OrganizationRaceSeriesStandingsTab,
    OrganizationRaceSeriesTab,
    OrganizationMemberFieldsTab,
    OrganizationMemberOrgsTab,
    ProfileOrganizationFormDialog,
    OrganizationRaceResultsTab,
    OrganizationMembersTab,
    OrganizationRacesTab,
    OrganizationBioPanel,
  },
  setup() {
    const { route } = useRouter();
    const tab = ref(null);
    const moreTab = ref({});

    const organization = ref({my_level: {}});
    const loadOrganization = () => {
      var params = {exfields: 'my_level'};
      axios.get(`bycing_org/organization/${route.value.params.record_id}`, {params: params}).then((response) => {
        organization.value = response.data;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    onMounted(() => {
      tab.value = route.value.params.tab !== undefined? route.value.params.tab: 0 ;
      loadOrganization();
    });

    return {
      organization,
      loadOrganization,
      tab,
      moreTab,
      icons: {
        mdiAccountMultipleOutline,
        mdiCalendarMultiple,
        mdiCheckerboard,
        mdiGold,
        mdiHomeGroup,
        mdiFormatListText,
        mdiFlagCheckered,
        mdiMenu,
        mdiFamilyTree,
      }
    }
  },
}
</script>

<style lang="scss">
//@import '@core/preset/preset/apps/user.scss';
@import '@core/preset/preset/mixins.scss';
@import '@core/preset/preset/variables.scss';

// user view
#organization-profile-view {
  .more-btn {
    height: 100% !important;
  }
  .organization-profile-tabs {
    &.v-tabs:not(.v-tabs--vertical) {
      box-shadow: none !important;
      .v-tabs-bar {
        background-color: transparent !important;
      }
    }
  }

  // tab content
  #organization-profile-tabs-content {
    background-color: transparent;
  }

  // bio panel
  .organization-profile-bio-panel {
    .user-plan {
      border: 2px solid var(--v-primary-base) !important;
    }
  }
}

</style>
