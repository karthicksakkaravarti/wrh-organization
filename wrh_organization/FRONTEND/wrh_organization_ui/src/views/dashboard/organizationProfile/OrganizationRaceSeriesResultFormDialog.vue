<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Race Series Result #${record.id}`: 'New Race Series Result'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" v-if="record._race_series || currentRaceSeries">
                <div>Race Series: <span class="font-weight-semibold">{{(record._race_series || currentRaceSeries).name}}</span></div>
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
                <v-autocomplete
                    v-model="record._category"
                    dense
                    label="Category"
                    :items="categories"
                    item-text="title"
                    item-value="id"
                    return-object
                >
                </v-autocomplete>
              </v-col>

              <v-col cols="12">
                <v-text-field type="number" min="1" step="1" v-model="record.place" dense label="Place"></v-text-field>
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

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const record = ref({more_data: {}});
    const currentRaceSeries = ref(null);
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const findingMembers = ref(false);
    const members = ref([]);
    const memberSearchInput = ref('');
    const categories = ref([]);

    watch(memberSearchInput, () => {
      findMembersDebounce(memberSearchInput.value);
    });

    const isEditMode = computed(() => !!record.value.id);

    const loadCategories = () => {
      var params = {
        organization: props.organization.id,
        page_size: 0
      };
      axios.get("bycing_org/category/", {params: params}).then((response) => {
        categories.value = response.data.results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

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
      axios.delete(`bycing_org/race_series_result/${record.value.id}`).then((response) => {
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
      var url = "bycing_org/race_series_result",
          httpMethod = axios.post,
          successMsg = "Race Series Result added successfully.";
      if (isEditMode.value) {
        url = `bycing_org/race_series_result/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Race Series Result updated successfully."
      } else {
        data.race_series = currentRaceSeries.value.id;
        data.organization = props.organization.id;
      }
      data.category = data._category && data._category.id;
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
      currentRaceSeries.value = race || null;
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
      findMembers();
      loadCategories();
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      record,
      saving,
      deleting,
      findingMembers,
      categories,
      findMembers,
      findMembersDebounce,
      members,
      memberSearchInput,
      deleteRecord,
      hide,
      show,
      save,
      currentRaceSeries,
      icons: {
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>