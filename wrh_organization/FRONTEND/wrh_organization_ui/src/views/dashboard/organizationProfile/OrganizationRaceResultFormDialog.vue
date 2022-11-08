<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Race Result #${record.id}`: 'New Race Result'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save" class="race-result-form">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" v-if="record._race || currentRace">
                <div>Event: <span class="font-weight-semibold">{{(record._race || currentRace)._event.name}}</span></div>
                <div>Race: <span class="font-weight-semibold">{{(record._race || currentRace).name}}</span></div>
              </v-col>
              <v-col cols="12 pt-0">
                <v-divider></v-divider>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-autocomplete
                    v-model="record._rider"
                    :search-input.sync="memberSearchInput"
                    :loading="findingMembers"
                    :items="members"
                    no-data-text="Enter part of name or email."
                    chips
                    label="Linked Rider"
                    item-text="first_name"
                    item-value="id"
                    :menu-props="{contentClass:'list-style'}"
                    return-object
                    dense
                >
                  <template #selection="data">
                    <v-chip
                        v-bind="data.attrs"
                        :input-value="data.selected"
                        close
                        @click="data.select"
                        @click:close="record._rider = null"
                    >
                      <v-avatar left>
                        <v-img :src="data.item._user.avatar || require('@/assets/images/misc/no-profile.png')"></v-img>
                      </v-avatar>
                      <div class="d-flex flex-column ms-3">
                        <span class="d-block text--success font-weight-semibold text-truncate">
                          {{ `${data.item.first_name} ${data.item.last_name}` }}
                        </span>
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
                <v-text-field v-model="record.more_data.first_name" label="First Name" dense></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="record.more_data.last_name" label="Last Name" dense></v-text-field>
              </v-col>
              <v-col cols="12">
                <div class="d-flex">
                  <v-text-field type="number" min="1" step="1" v-model="record.place" dense label="Place" :disabled="record.finish_status!='ok'">
                  </v-text-field>
                  <v-radio-group v-model="record.finish_status" row dense hide-details class="mt-0 mb-1">
                    <v-radio v-for="o in $const.RACE_FINISH_STATUS_OPTIONS" :label="o.title" :value="o.value" :key="o.value"></v-radio>
                  </v-radio-group>
                </div>
              </v-col>
              <v-col cols="12" v-if="isEditMode">
                <app-card-actions action-collapse flat outlined collapsed color="#f3f3f3" class="more-data-card">
                  <template #title>
                    More Data ...
                  </template>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6" v-for="(item, key) in moreDataFiltered" :key="key">
                        <div class="font-weight-semibold">{{key}}:</div>
                        <div>{{item == null || item == ""? '-': item}}</div>
                      </v-col>
                      <v-col cols="12" v-if="!Object.keys(moreDataFiltered).length">
                        <div class="text-center text-caption">No Extra Fields!</div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </app-card-actions>

              </v-col>
    
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-text v-if="confirmDelete">
          <v-alert type="warning" dense text :icon="icons.mdiAlert">
            <p>If you delete it, all related records will be deleted! Are you sure?</p>
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
  mdiDelete,
  mdiAlert,
} from '@mdi/js'
import {ref, computed} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import {watch} from "@vue/composition-api/dist/vue-composition-api";
import _ from "lodash";
import AppCardActions from "@core/components/app-card-actions/AppCardActions";

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
    const record = ref({more_data: {}});
    const currentRace = ref(null);
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
    const moreDataFiltered = computed(() => {
      const moreData = Object.assign({}, record.value.more_data);
      ['first_name', 'last_name', 'place'].forEach(f => {
        delete moreData[f];
      });
      return moreData;
    });

    const findMembers = (search) => {
      if (findingMembers.value || (search || '').length < 3) {
        members.value = [];
        if (record.value._rider) {
          members.value = [record.value._rider]
        }
        return;
      }
      findingMembers.value = true;
      axios.get("bycing_org/member/find", {params: {search: search}}).then((response) => {
        findingMembers.value = false;
        members.value = response.data.results;
        if (record.value._rider) {
          members.value = [record.value._rider]
        }

      }, (error) => {
        findingMembers.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findMembersDebounce = _.debounce(findMembers, 500);

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`bycing_org/race_result/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Record #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      var data = Object.assign({}, record.value);
      data.rider = data._rider? data._rider.id: null;
      delete data._rider;
      var url = "bycing_org/race_result",
          httpMethod = axios.post,
          successMsg = "Race Result added successfully.";
      if (isEditMode.value) {
        url = `bycing_org/race_result/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Race Result updated successfully."
      } else {
        data.race = currentRace.value.id;
        data.organization = props.organization.id;
      }
      saving.value = true;
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

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r, race) => {
      record.value = Object.assign({more_data: {}}, r);
      currentRace.value = race || null;
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
      findMembers();
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      moreDataFiltered,
      record,
      saving,
      deleting,
      findingMembers,
      findMembers,
      findMembersDebounce,
      members,
      memberSearchInput,
      deleteRecord,
      hide,
      show,
      save,
      currentRace,
      icons: {
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>

<style lang="scss">
.race-result-form {
  .more-data-card {
    .v-card__title {
      padding-top: 10px !important;
      padding-bottom: 10px !important;
    }
  }
}
</style>
