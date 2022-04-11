<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="700px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Member of Organization: #${record.id}`: 'Add Member to Organization'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save" v-model="formValid">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
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
                      <v-icon>{{record._member._user.id? icons.mdiAccountCheck: icons.mdiAccountCancel}}</v-icon>
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
                          <v-list-item-title>
                            <v-icon>{{record._member._user.id? icons.mdiAccountCheck: icons.mdiAccountCancel}}</v-icon>
                            {{ `${record._member.first_name} ${record._member.last_name}` }}
                          </v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                    <v-list dense class="member-info-list">
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>E-Mail</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.email || '[NO E-MAIL]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Phone</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.phone? $utils.formatPhone(record._member.phone): '[NO PHONE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Weight(kg)</v-list-item-subtitle>
                          <v-list-item-title v-text="$utils.removeTrailingZero(record._member.weight) || '[NO WEIGHT]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Height(m)</v-list-item-subtitle>
                          <v-list-item-title v-text="$utils.removeTrailingZero(record._member.height) || '[NO HEIGHT]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Country</v-list-item-subtitle>
                          <v-list-item-title v-text="($const.COUNTRY_MAP[record._member.country] || {}).name || record._member.country || '[NO COUNTRY]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>City</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.city || '[NO CITY]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>State</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.state || '[NO STATE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Zipcode</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.zipcode || '[NO ZIPCODE]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-subtitle>Address1</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.address1 || '[NO ADDRESS1]'"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item v-if="record._member.address2">
                        <v-list-item-content>
                          <v-list-item-subtitle>Address2</v-list-item-subtitle>
                          <v-list-item-title v-text="record._member.address2 || '[NO ADDRESS2]'"></v-list-item-title>
                        </v-list-item-content>
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
                    dense
                    :rules="[rules.required]"
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
                <v-text-field v-model="record.org_member_uid" label="Member UID" dense hide-details></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu v-model="startDateMenu" :close-on-content-click="false"
                    :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field class="pt-0 pb-0" v-model="record.start_date" label="Start Date" hide-details
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
                    <v-text-field class="pt-0 pb-0" v-model="record.exp_date" label="Exp Date" hide-details
                                  :prepend-icon="icons.mdiCalendar" v-bind="attrs" v-on="on" readonly>
                    </v-text-field>
                  </template>
                  <v-date-picker v-model="record.exp_date" color="primary" @input="expDateMenu = false">
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch v-model="record.is_admin" label="Is Admin?" color="primary" hide-details></v-switch>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch v-model="record.is_active" label="Is Active?" color="primary" hide-details></v-switch>
              </v-col>
            </v-row>
          </v-container>
          <app-card-actions action-collapse outlined v-if="schema && schema.length">
            <template #title>
              <span class="warning--text">Extra Organization Fields</span>
            </template>
            <v-card-text class="pr-2 pl-2">
              <v-container>
                <v-row>
                  <v-col cols="12" :md="f.type == 'text' || (f.choices && f.choices.length > 0)? 12: 6"
                         v-for="f in schema" :key="f.name">
                    <template v-if="f.choices && f.choices.length > 0">
                      <p class="caption mb-0">{{f.title}}</p>
                      <div v-if="f.multiple" class="d-flex flex-wrap demo-space-x mt-0">
                        <v-checkbox v-for="(c, cIdx) in f.choices" v-model="record.member_fields[f.name]"
                                    class="mt-0 mb-0 pt-0" :label="c.title" :value="c.value" :key="cIdx" hide-details></v-checkbox>
                      </div>
                      <v-radio-group v-else v-model="record.member_fields[f.name]" hide-details class="mt-0"
                                     :rules="f.required? [rules.required]: []">
                        <div class="d-flex flex-wrap demo-space-x mt-0">
                          <v-radio v-for="(c, cIdx) in f.choices" :label="c.title" :value="c.value" :key="cIdx"
                                   class="mt-0 mb-0 pt-0"></v-radio>
                        </div>
                      </v-radio-group>
                    </template>
                    <template v-else-if="f.type=='integer' || f.type=='float' || f.type=='number'">
                      <v-text-field
                          hide-details
                          dense
                          v-model.number="record.member_fields[f.name]"
                          :label="f.title"
                          type="number"
                          :step="f.type=='integer'? 1: 'any'"
                          :rules="f.required? [rules.required]: []"
                      ></v-text-field>
                    </template>
                    <template v-else-if="f.type=='percent'">
                      <v-text-field
                          hide-details
                          dense
                          v-model.number="record.member_fields[f.name]"
                          :label="f.title"
                          :rules="f.required? [rules.required]: []"
                          type="number"
                          suffix="%"
                          min="0"
                          max="100"
                      ></v-text-field>
                    </template>
                    <template v-else-if="f.type=='boolean'">
                      <v-switch
                          hide-details
                          v-model="record.member_fields[f.name]"
                          :label="f.title"
                          dense
                          class="pt-0 mt-1"
                      ></v-switch>
                    </template>
                    <template v-else-if="f.type=='date' || f.type=='time'">
                      <v-menu v-model="uiFieldsData[`menu__${f.name}`]" :close-on-content-click="false"
                              :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                        <template v-slot:activator="{ on, attrs }">
                          <v-text-field
                              hide-details
                              v-model="record.member_fields[f.name]"
                              :label="f.title"
                              :rules="f.required? [rules.required]: []"
                              class="pt-0 mt-0 mb-5"
                              :append-icon="f.type=='time'? icons.mdiClockOutline: icons.mdiCalendar"
                              v-bind="attrs"
                              v-on="on"
                              readonly>
                          </v-text-field>
                        </template>
                        <v-time-picker v-if="f.type=='time'" v-model="record.member_fields[f.name]" color="primary"
                                       @click:minute="uiFieldsData[`menu__${f.name}`] = false"></v-time-picker>
                        <v-date-picker v-else v-model="record.member_fields[f.name]" color="primary"
                                       @input="uiFieldsData[`menu__${f.name}`] = false"></v-date-picker>
                      </v-menu>
                    </template>
                    <template v-else-if="f.type=='datetime'">
                      <v-datetime-picker v-model="record.member_fields[f.name]" :label="f.title"
                                         :text-field-props="{appendIcon: icons.mdiCalendar, class: 'pt-0 mt-0 mb-5', rules: f.required? [rules.required]: []}">
                        <template #dateIcon>
                          <v-icon>{{icons.mdiCalendar}}</v-icon>
                        </template>
                        <template #timeIcon>
                          <v-icon>{{icons.mdiClock}}</v-icon>
                        </template>
                      </v-datetime-picker>
                    </template>
                    <template v-else-if="f.type=='text'">
                      <v-textarea
                          hide-details
                          dense
                          v-model="record.member_fields[f.name]"
                          :label="f.title"
                          :rules="f.required? [rules.required]: []"
                          rows="2"
                      ></v-textarea>
                    </template>
                    <template v-else>
                      <v-text-field
                          dense
                          v-model.trim="record.member_fields[f.name]"
                          :label="f.title"
                          :rules="f.required? [rules.required]: []"
                          type="text"
                      ></v-text-field>
                    </template>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
          </app-card-actions>
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
          <v-btn color="primary" type="submit" :loading="saving" :disabled="!formValid">Save</v-btn>
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
  mdiClock,
  mdiClockOutline,
  mdiAccountCheck,
  mdiAccountCancel,
  mdiPhoneOutline,
  mdiEmailOutline,
  mdiEarth,
  mdiHomeCity,
  mdiHomeCityOutline

} from '@mdi/js'
import _ from 'lodash';
import {ref, computed, watch, set} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import AppCardActions from "@core/components/app-card-actions/AppCardActions";
import {required} from "@core/utils/validation";
import moment from "moment";

