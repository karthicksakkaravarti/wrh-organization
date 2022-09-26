<template>
  <v-card>
    <v-card-title class="align-start pb-3 pt-5">
      <span>Race-Series List</span>
    </v-card-title>
    <v-divider></v-divider>
    <v-data-table
      :headers="tableColumns"
      :items="raceSeries"
      :options.sync="tableOptions"
      @update:options="loadRaceSeries()"
      :server-items-length="pagination.total"
      :loading="loading"
      class="text-no-wrap"
      :footer-props="{'items-per-page-options': $const.DEFAULT_TABLE_PER_PAGE_OPTIONS, 'show-current-page': true, 'show-first-last-page': true}"
    >
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

    </v-data-table>

  </v-card>
</template>

<script>
import {
  mdiAccountCheck,
  mdiPodiumGold,
} from '@mdi/js'
import {onMounted, ref} from "@vue/composition-api";
import moment from "moment/moment";
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";

export default {
  props: {
    event: {
      type: Object,
      required: true
    },
  },
  setup(props) {
    const raceSeries = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({});

    const loadRaceSeries = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({event: props.event.id, fields: 'id,name,start_datetime'}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      loading.value = true;
      axios.get("bycing_org/race_series/", {params: params}).then((response) => {
        loading.value = false;
        raceSeries.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    onMounted(() => {
      loadRaceSeries();
    });

    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'NAME', value: 'name'},
      {text: 'STARTED AT', value: 'start_datetime'},
    ];

    return {
      raceSeries,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      tableColumns,
      avatarText,
      loadRaceSeries,
      // icons
      icons: {
        mdiAccountCheck,
        mdiPodiumGold,
      },
    }
  },
}
</script>
