<template>
  <v-card>
    <v-card-title class="align-start">
      <span>Recent Winners</span>
    </v-card-title>
    <v-divider></v-divider>

    <v-data-table
      :headers="tableColumns"
      :items="raceResults"
      item-key="fullName"
      hide-default-footer
      class="table-rounded"
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
            <a v-if="item.rider" is="router-link" :to="{name: $rns.PUBLIC_RIDER_PROFILE, params:{record_id: item.rider}}" class="font-weight-semibold text-truncate text-decoration-none">
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
      <template #item.place="{item}">
        <template v-if="item.finish_status == 'ok'">
          <span class="font-weight-semibold">{{item.place || 'N/A'}}</span>
          <v-icon size="20" color="warning" v-if="item.place == 1" class="ml-1">{{ icons.mdiPodiumGold }}</v-icon>
        </template>
        <v-chip v-else outlined :color="($const.RACE_FINISH_STATUS_MAP[item.finish_status] || {}).css" small>
          {{($const.RACE_FINISH_STATUS_MAP[item.finish_status] || {}).title || item.finish_status}}
        </v-chip>
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
import {notifyDefaultServerError} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";

export default {
  setup() {
    const raceResults = ref([]);
    const loading = ref(false);

    const loadReceResults = () => {
      loading.value = true;
      var params = {
        page_size: 6,
        place: 1,
        order_by: '-id'
      };
      axios.get(`bycing_org/race_result`, {params: params}).then((response) => {
        loading.value = false;
        raceResults.value = response.data.results;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const displayRiderName = (r) => {
      var name = '';
      if (r._rider) {
        name = `${r._rider.first_name} ${r._rider.last_name}`.trim();
      } else {
        name = `${r.more_data.first_name || ''} ${r.more_data.last_name || ''}`.trim();
      }
      return name || 'N/A'
    };

    onMounted(() => {
      loadReceResults();
    });

    const tableColumns = [
      {text: 'RIDER', value: 'rider'},
      {text: 'RACE', value: 'race', cellClass: 'race-td'},
      {text: 'PLACE', value: 'place'},
    ];

    return {
      raceResults,
      tableColumns,
      avatarText,
      displayRiderName,
      // icons
      icons: {
        mdiAccountCheck,
        mdiPodiumGold,
      },
    }
  },
}
</script>
