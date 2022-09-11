<style scoped>
</style>

<template>
  <v-card>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6" sm="12">
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
        <a href="javascript:" class="font-weight-semibold text-decoration-none">{{item.name}}</a>
      </template>
      <template #item.start_date="{item}">
        {{$utils.formatDate(item.start_date, 'MMM D, YYYY')}}
      </template>
      <template #item.end_date="{item}">
        {{$utils.formatDate(item.end_date, 'MMM D, YYYY', '-')}}
      </template>
      <template #item.location="{item}">
        <span class="font-weight-medium">{{ item.country || '' }}{{ item.state? ` - ${item.state}`:'' }}{{item.city? ` - ${item.city}`:'' }}</span>
      </template>

    </v-data-table>
  </v-card>
</template>

<script>
import {
} from '@mdi/js'

import { ref, watch, onMounted } from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";

export default {
  components: {},
  props: {
    apiParams: {
      type: Object,
      required: false
    },
  },
  setup(props, context) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({});
    const fromDateMenu = ref();
    const toDateMenu = ref();
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'TITLE', value: 'name'},
      {text: 'START', value: 'start_date'},
      {text: 'END', value: 'end_date'},
      {text: 'LOCATION', value: 'location'},
    ];

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({}, tableFiltering.value, props.apiParams, refineVTableOptions(tableOptions.value));
      if ((params.order_by || '').endsWith('location')) {
        var desc = params.order_by[0] === '-'? '-': '';
        params.order_by = ['country', 'city', 'state'].map(f => `${desc}${f}`).join(',');
      }
      loading.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
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
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      loadRecords,
      fromDateMenu,
      toDateMenu,
      icons: {
      },
    }
  },
}
</script>
