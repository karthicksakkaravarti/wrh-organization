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
          <v-tab class="pl-0 pr-0" v-for="(t, tabIdx) in tabs" :key="t.title">
            <v-menu bottom right :offset-y="true">
              <template v-slot:activator="{ on, attrs, value }">
                <v-btn
                  text
                  class="align-self-center p-0 more-btn"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon size="20" class="mr-1">{{t.icon}}</v-icon>
                  <span>{{t.title}}</span>
                  <v-icon size="20" class="mr-1">{{value? icons.mdiChevronUp: icons.mdiChevronDown}}</v-icon>
                </v-btn>
              </template>

              <v-list class="grey lighten-3">
                <v-list-item v-for="childTab in t.children" :key="childTab.id" @click="tab=tabIdx; selectedTab=childTab" :input-value="childTab.id == selectedTab.id">
                  <v-icon size="20" class="me-3">{{ childTab.icon }}</v-icon> {{childTab.title}}
                </v-list-item>
              </v-list>
            </v-menu>
          </v-tab>
        </v-tabs>

        <v-tabs-items id="organization-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <organization-members-tab v-if="selectedTab.id == 'individual-members'"
                                      :organization="organization"></organization-members-tab>
            <organization-member-orgs-tab v-if="selectedTab.id == 'org-members'"
                                          :organization="organization"></organization-member-orgs-tab>
            <organization-member-fields-tab v-else-if="selectedTab.id == 'member-fields' && organization.my_level.is_admin"
                                            :organization="organization"></organization-member-fields-tab>

          </v-tab-item>
          <v-tab-item>
            <organization-events-tab v-if="selectedTab.id == 'events' && organization.my_level.is_admin"
                                            :organization="organization"></organization-events-tab>
            <organization-races-tab v-else-if="selectedTab.id == 'races'" :organization="organization"></organization-races-tab>
            <organization-race-results-tab v-else-if="selectedTab.id == 'race-results'" :organization="organization"></organization-race-results-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-race-series-tab v-if="selectedTab.id == 'race-series'" :organization="organization"></organization-race-series-tab>
            <organization-race-series-results-tab v-else-if="selectedTab.id == 'race-series-results'" :organization="organization"></organization-race-series-results-tab>
            <organization-race-series-standings-tab v-else-if="selectedTab.id == 'race-series-standings' && organization.my_level.is_admin"
                                            :organization="organization"></organization-race-series-standings-tab>
            <organization-categories-tab v-else-if="selectedTab.id == 'categories' && organization.my_level.is_admin"
                                            :organization="organization"></organization-categories-tab>
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
  mdiCalendar,
  mdiChevronDown,
  mdiChevronUp,
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
import OrganizationEventsTab from "@/views/dashboard/organizationProfile/OrganizationEventsTab";

export default {
  components: {
    OrganizationEventsTab,
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
    const tabs = [
      {
        title: 'Membership',
        icon: mdiAccountMultipleOutline,
        children: [
          {id: 'individual-members', title:  'Individual Members', icon: mdiAccountMultipleOutline},
          {id: 'org-members', title:  'Org Members', icon: mdiHomeGroup},
          {id: 'member-fields', title:  'Member Fields', icon: mdiFormatListText},
        ]
      },
      {
        title: 'Events',
        icon: mdiCalendar,
        children: [
          {id: 'events', title:  'Events', icon: mdiCalendar},
          {id: 'races', title:  'Races', icon: mdiCheckerboard},
          {id: 'race-results', title:  'Race-Results', icon: mdiFlagCheckered},
        ]
      },
      {
        title: 'Race-Series',
        icon: mdiCheckerboard,
        children: [
          {id: 'race-series', title:  'Race-Series', icon: mdiCheckerboard},
          {id: 'race-series-results', title:  'Race-Series Results', icon: mdiFlagCheckered},
          {id: 'race-series-standings', title:  'Race-Series Standings', icon: mdiGold},
          {id: 'categories', title:  'Categories', icon: mdiFamilyTree},
        ]
      },
    ];
    const selectedTab = ref({id: 'individual-members', title:  'Individual Members'});

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
      tabs,
      selectedTab,
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
        mdiCalendar,
        mdiChevronDown,
        mdiChevronUp,
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
