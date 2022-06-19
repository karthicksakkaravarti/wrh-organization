<template>
  <div class="organization-profile-race-results-tab">
    <v-card>
      <v-card-text class="pt-2 pb-2 pr-2 pl-2">
        <v-row>
          <v-col cols="12">
            <v-autocomplete
                v-model="selectedRaceSeries"
                outlined
                dense
                label="Choose a Race-Series"
                :items="raceSeries"
                item-text="name"
                item-value="id"
                hide-details
                :search-input.sync="raceSeriesSearchInput"
                :loading="findingRaceSeries"
                no-data-text="No Result Found! Type here to Search Race-Series"
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
                    <v-chip x-small v-for="e in (data.item._events || [])" :key="e.id" class="mr-1">
                      {{e.name}}
                    </v-chip>
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
                 @click="$refs.formDialogRef.show(null, selectedRaceSeries)" :disabled="!selectedRaceSeries">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>Race Series Result</span>
          </v-btn>
          <v-tooltip v-if="organization.my_level.is_admin" bottom>
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" small outlined color="info" class="me-1" :disabled="!selectedRaceSeries" @click="$refs.importDialogRef.show(selectedRaceSeries)">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiFileExcelOutline }}
                </v-icon>
                <span>Import</span>
              </v-btn>
            </template>
            <span>Import results from CSV file</span>
          </v-tooltip>
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

        <template #item.race_series="{item}">
          <div class="d-flex flex-column">
            <span class="font-weight-semibold text-truncate">
              {{item._race_series.name}}
            </span>
          </div>
        </template>
        <template #item.category="{item}">
          <span class="font-weight-medium text-truncate">{{item._category.title}}</span>
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
    <organization-race-series-result-form-dialog :organization="organization" ref="formDialogRef" @save-successed="loadRecords(1)"
                                          @delete-successed="loadRecords(1)">
    </organization-race-series-result-form-dialog>
    <organization-import-race-series-results-dialog ref="importDialogRef" :organization="organization"
                                             @import-successed="loadRecords(1)">
    </organization-import-race-series-results-dialog>
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
import {notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import OrganizationRaceResultFormDialog from "./OrganizationRaceResultFormDialog";
import _ from "lodash";
import OrganizationImportRaceResultsDialog
  from "@/views/dashboard/organizationProfile/OrganizationImportRaceResultsDialog";
import OrganizationRaceSeriesResultFormDialog
  from "@/views/dashboard/organizationProfile/OrganizationRaceSeriesResultFormDialog";
import OrganizationImportRaceSeriesResultsDialog
  from "@/views/dashboard/organizationProfile/OrganizationImportRaceSeriesResultsDialog";

export default {
  components: {
    OrganizationImportRaceSeriesResultsDialog,
    OrganizationRaceSeriesResultFormDialog
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
    const tableOptions = ref({});
    const tableFiltering = ref({});
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'RIDER', value: 'rider'},
      {text: 'RACE-SERIES', value: 'race_series', cellClass: 'race-series-td'},
      {text: 'CATEGORY', value: 'category'},
      {text: 'PLACE', value: 'place'},
      {text: 'CREATED AT', value: 'create_datetime'},
    ];
    if (props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }
    const raceSeries = ref([]);
    const races = ref([]);
    const raceSeriesSearchInput = ref('');
    const selectedRaceSeries = ref(null);
    const findingRaceSeries = ref(false);

    watch(raceSeriesSearchInput, () => {
      findRaceSeriesDebounce(raceSeriesSearchInput.value);
    });
    watch(selectedRaceSeries, () => {
      loadRecords(1);
    });

    const findRaceSeries = (search) => {
      if (findingRaceSeries.value) {
        raceSeries.value = [];
        return;
      }
      findingRaceSeries.value = true;
      axios.get("bycing_org/race_series/", {params: {search: search}}).then((response) => {
        findingRaceSeries.value = false;
        raceSeries.value = response.data.results;
      }, (error) => {
        findingRaceSeries.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findRaceSeriesDebounce = _.debounce(findRaceSeries, 500);

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
      const params = Object.assign({organization: props.organization.id}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      if (selectedRaceSeries.value) {
        params.race_series = selectedRaceSeries.value.id
      }
      loading.value = true;
      axios.get("bycing_org/race_series_result/", {params: params}).then((response) => {
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
      raceSeriesSearchInput,
      raceSeries,
      races,
      selectedRaceSeries,
      findRaceSeries,
      findRaceSeriesDebounce,
      findingRaceSeries,
      displayRiderName,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      avatarText,
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
.organization-profile-race-results-tab {
  .search-input {
    max-width: 10.625rem;
  }
  td.race-td {
    max-width: 250px;
  }
}
</style>
