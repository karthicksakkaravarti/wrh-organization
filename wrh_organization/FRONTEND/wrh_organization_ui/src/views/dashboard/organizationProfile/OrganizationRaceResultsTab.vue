<template>
  <div class="organization-profile-race-results-tab">
    <v-card>
      <v-card-text class="pt-2 pb-2 pr-2 pl-2">
        <v-row>
          <v-col cols="6">
            <v-autocomplete
                v-model="selectedEvent"
                outlined
                dense
                label="Choose Event"
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
          <v-col cols="6">
            <v-autocomplete
                :disabled="!selectedEvent"
                v-model="selectedRace"
                outlined
                dense
                label="Choose Race"
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
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text>
        <div class="align-center">
          <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1);">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
          <v-btn v-if="organization.my_level && organization.my_level.is_admin" small color="primary" class="me-1"
                 @click="$refs.formDialogRef.show(null, selectedRace)" :disabled="!selectedRace">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>Race Result</span>
          </v-btn>
          <v-tooltip v-if="organization.my_level && organization.my_level.is_admin" bottom>
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" small outlined color="info" class="me-1" :disabled="!selectedRace" @click="$refs.importDialogRef.show(selectedRace)">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiFileExcelOutline }}
                </v-icon>
                <span>Import</span>
              </v-btn>
            </template>
            <span>Import results from CSV file</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" small outlined color="error" class="me-1" :href="exportUrl" target="_blank" :disabled="!selectedEvent">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiFileExcelOutline }}
                </v-icon>
                <span>Export</span>
              </v-btn>
            </template>
            <span>Export results to CSV file</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" v-if="organization.my_level && organization.my_level.is_admin" small color="info" class="me-1"
                     @click="$refs.raceSeriesResultsDialogRef.show(selectedRace, selectedRows)" :disabled="!selectedRace || !selectedRows.length">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiPencilOutline }}
                </v-icon>
                <span>Race-Series Result</span>
              </v-btn>
            </template>
            <span>Add/Update Race-Series Results of selected rows</span>
          </v-tooltip>
        </div>
      </v-card-text>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4" sm="6">
            <v-text-field
                :value="tableFiltering.search"
                @change="value => $set(tableFiltering, 'search', value)"
                @click:clear="$set(tableFiltering, 'search', null)"
                dense clearable hide-details
                placeholder="Search ..." class="search-input"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4" sm="6">
            <v-checkbox v-model="tableFiltering.include_dns_dnf" hide-details label="Include DNS/DNF?" class="mt-1"></v-checkbox>
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
        :show-select="!!selectedRace"
        v-model="selectedRows"
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
              <a v-if="item.rider" is="router-link" :to="{name: $rns.PUBLIC_RIDER_PROFILE, params:{record_id: item.rider}}" target="_blank" class="font-weight-semibold text-truncate text-decoration-none">
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
          </div>
        </template>
        <template #item.event="{item}">
          <div class="d-flex flex-column">
            <span class="text-truncate">
              {{item._race._event.name}}
            </span>
          </div>
          <span class="text-caption">
            {{ $utils.formatDate(item._race._event.start_date, 'MMM D, YYYY') }} - {{ $utils.formatDate(item._race._event.end_date, 'MMM D, YYYY') }}
          </span>
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
    <organization-race-result-form-dialog :organization="organization" ref="formDialogRef" @save-successed="loadRecords(1)"
                                          @delete-successed="loadRecords(1)">
    </organization-race-result-form-dialog>
    <organization-race-series-results-form-dialog :organization="organization" ref="raceSeriesResultsDialogRef" >
    </organization-race-series-results-form-dialog>
    <organization-import-race-results-dialog ref="importDialogRef" :organization="organization"
                                             @import-successed="loadRecords(1)">
    </organization-import-race-results-dialog>
  </div>
</template>

<script>
import {
  mdiPlus,
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
import store from '@/store'
import axios from "@/axios";
import {combineURLs, notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import OrganizationRaceResultFormDialog from "./OrganizationRaceResultFormDialog";
import _ from "lodash";
import OrganizationImportRaceResultsDialog
  from "@/views/dashboard/organizationProfile/OrganizationImportRaceResultsDialog";
import {computed} from "@vue/composition-api/dist/vue-composition-api";
import OrganizationRaceSeriesResultsFormDialog
  from "@/views/dashboard/organizationProfile/OrganizationRaceSeriesResultsFormDialog";

export default {
  components: {
    OrganizationRaceSeriesResultsFormDialog,
    OrganizationImportRaceResultsDialog,
    OrganizationRaceResultFormDialog
  },
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const loadingRaces = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({});
    const selectedRows = ref([]);
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'RIDER', value: 'rider'},
      {text: 'PLACE', value: 'place'},
      {text: 'RACE', value: 'race', cellClass: 'race-td'},
      {text: 'EVENT', value: 'event', cellClass: 'event-td'},
      // {text: 'CREATED AT', value: 'create_datetime'},
    ];
    if (props.organization.my_level && props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }
    const events = ref([]);
    const races = ref([]);
    const eventSearchInput = ref('');
    const selectedEvent = ref(null);
    const selectedRace = ref(null);
    const findingEvents = ref(false);

    const exportUrl = computed(() => {
      const params = Object.assign({organization: props.organization.id}, tableFiltering.value);
      if (selectedRace.value) {
        params.race = selectedRace.value.id
      } else if (selectedEvent.value) {
        params.event = selectedEvent.value.id
      }
      return combineURLs(axios.defaults.baseURL, `bycing_org/race_result/export/csv`, params);
    });

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });
    watch(selectedEvent, () => {
      selectedRace.value = null;
      loadRecords(1);
      loadRaces();
    });
    watch(selectedRace, (value) => {
      selectedRows.value = [];
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
          {organization: props.organization.id, exfields: 'more_data'},
          tableFiltering.value, refineVTableOptions(tableOptions.value)
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

    watch(() => tableFiltering, (currentValue, oldValue) => {
        loadRecords(1);
      },
      { deep: true }
    );

    onMounted(() => {
    });

    return {
      records,
      eventSearchInput,
      events,
      races,
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
      pagination,
      avatarText,
      loadRecords,
      loadRaces,
      selectedRows,
      exportUrl,
      icons: {
        mdiPlus,
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

<style lang="scss">
.organization-profile-race-results-tab {
  .search-input {
    max-width: 10.625rem;
  }
  td.race-td {
    max-width: 250px;
  }
  td.event-td {
    max-width: 250px;
  }
}
</style>
