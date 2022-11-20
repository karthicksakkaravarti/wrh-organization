<template>
  <div class="member-org-profile-organization-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn fab x-small color="info" class="me-1" @click="loadRecords(1)">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
          <v-tooltip bottom v-if="organization.my_level.is_admin">
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" small color="primary" class="me-1" @click="$refs.formDialogRef.show()">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiHomePlus }}
                </v-icon>
                <span>Member Org</span>
              </v-btn>
            </template>
            <span>Add A Member-Org To Organization</span>
          </v-tooltip>
          <v-tooltip bottom v-if="organization.my_level.is_admin">
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" small outlined color="info" class="me-1" @click="$refs.importDialogRef.show()">
                <v-icon size="18" class="me-1">
                  {{ icons.mdiFileExcelOutline }}
                </v-icon>
                <span>Import</span>
              </v-btn>
            </template>
            <span>Import member orgs from CSV file</span>
          </v-tooltip>
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
        :footer-props="{'items-per-page-options': $const.DEFAULT_TABLE_PER_PAGE_OPTIONS, 'show-current-page': true, 'show-first-last-page': true}"
      >
        <template #item.datetime="{item}">
          <span class="pr-1">{{$utils.formatDate(item.datetime, 'M/D/YY')}}</span>
          <span class="text-caption">{{$utils.formatDate(item.datetime, 'HH:mm')}}</span>
        </template>
        <template #item.start_date="{item}">
          <v-tooltip bottom v-if="item.start_date">
            <template #activator="{ on, attrs }">
              <span v-on="on">{{$utils.formatDate(item.start_date, 'M/D/YY', 'N/A')}}</span>
            </template>
            <span>{{$utils.formatDate(item.start_date, 'MMM D, YYYY', 'N/A')}}</span>
          </v-tooltip>
          <span v-else>N/A</span>
          -
          <v-tooltip bottom v-if="item.exp_date">
            <template #activator="{ on, attrs }">
              <span v-on="on">{{$utils.formatDate(item.exp_date, 'M/D/YY', 'N/A')}}</span>
            </template>
            <span>{{$utils.formatDate(item.exp_date, 'MMM D, YYYY', 'N/A')}}</span>
          </v-tooltip>
          <span v-else>N/A</span>
        </template>
        <template #item.status="{item}">
          <v-tooltip bottom v-if="item.status == 'accept'" color="success">
            <template #activator="{ on, attrs }">
              <v-icon color="success" v-on="on">{{icons.mdiCheckCircleOutline}}</v-icon>
            </template>
            <span>Accepted</span>
          </v-tooltip>
          <v-tooltip bottom v-else-if="item.status == 'reject'" color="error">
            <template #activator="{ on, attrs }">
              <v-icon color="error" v-on="on">{{icons.mdiCloseCircleOutline}}</v-icon>
            </template>
            <span>Rejected</span>
          </v-tooltip>
          <v-tooltip bottom v-else-if="item.status == 'waiting'" color="warning">
            <template #activator="{ on, attrs }">
              <v-icon color="warning" v-on="on">{{icons.mdiSyncCircle}}</v-icon>
            </template>
            <span>Waiting for member review</span>
          </v-tooltip>
          <span v-else>{{item.status || '-'}}</span>
        </template>
        <template #item.member_org="{item}">
          <a is="router-link" :to="{name: $rns.PUBLIC_ORG_PROFILE, params:{record_id: item.member_org}}"
             class="d-flex align-center title-link" @click="$refs.formDialogRef.show(item)">
            <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
              <v-img v-if="item._member_org.logo" :src="item._member_org.logo"></v-img>
              <span v-else class="font-weight-medium">
                {{ avatarText(item._member_org.name) }}
              </span>
            </v-avatar>

            <div class="d-flex flex-column ms-3">
              <span class="d-block text--success  font-weight-semibold text-truncate">
                {{ item._member_org.name }}
              </span>
              <span class="text-xs" :class="`${($const.ORGANIZATION_TYPE_MAP[item._member_org.type] || {}).css}--text`">{{($const.ORGANIZATION_TYPE_MAP[item._member_org.type] || {}).title || item._member_org.type}}</span>
            </div>
          </a>
        </template>

        <!-- actions -->
        <template #item.actions="{item}">
          <div class="d-flex align-end justify-end">
            <v-tooltip bottom v-if="organization.my_level.is_admin">
              <template #activator="{ on, attrs }">
                <v-btn icon small v-bind="attrs" v-on="on" @click="$refs.formDialogRef.show(item)">
                  <v-icon size="18">
                    {{ icons.mdiPencilOutline }}
                  </v-icon>
                </v-btn>
              </template>
              <span>Edit / View</span>
            </v-tooltip>

          </div>
        </template>

      </v-data-table>
    </v-card>
    <organization-member-org-form-dialog ref="formDialogRef" :organization="organization"
                                         @save-successed="loadRecords(1)" @delete-successed="loadRecords(1)">
    </organization-member-org-form-dialog>
    <organization-import-member-orgs-dialog ref="importDialogRef" :organization="organization"
                                            @import-successed="loadRecords(1)">
    </organization-import-member-orgs-dialog>
  </div>
</template>

<script>
import {
  mdiHomePlus,
  mdiPencilOutline,
  mdiEyeOutline,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiAccountCheck,
  mdiAccountCancel,
  mdiAccountCheckOutline,
  mdiFileExcelOutline,
  mdiSyncCircle,
  mdiCheckCircleOutline,
  mdiCloseCircleOutline,
  mdiRefresh, mdiAccountPlusOutline,
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import store from '@/store'
import axios from "@/axios";
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import OrganizationMemberOrgFormDialog from "@/views/dashboard/organizationProfile/OrganizationMemberOrgFormDialog";
import OrganizationImportMemberOrgsDialog
  from "@/views/dashboard/organizationProfile/OrganizationImportMemberOrgsDialog";

export default {
  components: {
    OrganizationImportMemberOrgsDialog,
    OrganizationMemberOrgFormDialog
  },
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
      {text: 'MEMBER-ORG', value: 'member_org'},
      {text: 'START/EXP DATE', value: 'start_date'},
      {text: 'CREATED AT', value: 'datetime'},
      {text: 'STATUS', value: 'status'},
    ];
    if (props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }

    const tableRowClass = (item) => {
      return `member-org-row${!item.is_active? ' inactive': ''}`
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
      axios.get(`bycing_org/organization/${props.organization.id}/member_orgs`, {params: params}).then((response) => {
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
        mdiHomePlus,
        mdiPencilOutline,
        mdiEyeOutline,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiAccountCheck,
        mdiAccountCheckOutline,
        mdiFileExcelOutline,
        mdiSyncCircle,
        mdiCheckCircleOutline,
        mdiCloseCircleOutline,
        mdiAccountCancel,
        mdiRefresh,
      },
    }
  },
}
</script>

<style lang="scss">
.member-org-profile-organization-tab {
  a.title-link {
    color: inherit;
    text-decoration: none;
  }
  .organization-search {
    max-width: 10.625rem;
  }
  table tr.member-org-row.inactive td:not(:last-child) {
    opacity: 0.5;
  }
}
</style>
