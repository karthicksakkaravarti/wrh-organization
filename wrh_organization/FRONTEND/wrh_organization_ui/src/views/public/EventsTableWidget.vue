<style scoped>
</style>

<template>
  <v-card>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="3" sm="6">
          <div class="d-flex align-center">
            <v-btn small color="primary" class="mr-5" @click="$emit('add-action-clicked')" v-if="showActions">
              <v-icon left>{{icons.mdiCalendarPlus}}</v-icon>
              New Event
            </v-btn>
            <v-text-field
                :value="tableFiltering.search"
                @change="value => $set(tableFiltering, 'search', value)"
                @click:clear="$set(tableFiltering, 'search', null)"
                dense clearable hide-details
                placeholder="Search ..." class="me-3 search-input"
            ></v-text-field>
          </div>
        </v-col>
        <v-col cols="12" md="3" sm="6">
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

        <v-col cols="12" md="3" sm="6">
          <v-menu v-model="fromDateMenu" :close-on-content-click="false"
              :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
            <template v-slot:activator="{ on, attrs }">
              <v-text-field class="pt-0 pb-0" v-model="tableFiltering.start_date__gte" label="From Date" hide-details
                            v-bind="attrs" v-on="on" dense readonly clearable>
              </v-text-field>
            </template>
            <v-date-picker v-model="tableFiltering.start_date__gte" color="primary" no-title @input="fromDateMenu = false">
            </v-date-picker>
          </v-menu>
        </v-col>
        <v-col cols="12" md="3" sm="6">
          <v-menu v-model="toDateMenu" :close-on-content-click="false"
              :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
            <template v-slot:activator="{ on, attrs }">
              <v-text-field class="pt-0 pb-0" v-model="tableFiltering.start_date__lte" label="To Date" hide-details
                            v-bind="attrs" v-on="on" dense readonly clearable>
              </v-text-field>
            </template>
            <v-date-picker v-model="tableFiltering.start_date__lte" color="primary"  @input="toDateMenu = false">
            </v-date-picker>
          </v-menu>
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
      <template #item.name="{item}">
        <a @click="onClickName(item)" class="text-decoration-none">
          <div class="d-flex align-center">
            <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
              <v-img v-if="item.logo" :src="item.logo"></v-img>
              <span v-else class="font-weight-medium">
                {{ avatarText(item.name) }}
              </span>
            </v-avatar>

            <div class="d-flex flex-column pl-1">
              <span class="font-weight-semibold text-truncate text-decoration-none">
                {{ item.name }}
              </span>
              <small class="text--secondary" v-if="item.organization">{{ item._organization.name }}</small>
            </div>
          </div>
        </a>

      </template>
      <template #item.start_date="{item}">
        {{$utils.formatDate(item.start_date, 'MMM D, YYYY')}}
      </template>
      <template #item.end_date="{item}">
        {{$utils.formatDate(item.end_date, 'MMM D, YYYY', '-')}}
      </template>
      <template #item.location="{item}">
        <span class="font-weight-medium">{{ item.country || '' }}{{ item.state? `, ${item.state}`:'' }}{{item.city? `, ${item.city}`:'' }}</span>
      </template>
      <template #item.actions="{item}">
        <div class="d-flex align-end justify-end">
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn icon small v-bind="attrs" v-on="on" @click="$emit('edit-action-clicked', item)">
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
  mdiCalendarPlus,
} from '@mdi/js'

import { ref, watch, onMounted } from '@vue/composition-api'
import axios from "@/axios";
import {avatarText} from "@core/utils/filter";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {useRouter} from "@core/utils";
import {routeNames} from "@/router";
import _ from "lodash";

export default {
  components: {},
  props: {
    apiParams: {
      type: Object,
      required: false
    },
    showActions: {
      type: Boolean,
      default: false
    },
  },
  setup(props, context) {
    const { route, router } = useRouter();
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const loadingOrganizations = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref(route.value.query || {});
    const organizations = ref([]);
    const fromDateMenu = ref();
    const toDateMenu = ref();
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'TITLE', value: 'name'},
      {text: 'START', value: 'start_date'},
      {text: 'END', value: 'end_date'},
      {text: 'LOCATION', value: 'location'},
    ];
    if (props.showActions) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({}, tableFiltering.value, props.apiParams, refineVTableOptions(tableOptions.value));
      if (params.organization && typeof params.organization === "object") {
        params.organization = params.organization.id;
      }
      if ((params.order_by || '').endsWith('location')) {
        var desc = params.order_by[0] === '-'? '-': '';
        params.order_by = ['country', 'city', 'state'].map(f => `${desc}${f}`).join(',');
      }
      loading.value = true;
      axios.get("cycling_org/event/", {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const loadOrganizations = () => {
      loadingOrganizations.value = true;
      axios.get("cycling_org/organization/", {params: {page_size: 0}}).then((response) => {
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

    const onClickName = (item) => {
      if (props.showActions) {
        context.emit('edit-action-clicked', item);
      } else {
        router.push({name: routeNames.PUBLIC_EVENT_PROFILE, params: {record_id: item.id}})
      }
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
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      loadRecords,
      loadingOrganizations,
      organizations,
      avatarText,
      onClickName,
      fromDateMenu,
      toDateMenu,
      icons: {
        mdiPencilOutline,
        mdiCalendarPlus,
      },
    }
  },
}
</script>
