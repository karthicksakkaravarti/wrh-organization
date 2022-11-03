<style scoped>
</style>

<template>
  <v-card>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="4" sm="6">
          <v-autocomplete
              v-model="selectedEvent"
              dense
              label="Filter by Event"
              :items="events"
              item-text="name"
              item-value="id"
              hide-details
              :search-input.sync="eventSearchInput"
              :loading="findingEvents"
              no-data-text="No Result Found! Type here to Search event"
              :menu-props="{contentClass:'list-style'}"
              return-object
              clearable
          >
            <template #selection="data">
              <span class="d-block font-weight-medium text-truncate">
                {{ data.item.name }}
              </span>
            </template>
            <template #item="data">
              <v-list-item-content>
                <v-list-item-title class="text-sm">
                  {{ data.item.name }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ $utils.formatDate(data.item.start_date, 'MMM D, YYYY') }} - {{ $utils.formatDate(data.item.end_date, 'MMM D, YYYY') }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="12" md="4" sm="6">
          <v-autocomplete
              :disabled="!selectedEvent"
              v-model="selectedRace"
              dense
              label="Filter by Race"
              :items="races"
              item-text="name"
              item-value="id"
              :menu-props="{contentClass:'list-style'}"
              :loading="loadingRaces"
              no-data-text="No Race Found!"
              hide-details
              clearable
              return-object
          >
            <template #item="data">
              <v-list-item-content>
                <v-list-item-title class="text-sm">
                  {{ data.item.name }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ $utils.formatDate(data.item.start_datetime) }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="12" md="4" sm="6">
          <v-autocomplete
              v-model="tableFiltering.organization"
              dense
              label="Filter by Organization"
              :items="organizations"
              item-text="name"
              item-value="id"
              :menu-props="{contentClass:'list-style'}"
              :loading="loadingOrganizations"
              no-data-text="No Organization Found!"
              hide-details
              clearable
              return-object
          >
            <template #item="data">
              <v-list-item-content>
                <v-list-item-title class="text-sm">
                  {{ data.item.name }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ ($const.ORGANIZATION_TYPE_MAP[data.item.type] || {}).title || data.item.type }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="12" md="4" sm="6">
          <div class="d-flex align-center">
            <v-text-field
                :value="tableFiltering.search"
                @change="value => $set(tableFiltering, 'search', value)"
                @click:clear="$set(tableFiltering, 'search', null)"
                dense clearable hide-details
                placeholder="Search ..." class="me-3 search-input"
            ></v-text-field>
          </div>

        </v-col>
        <v-col cols="12" md="4" sm="6">
          <v-checkbox v-model="tableFiltering.include_dns_dnf" hide-details label="Include DNS/DNF?" class="mt-0"></v-checkbox>
        </v-col>
      </v-row>
    </v-card-text>

    <v-data-table
      :headers="tableColumns"
      :items="records"
      :options.sync="tableOptions"
      @update:options="loadRecords()"
      :server-items-length="pagination.total"
      :loading="loading"
      class="text-no-wrap"
      :footer-props="{'items-per-page-options': $const.DEFAULT_TABLE_PER_PAGE_OPTIONS, 'show-current-page': true, 'show-first-last-page': true}"
    >
      <template #item.rider="{item}">
        <div class="d-flex align-center">
          <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
            <v-img v-if="item._rider && item._rider._user.avatar" :src="item._rider._user.avatar"></v-img>
            <span v-else class="font-weight-medium">
              {{ avatarText(item._rider? item._rider.first_name: (item.more_data.first_name || 'N/A')) }}
            </span>
          </v-avatar>

          <div class="d-flex flex-column pl-1">
            <a v-if="item.rider" is="router-link" :to="getRiderRoute(item.rider)" class="font-weight-semibold text-truncate text-decoration-none">
              <v-icon v-if="item._rider" small>{{icons.mdiAccountCheck}}</v-icon> {{ displayRiderName(item) }}
            </a>
            <span v-else class="font-weight-semibold text-truncate text-decoration-none">
              {{ displayRiderName(item) }}
            </span>
          </div>
        </div>
      </template>

      <template #item.race="{item}">
        <div class="d-flex flex-column">
          <span class="font-weight-semibold text-truncate">
            {{item._race.name}}
          </span>
          <span class="text-xs text-truncate">
            {{item._race._event.name}}
          </span>
        </div>
      </template>
      <template #item.create_datetime="{item}">
        <span class="pr-1">{{$utils.formatDate(item.create_datetime, 'M/D/YY')}}</span>
        <span class="text-caption">{{$utils.formatDate(item.create_datetime, 'HH:mm')}}</span>
      </template>

      <template #item.place="{item}">
        <template v-if="item.finish_status == 'ok'">
          <span class="font-weight-semibold">{{item.place || 'N/A'}}</span>
          <v-icon size="20" color="warning" v-if="item.place == 1" class="ml-1">{{ icons.mdiPodiumGold }}</v-icon>
        </template>
        <v-chip v-else outlined :color="($const.RACE_FINISH_STATUS_MAP[item.finish_status] || {}).css" small>
          {{($const.RACE_FINISH_STATUS_MAP[item.finish_status] || {}).title || item.finish_status}}
        </v-chip>
      </template>

      <!-- actions -->
      <template #item.actions="{item}">
        <div class="d-flex align-end justify-end">
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn icon small v-bind="attrs" v-on="on" @click="$refs.formDialogRef.show(item)">
                <v-icon size="18">
                  {{ icons.mdiPencilOutline }}
                </v-icon>
              </v-btn>
            </template>
            <span>Edit</span>
          </v-tooltip>
        </div>
      </template>

    </v-data-table>
  </v-card>
</template>

<script>
import {
  mdiPencilOutline,
  mdiEyeOutline,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiClose,
  mdiCheck,
  mdiInformationOutline,
  mdiRefresh,
  mdiAccountCheck,
  mdiFileExcelOutline,
  mdiPodiumGold,
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import _ from "lodash";
import {useRouter} from "@core/utils";
import {routeNames} from "@/router";

export default {
  components: {},
  props: {
    apiParams: {
      type: Object,
      required: false
    },
    hiddenColumns: {
      type: Array,
      required: false
    },
    riderRoute: {
      type: String,
      default: routeNames.PUBLIC_RIDER_PROFILE
    }
  },
  setup(props, context) {
    const { route } = useRouter();
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const loadingRaces = ref(false);
    const loadingOrganizations = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref(route.value.query || {});
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'RIDER', value: 'rider'},
      {text: 'RACE', value: 'race', cellClass: 'race-td'},
      {text: 'PLACE', value: 'place'},
      {text: 'CREATED AT', value: 'create_datetime'},
    ].filter(c => (props.hiddenColumns || []).findIndex(r => c.value === r) < 0);
    const events = ref([]);
    const races = ref([]);
    const organizations = ref([]);
    const eventSearchInput = ref('');
    const selectedEvent = ref(null);
    const selectedRace = ref(null);
    const findingEvents = ref(false);

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });
    watch(selectedEvent, () => {
      selectedRace.value = null;
      loadRecords(1);
      loadRaces();
    });
    watch(selectedRace, (value) => {
      if (value) {
        tableOptions.value.sortBy = ['place'];
      }
      loadRecords(1);
    });

    const findEvents = (search) => {
      if (findingEvents.value) {
        events.value = [];
        return;
      }
      findingEvents.value = true;
      axios.get("bycing_org/event/", {params: {search: search}}).then((response) => {
        findingEvents.value = false;
        events.value = response.data.results;
      }, (error) => {
        findingEvents.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findEventsDebounce = _.debounce(findEvents, 500);

    const displayRiderName = (r) => {
      var name = '';
      if (r._rider) {
        name = `${r._rider.first_name} ${r._rider.last_name}`.trim();
      } else {
        name = `${r.more_data.first_name || ''} ${r.more_data.last_name || ''}`.trim();
      }
      return name || 'N/A'
    };

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign(
          {exfields: 'more_data'},
          tableFiltering.value, props.apiParams, refineVTableOptions(tableOptions.value)
      );
      if (!params.include_dns_dnf) {
        params.finish_status = 'ok';
      }
      delete params.include_dns_dnf;
      if (selectedRace.value) {
        params.race = selectedRace.value.id
      } else if (selectedEvent.value) {
        params.event = selectedEvent.value.id
      }
      loading.value = true;
      if (params.organization && typeof params.organization === "object") {
        params.organization = params.organization.id;
      }
      axios.get("bycing_org/race_result/", {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };
    const loadRaces = () => {
      if (!selectedEvent.value) {
        races.value = [];
        return
      }
      loadingRaces.value = true;
      axios.get("bycing_org/race/", {params: {event: selectedEvent.value.id, page_size: 0}}).then((response) => {
        loadingRaces.value = false;
        races.value = response.data.results;
      }, (error) => {
        loadingRaces.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const loadOrganizations = () => {
      loadingOrganizations.value = true;
      axios.get("bycing_org/organization/", {params: {page_size: 0}}).then((response) => {
        loadingOrganizations.value = false;
        organizations.value = response.data.results;
        if (route.value.query.organization) {
          tableFiltering.value.organization = _.find(organizations.value, {id: route.value.query.organization * 1});
        }
      }, (error) => {
        loadingOrganizations.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const getRiderRoute = (rider) => {
      if (!props.riderRoute) {
        return {};
      }
      return {name: props.riderRoute, params:{record_id: rider}}
    };

    watch(() => tableFiltering, (currentValue, oldValue) => {
        loadRecords(1);
      },
      { deep: true }
    );

    onMounted(() => {
      loadOrganizations();
    });

    return {
      records,
      eventSearchInput,
      events,
      races,
      organizations,
      selectedEvent,
      selectedRace,
      findEvents,
      findEventsDebounce,
      findingEvents,
      displayRiderName,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      loadingRaces,
      loadingOrganizations,
      pagination,
      avatarText,
      getRiderRoute,
      loadRecords,
      loadRaces,
      icons: {
        mdiPencilOutline,
        mdiEyeOutline,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiClose,
        mdiCheck,
        mdiInformationOutline,
        mdiRefresh,
        mdiAccountCheck,
        mdiFileExcelOutline,
        mdiPodiumGold,
      },
    }
  },
}
</script>
