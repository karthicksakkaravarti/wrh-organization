<template>
  <div class="member-profile-organization-tab">
    <v-card class="mb-1" v-if="membershipRequests && membershipRequests.length">
      <v-card-title>
        <span class="error--text">
          <v-icon color="error">{{icons.mdiInformationOutline}}</v-icon>
          Organizations Membership Requests
        </span>
      </v-card-title>
      <v-card-text>
        <v-list class="py-0">
          <template v-for="(r, index) in membershipRequests">
            <v-list-item :key="r.id" >
              <v-avatar rounded size="35" class="me-4">
                <v-img
                  :src="r._organization.logo || require('@/assets/images/misc/no-photo.png')"
                ></v-img>
              </v-avatar>

              <div>
                <v-list-item-title class="text-sm">
                  {{ r._organization.name }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ ($const.ORGANIZATION_TYPE_MAP[r._organization.type] || {}).title || r._organization.type }}
                </v-list-item-subtitle>
              </div>

              <v-spacer></v-spacer>

              <v-btn x-small color="error" min-width="38" class="px-1 mr-1" @click="reviewMembershipRequest(r, 'reject')">
                <v-icon size="20">{{icons.mdiClose }}</v-icon> Reject
              </v-btn>
              <v-btn x-small color="success" min-width="38" class="px-1" @click="reviewMembershipRequest(r, 'accept')">
                <v-icon size="20">{{icons.mdiCheck }}</v-icon> Accept
              </v-btn>
            </v-list-item>
            <v-divider :key="index"></v-divider>
          </template>

        </v-list>
      </v-card-text>
      <v-overlay :value="reviewingMembership" :absolute="true" opacity="0.3">
        <v-progress-circular indeterminate></v-progress-circular>
      </v-overlay>
    </v-card>
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1); loadMebershipRequests()">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
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

          <v-switch hide-details class="mt-0" v-model="tableFiltering.managed_by_me">
            <template #label>
              <span class="text-sm ms-2">Managed by me</span>
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
        :footer-props="{'items-per-page-options': $const.DEFAULT_TABLE_PER_PAGE_OPTIONS, 'show-current-page': true, 'show-first-last-page': true}"
      >
        <template #item.type="{item}">
          <v-chip small :color="($const.ORGANIZATION_TYPE_MAP[item.type] || {}).css"
                  :class="`v-chip-light-bg ${($const.ORGANIZATION_TYPE_MAP[item.type] || {}).css}--text`">
            {{($const.ORGANIZATION_TYPE_MAP[item.type] || {}).title || item.type}}
          </v-chip>
        </template>

        <template #item.expiry="{item}">
          <span v-if="!item.membership.exp_date || item.membership.is_admin || item.membership.is_master_admin" class="success--text">
            Never<small class="secondary--text" v-if="item.membership.is_admin || item.membership.is_master_admin">(Is Admin)</small>
          </span>
          <span v-else :class="item.membership.is_expiring? 'warning--text': 'success--text'">
            {{-$utils.moment().diff(item.membership.exp_date, 'days') + ' days'}}
          </span>

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

        <!-- actions -->
        <template #item.actions="{item}">
          <div class="d-flex align-end justify-end">
            <v-tooltip bottom v-if="$store.getters.defaultRegionalOrg == item.id">
              <template #activator="{ on, attrs }">
                <v-btn x-small outlined color="error" v-bind="attrs" v-on="on"
                       @click="setRegionalDefault(null)">
                  <v-icon size="18" left>
                    {{ icons.mdiBankCheck }}
                  </v-icon>
                  Default
                </v-btn>
              </template>
              <span>Remove as default</span>
            </v-tooltip>
            <v-tooltip bottom v-else-if="item.type == 'regional'">
              <template #activator="{ on, attrs }">
                <v-btn x-small outlined color="secondary" class="set-default" v-bind="attrs" v-on="on"
                       @click="setRegionalDefault(item.id)">
                  <v-icon size="18" left>
                    {{ icons.mdiBankCheck }}
                  </v-icon>
                  Default
                </v-btn>
              </template>
              <span>Make this regional organization as default</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon small v-bind="attrs" v-on="on"
                       :disabled="!item.membership.is_admin && !item.membership.is_master_admin"
                       :to="{name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params:{record_id: item.id}}">
                  <v-icon size="18">
                    {{ icons.mdiOfficeBuildingCog }}
                  </v-icon>
                </v-btn>
              </template>
              <span>Manage</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon small v-bind="attrs" v-on="on" @click="$refs.myMemberFieldsDialogRef.show(item)">
                  <v-icon size="18">
                    {{ (item.membership.is_admin || item.membership.is_master_admin)? icons.mdiAccountEdit: icons.mdiAccountEditOutline }}
                  </v-icon>
                </v-btn>
              </template>
              <span>Edit your membership fields</span>
            </v-tooltip>
          </div>
        </template>

      </v-data-table>
    </v-card>
    <profile-organization-form-dialog ref="formDialogRef"
                                     @save-successed="loadRecords(1)" @delete-successed="loadRecords(1)">
    </profile-organization-form-dialog>
    <edit-my-orgganization-member-fields-dialog ref="myMemberFieldsDialogRef"></edit-my-orgganization-member-fields-dialog>
  </div>
