<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Member-Org of Organization: #${record.id}`: 'Add Member-Org to Organization'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-menu
                  v-if="isEditMode"
                  bottom
                  right
                  transition="scale-transition"
                  origin="top left"
                >
                  <template v-slot:activator="{ on }">
                    <v-chip pill v-on="on">
                      <v-avatar left>
                        <v-img :src="record._member_org.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
                      </v-avatar>
                      {{ record._member_org.name }}
                    </v-chip>
                  </template>
                  <v-card width="300">
                    <v-list dark>
                      <v-list-item>
                        <v-list-item-avatar>
                          <v-img :src="record._member_org.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>
                            {{ record._member_org.name }}
                          </v-list-item-title>
                        </v-list-item-content>
                        <v-chip small :color="($const.ORGANIZATION_TYPE_MAP[record._member_org.type] || {}).css">
                          {{($const.ORGANIZATION_TYPE_MAP[record._member_org.type] || {}).title || record._member_org.type}}
                        </v-chip>
                      </v-list-item>
                    </v-list>
                    <v-list dense class="member-org-info-list">
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Website</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.website || '[NO WEBSITE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>E-Mail</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.email || '[NO E-MAIL]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Phone</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.phone? $utils.formatPhone(record._member_org.phone): '[NO PHONE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Country</v-list-item-subtitle>
                          <v-list-item-title v-text="($const.COUNTRY_MAP[record._member_org.country] || {}).name || record._member_org.country || '[NO COUNTRY]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>City</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.city || '[NO CITY]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>State</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.state || '[NO STATE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Zipcode</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.zipcode || '[NO ZIPCODE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Address1</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member_org.address || '[NO ADDRESS]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-card>
                </v-menu>
                <v-autocomplete
                    v-else
                    v-model="record._member_org"
                    :search-input.sync="memberOrgSearchInput"
                    :loading="findingMemberOrgs"
                    :items="memberOrgs"
                    no-data-text="Enter part of organization name."
                    chips
                    hide-details
                    label="Member Org"
                    item-text="name"
                    item-value="id"
                    :menu-props="{contentClass:'list-style'}"
                    return-object
                >
                  <template #selection="data">
                    <v-chip
                        v-bind="data.attrs"
                        :input-value="data.selected"
                        close
                        @click="data.select"
                        @click:close="record._member_org = null"
                    >
                      <v-avatar left>
                        <v-img :src="data.item.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
                      </v-avatar>
                      <div class="d-flex flex-column ms-3">
                        <span class="d-block text--success font-weight-semibold text-truncate">
                          {{ data.item.name }}
                        </span>
                        <span class="text-xs">{{ data.item.website || '[NO WEBSITE]' }}</span>
                      </div>
                    </v-chip>
                  </template>

                  <template #item="data">
                    <template>
                      <v-list-item-avatar>
                        <v-img :src="data.item.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
                      </v-list-item-avatar>

                      <v-list-item-content>
                        <v-list-item-title>
                          {{ data.item.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                          {{ data.item.website || '[NO WEBSITE]' }}
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </template>
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu v-model="startDateMenu" :close-on-content-click="false"
                    :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field class="pt-0 pb-0" v-model="record.start_date" label="Start Date"
                                  :prepend-icon="icons.mdiCalendar" v-bind="attrs" v-on="on" readonly>
                    </v-text-field>
                  </template>
                  <v-date-picker v-model="record.start_date" color="primary" @input="startDateMenu = false">
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu v-model="expDateMenu" :close-on-content-click="false"
                    :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field class="pt-0 pb-0" v-model="record.exp_date" label="Exp Date"
                                  :prepend-icon="icons.mdiCalendar" v-bind="attrs" v-on="on" readonly>
                    </v-text-field>
                  </template>
                  <v-date-picker v-model="record.exp_date" color="primary" @input="expDateMenu = false">
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch v-model="record.is_active" label="Is Active?" color="primary" hide-details></v-switch>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-text v-if="confirmDelete">
          <v-alert type="warning" dense text :icon="icons.mdiAlert">
            <p>If you delete this member-org, all related records will be deleted! Are you sure?</p>
            <v-btn color="error" outlined small :loading="deleting" @click="deleteRecord()">Yes, Delete It</v-btn>
            <v-btn color="secondary" @click="confirmDelete=false" small text class="ml-1">Cancel</v-btn>
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <template v-if="isEditMode" >
            <v-btn color="error" outlined @click="confirmDelete=true" :disabled="confirmDelete">
              <v-icon>{{icons.mdiDelete}}</v-icon>Delete
            </v-btn>
          </template>
          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
          <v-btn color="primary" type="submit" :loading="saving">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {
  mdiPencilOutline,
  mdiPlus,
  mdiDelete,
  mdiAlert,
  mdiCalendar,
  mdiAccountCheck,
  mdiAccountCancel,
} from '@mdi/js'
import _ from 'lodash';
import {ref, computed, watch} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const record = ref({});
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const findingMemberOrgs = ref(false);
    const startDateMenu = ref(false);
    const expDateMenu = ref(false);
    const memberOrgs = ref([]);
    const memberOrgSearchInput = ref('');

    watch(memberOrgSearchInput, () => {
      findMemberOrgsDebounce(memberOrgSearchInput.value);
    });

    const isEditMode = computed(() => !!record.value.id);

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`cycling_org/organization/${props.organization.id}/member_orgs/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Member-Org deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      if (!record.value._member_org) {
        return;
      }
      var data = Object.assign({}, record.value);
      data.member_org = data._member_org.id;
      delete data._member_org;
      saving.value = true;
      var url = `cycling_org/organization/${props.organization.id}/member_orgs`,
          httpMethod = axios.post,
          successMsg = "Member-Org added successfully.";
      if (isEditMode.value) {
        url = `${url}/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Member-Org updated successfully."
      }
      httpMethod(url, data).then((response) => {
        saving.value = false;
        notifySuccess(successMsg);
        hide();
        context.emit('save-successed', response.data);
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const findMemberOrgs = (search) => {
      if (findingMemberOrgs.value || (search || '').length < 3) {
        memberOrgs.value = [];
        return;
      }
      findingMemberOrgs.value = true;
      axios.get("cycling_org/organization/find", {params: {search: search}}).then((response) => {
        findingMemberOrgs.value = false;
        memberOrgs.value = response.data.results;
      }, (error) => {
        findingMemberOrgs.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findMemberOrgsDebounce = _.debounce(findMemberOrgs, 500);

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r) => {
      record.value = Object.assign({is_active: true}, r);
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      record,
      saving,
      deleting,
      deleteRecord,
      hide,
      show,
      save,
      findingMemberOrgs,
      findMemberOrgs,
      findMemberOrgsDebounce,
      memberOrgs,
      memberOrgSearchInput,
      startDateMenu,
      expDateMenu,
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiDelete,
        mdiAlert,
        mdiCalendar,
        mdiAccountCheck,
        mdiAccountCancel,
      },
    }
  },
}
</script>
<style scoped>
.member-org-info-list .v-list-item {
  margin-bottom: 15px;
  margin-top: 15px;
}
</style>
