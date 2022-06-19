<template>
  <div class="organization-profile-race-series-tab">
    <v-card>
      <v-card-text class="pt-2 pb-2 pr-2 pl-2">
        <v-row>
          <v-col cols="12">
            <v-autocomplete
                v-model="tableFiltering.events"
                outlined
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
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1);">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
          <v-btn v-if="organization.my_level.is_admin" small color="primary" class="me-1"
                 @click="$refs.formDialogRef.show(null)">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>New Race Series</span>
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
        <template #item.events="{item}">
          <div>
            <v-chip lable small color="secondary" v-for="r in item._events" :key="r.id" class="mr-1">{{r.name}}</v-chip>
          </div>
        </template>
        <template #item.races="{item}">
          <div>
            <v-chip lable small color="primary" v-for="r in item._races" :key="r.id" class="mr-1">{{r.name}}</v-chip>
          </div>
        </template>
        <template #item.categories="{item}">
          <div>
            <v-chip lable small color="info" v-for="r in item._categories" :key="r.id" class="mr-1">{{r.title}}</v-chip>
          </div>
        </template>
        <template #item.name="{item}">
            <span class="text-truncate font-weight-semibold">
              {{item.name}}
            </span>
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
    <organization-race-series-form-dialog :organization="organization" ref="formDialogRef" @save-successed="loadRecords(1)"
                                    @delete-successed="loadRecords(1)">
    </organization-race-series-form-dialog>
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
import _ from "lodash";
import OrganizationRaceSeriesFormDialog from "./OrganizationRaceSeriesFormDialog";

export default {
  components: {OrganizationRaceSeriesFormDialog},
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
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'NAME', value: 'name'},
      {text: 'EVENTS', value: 'events', cellClass: 'events-td', sortable: false},
      {text: 'RACES', value: 'races', cellClass: 'races-td', sortable: false},
      {text: 'CATEGORIES', value: 'categories', cellClass: 'categories-td', sortable: false},
      {text: 'CREATED AT', value: 'create_datetime'},
    ];
    if (props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false})
    }
    const events = ref([]);
    const eventSearchInput = ref('');
    const findingEvents = ref(false);

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });

    const findEvents = (search, ids) => {
      if (findingEvents.value) {
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

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({organization: props.organization.id}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      if (params.events) {
        params.events = params.events.id
      } else {
        delete params.events;
      }
      loading.value = true;
      axios.get("bycing_org/race_series/", {params: params}).then((response) => {
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
      findEvents,
      findEventsDebounce,
      findingEvents,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      loadRecords,
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
.organization-profile-race-series-tab {
  .search-input {
    max-width: 10.625rem;
  }
}
</style>