</template>

<script>
import {
  mdiPlus,
  mdiPencilOutline,
  mdiOfficeBuildingCog,
  mdiBankCheck,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiClose,
  mdiCheck,
  mdiInformationOutline,
  mdiRefresh,
  mdiAccountEditOutline,
  mdiAccountEdit,
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import store from '@/store'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import {avatarText} from "@core/utils/filter";
import ProfileOrganizationFormDialog from "./ProfileOrganizationFormDialog";
import EventBus from "@/EventBus";
import EditMyOrgganizationMemberFieldsDialog from "@/views/dashboard/memberProfile/EditMyOrgganizationMemberFieldsDialog";

export default {
  components: {EditMyOrgganizationMemberFieldsDialog, ProfileOrganizationFormDialog},
  setup() {
    const membershipRequests = ref([]);
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const reviewingMembership = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({managed_by_me: false});
    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'NAME', value: 'name'},
      {text: 'TYPE', value: 'type'},
      {text: 'EXPIRY', value: 'expiry', sortable: false},
      {text: 'ACTIONS', value: 'actions', align: 'end', sortable: false, cellClass: 'actions-td'},
    ];

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({my: true}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      loading.value = true;
      axios.get("cycling_org/organization/my_orgs", {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const setRegionalDefault = (orgId) => {
      axios.put("account/me/prefs", {default_regional_org: orgId}).then((response) => {
        store.state.currentUser.prefs = response.data;
        notifySuccess("Default regional organization changed!");
      }, (response) => {
        notifyDefaultServerError(response, true);
      });
    };

    const loadMebershipRequests = () => {
      axios.get("cycling_org/organization/my_membership_requests/", {params: {page_size: 5}}).then((response) => {
        membershipRequests.value = response.data.results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const reviewMembershipRequest = (record, action) => {
      reviewingMembership.value = true;
      axios.post(`cycling_org/organization/my_membership_requests/${record.id}/${action}`).then((response) => {
        reviewingMembership.value = false;
        notifySuccess(`Membershipt ${action}ed for "${record._organization.name}"`);
        loadMebershipRequests();
        loadRecords(1);
      }, (error) => {
        reviewingMembership.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    watch(() => tableFiltering, (currentValue, oldValue) => {
        loadRecords(1);
      },
      { deep: true }
    );

    onMounted(() => {
      loadMebershipRequests();
    });

    return {
      membershipRequests,
      records,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      reviewingMembership,
      pagination,
      avatarText,
      loadRecords,
      loadMebershipRequests,
      reviewMembershipRequest,
      setRegionalDefault,
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiOfficeBuildingCog,
        mdiBankCheck,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiClose,
        mdiCheck,
        mdiInformationOutline,
        mdiRefresh,
        mdiAccountEditOutline,
        mdiAccountEdit,
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
  .v-data-table tr td .v-btn.set-default {
    display: none;
  }
  .v-data-table tr:hover td .v-btn.set-default {
    display: inline-flex;
  }
  td.actions-td {
    width: 185px;
  }
}
</style>
