<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Race #${record.id}`: 'New Race'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" v-if="record._event || currentEvent">
                <div>Event: <span class="font-weight-semibold">{{(record._event || currentEvent).name}}</span></div>
              </v-col>
              <v-col cols="12 pt-0">
                <v-divider></v-divider>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="record.name" label="Race Name" dense></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-datetime-picker v-model="record.start_datetime" label="Start Date/Time">
                  <template #dateIcon>
                    <v-icon>{{icons.mdiCalendar}}</v-icon>
                  </template>
                  <template #timeIcon>
                    <v-icon>{{icons.mdiClock}}</v-icon>
                  </template>
                </v-datetime-picker>
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
  mdiCalendar,
  mdiClock
} from '@mdi/js'
import {ref, computed} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import {watch} from "@vue/composition-api/dist/vue-composition-api";
import _ from "lodash";
import moment from "moment";

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
    const currentEvent = ref(null);
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const isEditMode = computed(() => !!record.value.id);

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`bycing_org/race/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Race #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      var data = Object.assign({}, record.value);
      var url = "bycing_org/race",
          httpMethod = axios.post,
          successMsg = "Race added successfully.";
      if (isEditMode.value) {
        url = `bycing_org/race/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Race updated successfully."
      } else {
        data.event = currentEvent.value.id;
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
    const show = (r, event) => {
      record.value = Object.assign({}, r);
      currentEvent.value = event || null;
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
      if (record.value.start_datetime) {
        record.value.start_datetime = moment(record.value.start_datetime).toDate()
      }
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
      currentEvent,
      icons: {
        mdiDelete,
        mdiAlert,
        mdiCalendar,
        mdiClock
      },
    }
  },
}
</script>
