<template>
  <div id="member-profile-view">
    <v-row>
      <v-col cols="12" md="5" lg="4">
        <profile-bio-panel :member-data="memberData"></profile-bio-panel>
      </v-col>

      <v-col cols="12" md="7" lg="8">
        <v-tabs v-model="tab" show-arrows class="member-profile-tabs">
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiAccountOutline }}</v-icon>
            <span>Overview</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiHomeAccount }}</v-icon>
            <span>My Organizations</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiFlagCheckered }}</v-icon>
            <span>My Results</span>
          </v-tab>
        </v-tabs>

        <v-tabs-items id="member-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <profile-overview-tab></profile-overview-tab>
          </v-tab-item>
          <v-tab-item>
            <profile-organizations-tab></profile-organizations-tab>
          </v-tab-item>
          <v-tab-item>
            <profile-my-race-results-tab></profile-my-race-results-tab>
          </v-tab-item>

        </v-tabs-items>
      </v-col>
    </v-row>

  </div>
</template>

<script>
import { ref } from '@vue/composition-api'

// eslint-disable-next-line object-curly-newline
import { mdiAccountOutline, mdiFlagCheckered, mdiHomeAccount } from '@mdi/js'
import ProfileBioPanel from "./ProfileBioPanel";
import ProfileOverviewTab from "./ProfileOverviewTab";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import ProfileOrganizationsTab from "@/views/dashboard/memberProfile/ProfileOrganizationsTab";
import ProfileMyRaceResultsTab from "@/views/dashboard/memberProfile/ProfileMyRaceResultsTab";
import {useRouter} from "@core/utils";

export default {
  components: {
    ProfileMyRaceResultsTab,
    ProfileOrganizationsTab,
    ProfileOverviewTab,
    ProfileBioPanel,
  },
  setup() {
    const { route } = useRouter();
    const tab = ref(null);

    const memberData = ref({user: {}});

    const loadMemberData = () => {
      axios.get("bycing_org/member/me", {params: {exfields: 'summary'}}).then((response) => {
        memberData.value = response.data;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    onMounted(() => {
      tab.value = route.value.params.tab !== undefined? route.value.params.tab: 1 ;
      loadMemberData();
    });

    return {
      memberData,
      loadMemberData,
      tab,
      icons: {
        mdiAccountOutline,
        mdiHomeAccount,
        mdiFlagCheckered,
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
#member-profile-view {
  .member-profile-tabs {
    &.v-tabs:not(.v-tabs--vertical) {
      box-shadow: none !important;
      .v-tabs-bar {
        background-color: transparent !important;
      }
    }
  }

  // tab content
  #member-profile-tabs-content {
    background-color: transparent;
  }

  // bio panel
  .member-profile-bio-panel {
    .user-plan {
      border: 2px solid var(--v-primary-base) !important;
    }
  }
}

</style>
