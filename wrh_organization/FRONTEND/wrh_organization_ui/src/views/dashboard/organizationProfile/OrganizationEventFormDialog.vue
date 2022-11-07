<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="700px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Event #${record.id}`: 'New Event'}}</span>
      </v-card-title>
      <v-card-text class="d-flex">
        <v-avatar rounded size="80" class="me-6 v-avatar-light-bg" color="grey">
          <v-img :src="logoChosenFileData || record.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
        </v-avatar>

        <!-- upload photo -->
        <div>
          <v-btn small color="primary" class="me-3 mt-5" @click="logoImageRef.click()">
            <v-icon class="d-sm-none">
              {{ icons.mdiCloudUploadOutline }}
            </v-icon>
            <span class="d-none d-sm-block">Choose Logo</span>
          </v-btn>

          <input
            ref="logoImageRef"
            type="file"
            accept=".jpeg,.png,.jpg,GIF"
            :hidden="true"
            @change="onChangeLogoFile"
          />

          <v-btn
              small color="warning" outlined class="mt-5 mr-2" @click="clearChosenLogo()" :disabled="!logoChosenFile">
            Reset
          </v-btn>
          <v-btn small color="error" outlined class="mt-5 mr-2" @click="clearChosenLogo(); record.logo=null">
            Delete
          </v-btn>

          <p class="text-sm mt-5">
            Allowed JPG, GIF or PNG. Max size of 2MB
          </p>
        </div>
      </v-card-text>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="record.name" label="Name" dense outlined hide-details></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="record.description" label="Description" dense outlined hide-details rows="3"></v-textarea>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu v-model="startDateMenu" :close-on-content-click="false"
                    :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field class="pt-0 pb-0" v-model="record.start_date" label="Start Date"
                                  v-bind="attrs" v-on="on" readonly dense outlined hide-details>
                    </v-text-field>
                  </template>
                  <v-date-picker v-model="record.start_date" color="primary" @input="startDateMenu = false">
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu v-model="endDateMenu" :close-on-content-click="false"
                    :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field class="pt-0 pb-0" v-model="record.end_date" label="Exp Date"
                                  v-bind="attrs" v-on="on" readonly dense outlined hide-details>
                    </v-text-field>
                  </template>
                  <v-date-picker v-model="record.end_date" color="primary" @input="endDateMenu = false">
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="record.website" dense outlined hide-details label="Website"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="record.registration_website" dense outlined hide-details label="Registration Website"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-combobox v-model="record.tags" :items="$const.EVENT_TAGS_PREDEFINED" dense outlined hide-details label="Tags" clearable multiple small-chips deletable-chips></v-combobox>
              </v-col>
              <v-col cols="12" md="4">
                <v-autocomplete v-model="record.country" dense outlined hide-details label="Country" :items="$const.COUNTRY_OPTIONS"
                                item-text="name" item-value="code"></v-autocomplete>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="record.state" dense outlined hide-details label="State"></v-text-field>
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field v-model="record.city" dense outlined hide-details label="City"></v-text-field>
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
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const startDateMenu = ref(false);
    const endDateMenu = ref(false);
    const logoChosenFile = ref(null);
    const logoChosenFileData = ref(null);
    const logoImageRef = ref(null);
    const isEditMode = computed(() => !!record.value.id);

    const clearChosenLogo = () => {
      logoChosenFile.value = null;
      logoChosenFileData.value = null;
      logoImageRef.value = null;
    };

    const onChangeLogoFile = (event) => {
      if (event.target.files.length > 0) {
        logoChosenFile.value = event.target.files[0];
        var f = logoChosenFile.value,
          r = new FileReader();
        r.onloadend = (e) => {
          logoChosenFileData.value = e.target.result;
        };
        r.readAsDataURL(f);
      }
    };

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`bycing_org/event/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Event #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      var data = Object.assign({country: "US", state: "Colorado"}, record.value);
      var url = "bycing_org/event",
          httpMethod = axios.post,
          successMsg = "Event added successfully.";
      if (isEditMode.value) {
        url = `bycing_org/event/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Event updated successfully."
      } else {
        data.organization = props.organization.id;
      }
      if (logoChosenFileData.value) {
        data.logo = logoChosenFileData.value;
      } else if (data.logo !== null) {
        delete data.logo;
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
      record.value = Object.assign({country: "US", state: "Colorado"}, r);
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      isVisible.value = true;
      clearChosenLogo();
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      record,
      saving,
      deleting,
      deleteRecord,
      clearChosenLogo,
      logoChosenFile,
      logoChosenFileData,
      logoImageRef,
      onChangeLogoFile,
      hide,
      show,
      save,
      startDateMenu,
      endDateMenu,
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
