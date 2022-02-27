<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Member of Organization: #${record.id}`: 'Add Member to Organization'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text class="mb-1">
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
                      <v-img :src="record._member._user.avatar || require('@/assets/images/misc/no-profile.png')"></v-img>
                    </v-avatar>
                    {{ `${record._member.first_name} ${record._member.last_name}` }}
                  </v-chip>
                </template>
                <v-card width="300">
                  <v-list dark>
                    <v-list-item>
                      <v-list-item-avatar>
                        <v-img :src="record._member._user.avatar || require('@/assets/images/misc/no-profile.png')"></v-img>
                      </v-list-item-avatar>
                      <v-list-item-content>
                        <v-list-item-title>{{ `${record._member.first_name} ${record._member.last_name}` }}</v-list-item-title>

                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                  <v-list>
                    <v-list-item>
                      <v-list-item-title>
                        <v-chip small class="v-chip-light-bg">
                          {{($const.GENDER_MAP[record._member.gender] || {}).title || record._member.gender}}
                        </v-chip>
                        {{record._member.email || '[NO E-MAIL]'}}
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-card>
              </v-menu>
              <v-autocomplete
                  v-else
                  v-model="record._member"
                  :search-input.sync="memberSearchInput"
                  :loading="findingMembers"
                  :items="members"
                  no-data-text="Enter part of name or email."
                  chips
                  hide-details
                  label="Member"
                  item-text="first_name"
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
                      @click:close="record._member = null"
                  >
                    <v-avatar left>
                      <v-img :src="data.item._user.avatar || require('@/assets/images/misc/no-profile.png')"></v-img>
                    </v-avatar>
                    <div class="d-flex flex-column ms-3">
                      <span class="d-block text--success font-weight-semibold text-truncate">
                        {{ `${data.item.first_name} ${data.item.last_name}` }}
                      </span>
                      <span class="text-xs">{{ data.item.email || '[NO E-MAIL]' }}</span>
                    </div>
                  </v-chip>
                </template>

                <template #item="data">
                  <template>
                    <v-list-item-avatar>
                      <v-img :src="data.item._user.avatar || require('@/assets/images/misc/no-profile.png')"></v-img>
                    </v-list-item-avatar>

                    <v-list-item-content>
                      <v-list-item-title>
                        {{ `${data.item.first_name} ${data.item.last_name}` }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{ data.item.email || '[NO E-MAIL]' }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </template>
                </template>
              </v-autocomplete>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch v-model="record.is_admin" label="Is Admin?" color="primary" hide-details></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch v-model="record.is_active" label="Is Active?" color="primary" hide-details></v-switch>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-text v-if="confirmDelete">
          <v-alert type="warning" dense text :icon="icons.mdiAlert">
            <p>If you delete this member, all related records will be deleted! Are you sure?</p>
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
    const findingMembers = ref(false);
    const members = ref([]);
    const memberSearchInput = ref('');

    watch(memberSearchInput, () => {
      findMembersDebounce(memberSearchInput.value);
    });

    const isEditMode = computed(() => !!record.value.id);

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`bycing_org/organization/${props.organization.id}/members/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Member deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      if (!record.value._member) {
        return;
      }
      var data = Object.assign({}, record.value);
      data.member = data._member.id;
      delete data._member;
      saving.value = true;
      var url = `bycing_org/organization/${props.organization.id}/members`,
          httpMethod = axios.post,
          successMsg = "Member added successfully.";
      if (isEditMode.value) {
        url = `${url}/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Member updated successfully."
      }
      httpMethod(url, data).then((response) => {
        saving.value = false;
        record.value = response.data;
        notifySuccess(successMsg);
        hide();
        context.emit('save-successed', record.value);
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const findMembers = (search) => {
      if (findingMembers.value || (search || '').length < 3) {
        members.value = [];
        return;
      }
      findingMembers.value = true;
      axios.get("bycing_org/member/find", {params: {search: search}}).then((response) => {
        findingMembers.value = false;
        members.value = response.data.results;
      }, (error) => {
        findingMembers.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findMembersDebounce = _.debounce(findMembers, 500);

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r) => {
      record.value = Object.assign({}, r);
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
      findingMembers,
      findMembers,
      findMembersDebounce,
      members,
      memberSearchInput,
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>