export default {
  components: {AppCardActions},
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const formValid = ref(false);
    const uiFieldsData = ref({});
    const record = ref({member_fields: {}});
    const schema = ref(null);
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const findingMembers = ref(false);
    const startDateMenu = ref(false);
    const expDateMenu = ref(false);
    const members = ref([]);
    const memberSearchInput = ref('');

    watch(memberSearchInput, () => {
      findMembersDebounce(memberSearchInput.value);
    });

    const isEditMode = computed(() => !!record.value.id);

    const loadSchema = () => {
      let params = {exfields: "member_fields_schema", fields: "member_fields_schema"};
      axios.get(`bycing_org/organization/${props.organization.id}`, {params: params}).then((response) => {
        schema.value = response.data.member_fields_schema || [];
        schema.value.forEach(r => {
          if (r.multiple && !Array.isArray(record.value.member_fields[r.name])) {
            set(record.value.member_fields, r.name, []);
          }
          if (r.type === 'datetime' && record.value.member_fields[r.name]) {
            record.value.member_fields[r.name] = moment(record.value.member_fields[r.name]).toDate();
          }
        });

      }, (error) => {
        notifyDefaultServerError(error, true);
      });

    };

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
      data.member_fields = Object.assign({}, record.value.member_fields);
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
        notifySuccess(successMsg);
        hide();
        context.emit('save-successed', response.data);
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
      loadSchema();
      uiFieldsData.value = {};
      record.value = Object.assign({is_active: true}, r);
      record.value.member_fields = Object.assign({}, record.value.member_fields);
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
    };

    return {
      isVisible,
      formValid,
      confirmDelete,
      isEditMode,
      record,
      uiFieldsData,
      schema,
      saving,
      deleting,
      deleteRecord,
      hide,
      show,
      save,
      loadSchema,
      findingMembers,
      findMembers,
      findMembersDebounce,
      members,
      memberSearchInput,
      startDateMenu,
      expDateMenu,
      rules: {
        required
      },
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiDelete,
        mdiAlert,
        mdiCalendar,
        mdiClock,
        mdiClockOutline,
        mdiAccountCheck,
        mdiAccountCancel,
        mdiPhoneOutline,
        mdiEmailOutline,
        mdiEarth,
        mdiHomeCity,
        mdiHomeCityOutline,
      },
    }
  },
}
</script>

<style scoped>
.member-info-list .v-list-item {
  margin-bottom: 15px;
  margin-top: 15px;
}
</style>
