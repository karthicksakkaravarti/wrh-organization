<template>
  <div id="public-org-profile-view">
    <v-row v-if="organization.id">
      <v-col cols="12" md="4" lg="3">
        <organization-bio-panel :organization="organization" read-only>
        </organization-bio-panel>
      </v-col>

      <v-col cols="12" md="8" lg="9">
        <v-tabs v-model="tab" show-arrows class="public-org-profile-tabs">
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiFlagCheckered }}</v-icon>
            <span>Race Results</span>
          </v-tab>
        </v-tabs>

        <v-tabs-items id="public-org-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <organization-race-results-tab :organization="organization"></organization-race-results-tab>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
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
import OrganizationBioPanel from "../dashboard/organizationProfile/OrganizationBioPanel";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationRaceResultsTab from "../dashboard/organizationProfile/OrganizationRaceResultsTab";
import {useRouter} from "@core/utils";

export default {
  components: {
    OrganizationRaceResultsTab,
    OrganizationBioPanel,
  },
  setup() {
    const { route } = useRouter();
    const tab = ref(null);
    const moreTab = ref({});

    const organization = ref({});
    const loadOrganization = () => {
      axios.get(`bycing_org/public/organization/${route.value.params.record_id}`).then((response) => {
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
#public-org-profile-view {
  .more-btn {
    height: 100% !important;
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
}

</style>
