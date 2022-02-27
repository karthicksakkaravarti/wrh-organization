<template>
  <div class="member-profile-organization-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn small color="primary" class="me-3" @click="$refs.formDialogRef.show()">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>New Organization</span>
          </v-btn>
        </div>

        <v-spacer></v-spacer>

        <div class="d-flex align-center pb-5">
          <v-text-field
              :value="tableFiltering.search"
              @change="value => $set(tableFiltering, 'search', value)"
              @click:clear="$set(tableFiltering, 'search', null)"
              dense clearable hide-details
              placeholder="Search ..." class="me-3 organization-search"
          ></v-text-field>

          <v-switch hide-details class="mt-0" v-model="tableFiltering.my_adminated">
            <template #label>
              <span class="text-sm ms-2">Only My Adminated</span>
            </template>
          </v-switch>
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
              <a is="router-link" :to="{name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params:{record_id: item.id}}"
                 class="d-block text--success  font-weight-semibold text-truncate text-decoration-none">{{ item.name }}
              </a>
            </div>
          </div>
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

            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon small v-bind="attrs" v-on="on"
                       :to="{name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params:{record_id: item.id}}">
                  <v-icon size="18">
                    {{ icons.mdiEyeOutline }}
                  </v-icon>
                </v-btn>
              </template>
              <span>View</span>
            </v-tooltip>
          </div>
        </template>

      </v-data-table>
    </v-card>
    <profile-organization-form-dialog ref="formDialogRef"
                                     @save-successed="loadRecords(1)" @delete-successed="loadRecords(1)">
    </profile-organization-form-dialog>
  </div>
</template>

<script>
import {
  mdiPlus,
  mdiPencilOutline,
  mdiEyeOutline,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import store from '@/store'
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import ProfileOrganizationFormDialog from "./ProfileOrganizationFormDialog";

export default {
  components: {ProfileOrganizationFormDialog},
  setup() {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({my_adminated: true});
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'NAME', value: 'name'},
      {text: 'TYPE', value: 'type'},
      {text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,},
    ];

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({my: true}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      loading.value = true;
      axios.get("bycing_org/organization/", {params: params}).then((response) => {
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

    return {
      records,
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
        mdiAccountMultipleOutline
      },
    }
  },
}
</script>

<style lang="scss" scoped>
.member-profile-organization-tab {
  .organization-search {
    max-width: 10.625rem;
  }
  .organization-list-actions {
    max-width: 7.81rem;
  }
}
</style>
