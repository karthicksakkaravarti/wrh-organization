<template>
  <div id="organization-profile-view">
    <v-row v-if="organization.id">
      <v-col cols="12" md="5" lg="4">
        <organization-bio-panel :organization="organization"
                                @edit-click="$refs.editDialogRef.show(organization)">
        </organization-bio-panel>
      </v-col>

      <v-col cols="12" md="7" lg="8">
        <v-tabs v-model="tab" show-arrows class="organization-profile-tabs">
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiHomeAccount }}</v-icon>
            <span>Overview</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiAccountMultipleOutline }}</v-icon>
            <span>Members</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiHomeGroup }}</v-icon>
            <span>Member Orgs</span>
          </v-tab>
          <v-tab v-if="organization.my_level.is_admin">
            <v-icon size="20" class="me-3">{{ icons.mdiFormatListText }}</v-icon>
            <span>Member Fields</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiCalendarMultiple }}</v-icon>
            <span>Events</span>
          </v-tab>
        </v-tabs>

        <v-tabs-items id="organization-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <organization-overview-tab :organization="organization"></organization-overview-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-members-tab :organization="organization"></organization-members-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-member-orgs-tab :organization="organization"></organization-member-orgs-tab>
          </v-tab-item>
          <v-tab-item v-if="organization.my_level.is_admin">
            <organization-member-fields-tab :organization="organization"></organization-member-fields-tab>
          </v-tab-item>
          <v-tab-item>
            <organization-events-tab :organization="organization"></organization-events-tab>
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
  mdiHomeAccount,
  mdiHomeGroup,
  mdiFormatListText,
} from '@mdi/js'
import OrganizationBioPanel from "./OrganizationBioPanel";
import OrganizationOverviewTab from "./OrganizationOverviewTab";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationMembersTab from "./OrganizationMembersTab";
import OrganizationEventsTab from "./OrganizationEventsTab";
import {useRouter} from "@core/utils";
import ProfileOrganizationFormDialog from "@/views/dashboard/memberProfile/ProfileOrganizationFormDialog";
import OrganizationMemberOrgsTab from "./OrganizationMemberOrgsTab";
import OrganizationMemberFieldsTab from "./OrganizationMemberFieldsTab";

export default {
  components: {
    OrganizationMemberFieldsTab,
    OrganizationMemberOrgsTab,
    ProfileOrganizationFormDialog,
    OrganizationEventsTab,
    OrganizationMembersTab,
    OrganizationOverviewTab,
    OrganizationBioPanel,
  },
  setup() {
    const { route } = useRouter();
    const tab = ref(null);

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
      tab.value = route.value.params.tab !== undefined? route.value.params.tab: 1 ;
      loadOrganization();
    });

    return {
      organization,
      loadOrganization,
      tab,
      icons: {
        mdiAccountMultipleOutline,
        mdiCalendarMultiple,
        mdiHomeAccount,
        mdiHomeGroup,
        mdiFormatListText,
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
