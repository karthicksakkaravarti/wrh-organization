<template>
  <v-card>
    <v-card-title class="align-start">
      <span>Team Orgs</span>
    </v-card-title>
    <v-divider></v-divider>

    <v-data-table
      :headers="tableColumns"
      :items="organizations"
      hide-default-footer
      class="table-rounded"
    >
      <template #item.type="{item}">
        <v-chip small :color="($const.ORGANIZATION_TYPE_MAP[item.type] || {}).css"
                :class="`v-chip-light-bg ${($const.ORGANIZATION_TYPE_MAP[item.type] || {}).css}--text`">
          {{($const.ORGANIZATION_TYPE_MAP[item.type] || {}).title || item.type}}
        </v-chip>
      </template>

      <template #item.name="{item}">
        <div class="d-flex align-center">
          <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
            <v-img v-if="item.logo" :src="item.logo"></v-img>
            <span v-else class="font-weight-medium">
              {{ avatarText(item.name) }}
            </span>
          </v-avatar>

          <div class="d-flex flex-column ms-3">
            <a is="router-link" :to="{name: $rns.PUBLIC_ORG_PROFILE, params:{record_id: item.id}}"
               class="d-block text--success  font-weight-semibold text-truncate text-decoration-none">{{ item.name }}
            </a>
          </div>
        </div>
      </template>
      <template #item.location="{item}">
        {{ item.country || '' }}{{ item.state? ` - ${item.state}`:'' }}{{item.city? ` - ${item.city}`:'' }}
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
    const organizations = ref([]);
    const loading = ref(false);

    const loadOrganizations = () => {
      loading.value = true;
      var params = {
        page_size: 6,
        order_by: '-id'
      };
      axios.get(`bycing_org/organization`, {params: params}).then((response) => {
        loading.value = false;
        organizations.value = response.data.results;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    onMounted(() => {
      loadOrganizations();
    });

    const tableColumns = [
      {text: 'NAME', value: 'name'},
      {text: 'TYPE', value: 'type'},
      {text: 'LOCATION', value: 'location', sortable: false},
    ];

    return {
      organizations,
      tableColumns,
      avatarText,
      icons: {
      },
    }
  },
}
</script>
