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
              <template v-if="isEditMode">
                <v-col cols="12">
                  <div class="d-flex align-center">
                    <span class="mr-2">Rider: </span>
                    <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
                      <v-img v-if="record._race_result._rider && record._race_result._rider._user.avatar" :src="record._race_result._rider._user.avatar"></v-img>
                      <span v-else class="font-weight-medium">
                        {{ avatarText(record._race_result._rider? record._race_result._rider.first_name: (record._race_result.more_data.first_name || 'N/A')) }}
                      </span>
                    </v-avatar>

                    <div class="d-flex flex-column pl-1">
                      <span href="javascript:" class="font-weight-semibold text-truncate text-decoration-none">
                        <v-icon v-if="record._race_result._rider" small>{{icons.mdiAccountCheck}}</v-icon> {{ displayRiderName(record) }}
                      </span>
                    </div>
                  </div>
                </v-col>
                <v-col cols="12 pt-0">
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12">
                  <div class="d-flex">
                    <span class="mr-2">Race: </span>
                    <div class="d-flex flex-column">
                      <span class="font-weight-semibold text-truncate">
                        {{record._race_result._race.name}}
                      </span>
                      <span class="text-xs text-truncate">
                        {{record._race_result._race._event.name}}
                      </span>
                    </div>
                  </div>
                </v-col>
                <v-col cols="12 pt-0">
                  <v-divider></v-divider>
                </v-col>
              </template>

            </v-row>
            <v-row>
              <v-col cols="12" v-if="!isEditMode">
                <v-text-field type="number" v-model="record.race_result" label="Race-Result ID" dense></v-text-field>
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
import {avatarText} from "@core/utils/filter";

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
    const categories = ref([]);

    const isEditMode = computed(() => !!record.value.id);

    const loadCategories = () => {
      var params = {
        organization: props.organization.id,
        page_size: 0
      };
      axios.get("cycling_org/category/", {params: params}).then((response) => {
        categories.value = response.data.results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`cycling_org/race_series_result/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Record #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const displayRiderName = (r) => {
      var name = '';
      if (r._race_result._rider) {
        name = `${r._race_result._rider.first_name} ${r._race_result._rider.last_name}`.trim();
      } else {
        name = `${r._race_result.more_data.first_name || ''} ${r._race_result.more_data.last_name || ''}`.trim();
      }
      return name || 'N/A'
    };

    const save = () => {
      var data = Object.assign({}, record.value);
      data.rider = data._rider? data._rider.id: null;
      delete data._rider;
      var url = "cycling_org/race_series_result",
          httpMethod = axios.post,
          successMsg = "Race Series Result added successfully.";
      if (isEditMode.value) {
        url = `cycling_org/race_series_result/${record.value.id}`;
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
      loadCategories();
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      record,
      saving,
      deleting,
      categories,
      deleteRecord,
      hide,
      show,
      save,
      avatarText,
      currentRaceSeries,
      displayRiderName,
      icons: {
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>
