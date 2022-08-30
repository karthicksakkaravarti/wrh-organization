<template>
  <div id="rider-profile-view">
    <v-row v-if="memberData.id">
      <v-col cols="12" md="5" lg="4">
        <profile-bio-panel :member-data="memberData" read-only></profile-bio-panel>
      </v-col>

      <v-col cols="12" md="7" lg="8">
        <v-tabs v-model="tab" show-arrows class="rider-profile-tabs">
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiAccountOutline }}</v-icon>
            <span>Overview</span>
          </v-tab>
          <v-tab>
            <v-icon size="20" class="me-3">{{ icons.mdiFlagCheckered }}</v-icon>
            <span>Race Results</span>
          </v-tab>
        </v-tabs>

        <v-tabs-items id="rider-profile-tabs-content" v-model="tab" class="mt-5 pa-1">
          <v-tab-item>
            <profile-overview-tab></profile-overview-tab>
          </v-tab-item>
          <v-tab-item>
            <rider-race-results-tab :rider-id="$route.params.record_id"></rider-race-results-tab>
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
import ProfileBioPanel from "../dashboard/memberProfile/ProfileBioPanel";
import ProfileOverviewTab from "../dashboard/memberProfile/ProfileOverviewTab";
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import ProfileOrganizationsTab from "@/views/dashboard/memberProfile/ProfileOrganizationsTab";
import {useRouter} from "@core/utils";
import RiderRaceResultsTab from "@/views/public/RiderRaceResultsTab";

export default {
  components: {
    RiderRaceResultsTab,
    ProfileOrganizationsTab,
    ProfileOverviewTab,
    ProfileBioPanel,
  },
  setup() {
    const { route } = useRouter();
    const tab = ref(null);

    const memberData = ref({user: {}});

    const loadMemberData = () => {
      axios.get(`bycing_org/public/member/${route.value.params.record_id}`, {params: {exfields: 'summary'}}).then((response) => {
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
#rider-profile-view {
  .rider-profile-tabs {
    &.v-tabs:not(.v-tabs--vertical) {
      box-shadow: none !important;
      .v-tabs-bar {
        background-color: transparent !important;
      }
    }
  }

  // tab content
  #rider-profile-tabs-content {
    background-color: transparent;
  }

  // bio panel
  .rider-profile-bio-panel {
    .user-plan {
      border: 2px solid var(--v-primary-base) !important;
    }
  }
}

</style>
