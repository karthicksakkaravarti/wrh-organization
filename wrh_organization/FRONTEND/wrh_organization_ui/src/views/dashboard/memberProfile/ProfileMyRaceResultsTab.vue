<template>
  <div class="profile-my-race-results-tab">
    <v-card>
      <v-card-text>
        <v-row>
          <v-col cols="4">
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
          <v-col cols="4">
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
          <v-col cols="4">
            <div class="d-flex align-center pb-5">
              <v-text-field
                  :value="tableFiltering.search"
                  @change="value => $set(tableFiltering, 'search', value)"
                  @click:clear="$set(tableFiltering, 'search', null)"
                  dense clearable hide-details
                  placeholder="Search ..." class="me-3 search-input"
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1);">
                <v-icon>{{icons.mdiRefresh}}</v-icon>
              </v-btn>
            </div>

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
              <span href="javascript:" class="font-weight-semibold text-truncate text-decoration-none">
                <v-icon v-if="item._rider" small>{{icons.mdiAccountCheck}}</v-icon> {{ displayRiderName(item) }}
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
          <span class="font-weight-semibold">{{item.place}}</span>
          <v-icon size="20" color="warning" v-if="item.place == 1" class="ml-1">{{ icons.mdiPodiumGold }}</v-icon>
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
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import _ from "lodash";

export default {
  components: {},
  props: {
  },
  setup(props, context) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const loadingRaces = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({});
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'RIDER', value: 'rider'},
      {text: 'RACE', value: 'race', cellClass: 'race-td'},
      {text: 'PLACE', value: 'place'},
      {text: 'CREATED AT', value: 'create_datetime'},
    ];
    const events = ref([]);
    const races = ref([]);
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
    watch(selectedRace, () => {
      loadRecords(1);
    });

    const findEvents = (search) => {
      if (findingEvents.value) {
        events.value = [];
        return;
      }
      findingEvents.value = true;
      axios.get("usacycling/event/", {params: {search: search}}).then((response) => {
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
      const params = Object.assign({my: true}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      if (selectedRace.value) {
        params.race = selectedRace.value.id
      } else if (selectedEvent.value) {
        params.event = selectedEvent.value.event_id
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
      axios.get("bycing_org/race/", {params: {event: selectedEvent.value.event_id, page_size: 0}}).then((response) => {
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
.profile-my-race-results-tab {
  td.race-td {
    max-width: 250px;
  }
}
</style>
