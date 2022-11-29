<template>
  <div id="public-org-profile-view">
    <v-row v-if="event.id">
      <v-col
        md="12"
        sm="12"
        cols="12"
      >
        <v-card class="banner">
          <img
            class="white--text align-end banner-img"
            :src="event.prefs.banner_image || require(`@/assets/images/misc/public-banner-bg-light.jpeg`)"
          />
          <v-card-text class="position-relative">
            <v-avatar
              size="60"
              color="white"
              class="avatar-center"
            >
              <v-img :src="event.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
            </v-avatar>
            <!-- Title, Subtitle & Action Button -->
            <div class="d-flex justify-space-between flex-wrap pt-12">
              <div class="me-2 mb-2">
                <h2 class="pt-0 px-0">
                  {{event.name}}
                </h2>
                <h3 class="pt-0 pb-1 px-0 text-caption" v-if="event.organization">
                  {{event._organization.name}}
                </h3>
                <v-card-subtitle class="text-xs pa-0">
                  <v-icon size="15" class="mr-1">{{icons.mdiCalendar}}</v-icon>
                  <span>{{ $utils.formatDate(event.start_date, 'MMM D, YYYY') }}</span>
                  <span v-if="event.end_date"> - {{ $utils.formatDate(event.end_date, 'MMM D, YYYY') }}</span>
                </v-card-subtitle>
                <v-card-subtitle class="text-xs pa-0 pt-1">
                  <v-icon size="15" class="mr-1">{{icons.mdiMapMarker}}</v-icon>
                  <span>{{ event.country || '' }}{{ event.state? `, ${event.state}`:'' }}{{event.city? `, ${event.city}`:'' }}</span>
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
                    {{ icons.mdiBike }}
                  </v-icon>
                </v-avatar>

                <div>
                  <h3 class="text-xl font-weight-medium mb-n1">
                    {{ event.summary.races_count || 0 }}
                  </h3>
                  <span>Races</span>
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
                    {{ icons.mdiBikeFast }}
                  </v-icon>
                </v-avatar>

                <div>
                  <h3 class="text-xl font-weight-medium mb-n1">
                    {{ event.summary.race_series_count || 0 }}
                  </h3>
                  <span>Race Series</span>
                </div>
              </div>

            </div>

            <div class="mt-4">
              <div v-html="event.description"></div>
            </div>
            <div class="d-flex justify-space-between flex-wrap align-center mt-8 pa-0">
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiWeb }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="event.website" target="_blank" v-if="event.website">
                  {{event.website}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiWeb }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="event.registration_website" target="_blank" v-if="event.registration_website">
                  {{event.registration_website}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
              <div>
                <v-icon class="me-1" size="20">
                  {{ icons.mdiEmail }}
                </v-icon>
                <a class="font-weight-medium text-sm me-4 text-decoration-none" :href="`mailto:${event.organizer_email}`" target="_blank" v-if="event.organizer_email">
                  {{event.organizer_email}}
                </a>
                <span v-else class="text-sm me-4">-</span>
              </div>
            </div>

          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <event-races-widget :event="event" class="home-widget"></event-races-widget>
      </v-col>
      <v-col cols="12" md="6">
        <event-race-series-widget :event="event" class="home-widget"></event-race-series-widget>
      </v-col>

    </v-row>
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
  mdiBike,
  mdiBikeFast,
  mdiEmail,
  mdiPhone,
  mdiCalendar,
  mdiMapMarker,
  mdiWeb,
} from '@mdi/js'
import axios from "@/axios";
import {notifyDefaultServerError} from "@/composables/utils";
import useVuetify from '@core/utils/vuetify'
import {onMounted} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationRaceResultsTab from "../dashboard/organizationProfile/OrganizationRaceResultsTab";
import {useRouter} from "@core/utils";
import RecentRaceResultsWidget from "@/views/public/RecentRaceResultsWidget";
import UpcomingEventsWidget from "@/views/public/UpcomingEventsWidget";
import EventRacesWidget from "@/views/public/EventRacesWidget";
import EventRaceSeriesWidget from "@/views/public/EventRaceSeriesWidget";

export default {
  components: {
    EventRaceSeriesWidget,
    EventRacesWidget,
    UpcomingEventsWidget,
    RecentRaceResultsWidget,
    OrganizationRaceResultsTab,
  },
  setup() {
    const { rootThemeClasses } = useVuetify();
    const { route } = useRouter();
    const tab = ref(null);

    const event = ref({});
    const orgId = route.value.params.record_id;
    const loadEvent = () => {
      axios.get(`bycing_org/event/${orgId}`, {params: {exfields: 'summary'}}).then((response) => {
        const e = response.data;
        if (!e.summary) {
          e.summary = {};
        }
        event.value = e;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    onMounted(() => {
      tab.value = route.value.params.tab !== undefined? route.value.params.tab: 0 ;
      loadEvent();
    });

    return {
      rootThemeClasses,
      event,
      loadEvent,
      tab,
      icons: {
        mdiFlagCheckered,
        mdiAccountPlus,
        mdiOfficeBuildingCog,
        mdiAccountMultipleOutline,
        mdiBike,
        mdiBikeFast,
        mdiEmail,
        mdiPhone,
        mdiCalendar,
        mdiMapMarker,
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
    opacity: 0.8;
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
