<template>
  <div class="organization-profile-races-tab">
    <v-card>
      <v-card-text class="pt-2 pb-2 pr-2 pl-2">
        <v-row>
          <v-col cols="12">
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
              <template #prepend-item>
                <v-row class="pl-1 pr-1 mb-1">
                  <v-col cols="12" md="6">
                    <v-menu v-model="eventFromDate" :close-on-content-click="false"
                        :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                      <template v-slot:activator="{ on, attrs }">
                        <v-text-field class="pt-0 pb-0" v-model="eventFiltering.from_date" label="From Date" hide-details
                                      v-bind="attrs" v-on="on" dense readonly clearable filled>
                        </v-text-field>
                      </template>
                      <v-date-picker v-model="eventFiltering.from_date" color="primary" @input="eventFromDate = false">
                      </v-date-picker>
                    </v-menu>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-menu v-model="eventToDate" :close-on-content-click="false"
                        :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                      <template v-slot:activator="{ on, attrs }">
                        <v-text-field class="pt-0 pb-0" v-model="eventFiltering.to_date" label="To Date" hide-details
                                      v-bind="attrs" v-on="on" dense readonly clearable filled>
                        </v-text-field>
                      </template>
                      <v-date-picker v-model="eventFiltering.to_date" color="primary" @input="eventToDate = false">
                      </v-date-picker>
                    </v-menu>
                  </v-col>
                </v-row>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1);">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
          <v-btn v-if="organization.my_level.is_admin" small color="primary" class="me-1"
                 @click="$refs.formDialogRef.show(null, selectedEvent)" :disabled="!selectedEvent">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>New Race</span>
          </v-btn>
        </div>

        <v-spacer></v-spacer>

        <div class="d-flex align-center pb-5">
          <v-text-field
              :value="tableFiltering.search"
              @change="value => $set(tableFiltering, 'search', value)"
              @click:clear="$set(tableFiltering, 'search', null)"
              dense clearable hide-details
              placeholder="Search ..." class="me-3 search-input"
          ></v-text-field>

        </div>
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
        <template #item.event="{item}">
          <div class="d-flex flex-column">
            <span class="text-truncate">
              {{item._event.name}}
            </span>
          </div>
          <span class="text-caption">
            {{ $utils.formatDate(item._event.start_date, 'MMM D, YYYY') }} - {{ $utils.formatDate(item._event.end_date, 'MMM D, YYYY') }}
          </span>
        </template>
        <template #item.name="{item}">
            <span class="text-truncate font-weight-semibold">
              {{item.name}}
            </span>
        </template>
        <template #item.start_datetime="{item}">
          <span v-if="!item.start_datetime">-</span>
          <template v-else>
            <span class="pr-1">{{$utils.formatDate(item.start_datetime, 'MMM D, YYYY')}}</span>
            <span class="text-caption">{{$utils.formatDate(item.start_datetime, 'HH:mm')}}</span>
          </template>
        </template>
        <template #item.create_datetime="{item}">
          <span class="pr-1">{{$utils.formatDate(item.create_datetime, 'M/D/YY')}}</span>
          <span class="text-caption">{{$utils.formatDate(item.create_datetime, 'HH:mm')}}</span>
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
    <organization-race-form-dialog :organization="organization" ref="formDialogRef" @save-successed="loadRecords(1)"
                                    @delete-successed="loadRecords(1)">
    </organization-race-form-dialog>
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
import {notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import OrganizationRaceFormDialog from "./OrganizationRaceFormDialog";
import _ from "lodash";

export default {
  components: {OrganizationRaceFormDialog},
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
    const tableOptions = ref({});
    const tableFiltering = ref({});
    const eventFromDate = ref();
    const eventToDate = ref();
    const eventFiltering = ref({});

    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'NAME', value: 'name'},
      {text: 'STARTED AT', value: 'start_datetime'},
      {text: 'EVENT', value: 'event', cellClass: 'event-td'},
      {text: 'CREATED AT', value: 'create_datetime'},
    ];
    if (props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }
    const events = ref([]);
    const eventSearchInput = ref('');
    const selectedEvent = ref(null);
    const findingEvents = ref(false);

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });
    watch(selectedEvent, () => {
      loadRecords(1);
    });
    watch(() => eventFiltering, (currentValue, oldValue) => {
        findEvents(eventSearchInput.value);
      },
      { deep: true }
    );

    const findEvents = (search) => {
      if (findingEvents.value) {
        events.value = [];
        return;
      }
      var params = {search: search};
      if (eventFiltering.value.from_date) {
        params.start_date__gte = eventFiltering.value.from_date
      }
      if (eventFiltering.value.to_date) {
        params.start_date__lte = eventFiltering.value.to_date
      }
      findingEvents.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
        findingEvents.value = false;
        events.value = response.data.results;
      }, (error) => {
        findingEvents.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findEventsDebounce = _.debounce(findEvents, 500);

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({organization: props.organization.id}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      if (selectedEvent.value) {
        params.event = selectedEvent.value.id
      }
      loading.value = true;
      axios.get("bycing_org/race/", {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
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
      selectedEvent,
      findEvents,
      findEventsDebounce,
      findingEvents,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      loadRecords,
      eventFromDate,
      eventToDate,
      eventFiltering,
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
.organization-profile-races-tab {
  .search-input {
    max-width: 10.625rem;
  }
  td.event-td {
    max-width: 250px;
  }
}
</style>
