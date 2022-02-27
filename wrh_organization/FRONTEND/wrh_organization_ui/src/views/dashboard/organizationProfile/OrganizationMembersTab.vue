<template>
  <div class="member-profile-organization-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn small color="primary" class="me-3" @click="$refs.formDialogRef.show()">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>Add Member</span>
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

          <v-switch hide-details class="mt-0" v-model="tableFiltering.is_active">
            <template #label>
              <span class="text-sm ms-2">Only Active?</span>
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
        :item-class="tableRowClass"
      >
        <template #item.datetime="{item}">
          {{$utils.formatDate(item.datetime)}}
        </template>

        <template #item.is_admin="{item}">
          <v-tooltip v-if="item.is_master_admin" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on" color="success">{{icons.mdiAccountCheck}}</v-icon>
            </template>
            <span>Is Master Admin</span>
          </v-tooltip>
          <v-tooltip v-else-if="item.is_admin" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on" color="success">{{icons.mdiAccountCheckOutline}}</v-icon>
            </template>
            <span>Is Admin</span>
          </v-tooltip>
          <span v-else>-</span>
        </template>

        <template #item.name="{item}">
          <div class="d-flex align-center">
            <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
              <v-img v-if="item._member._user.avatar" :src="item._member._user.avatar"></v-img>
              <span v-else class="font-weight-medium">
                {{ avatarText(item._member.first_name) }}
              </span>
            </v-avatar>

            <div class="d-flex flex-column ms-3">
              <span class="d-block text--success  font-weight-semibold text-truncate">{{ item._member.first_name }} {{ item._member.last_name }}</span>
              <span class="text-xs">{{ item._member.email || '-' }}</span>
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
                <v-btn icon small v-bind="attrs" v-on="on">
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
    <organization-member-form-dialog ref="formDialogRef" :organization="organization"
                                     @save-successed="loadRecords(1)" @delete-successed="loadRecords(1)">
    </organization-member-form-dialog>
  </div>
</template>

<script>
import {
  mdiPlus,
  mdiPencilOutline,
  mdiEyeOutline,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiAccountCheck,
  mdiAccountCheckOutline,
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import store from '@/store'
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import OrganizationMemberFormDialog from "./OrganizationMemberFormDialog";

export default {
  components: {OrganizationMemberFormDialog},
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({is_active: true});
    const tableColumns = [
      {text: 'NAME', value: 'name'},
      {text: 'ADMIN?', value: 'is_admin'},
      {text: 'JOINED AT', value: 'datetime'},
      {text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,},
    ];

    const tableRowClass = (item) => {
      return `member-row${!item.is_active? ' inactive': ''}`
    };

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      if (!params.is_active) {
        delete params.is_active;
      }
      loading.value = true;
      axios.get(`bycing_org/organization/${props.organization.id}/members`, {params: params}).then((response) => {
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
      tableRowClass,

      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiEyeOutline,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiAccountCheck,
        mdiAccountCheckOutline,
      },
    }
  },
}
</script>

<style lang="scss">
.member-profile-organization-tab {
  .organization-search {
    max-width: 10.625rem;
  }
  .organization-list-actions {
    max-width: 7.81rem;
  }
  table tr.member-row.inactive td:not(:last-child) {
    opacity: 0.5;
  }
}
</style>
