<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Organization #${record.id}`: 'New Organization'}}</span>
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
                <v-text-field v-model="record.name" label="Name" dense></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-select v-model="record.type" :items="$const.ORGANIZATION_TYPE_OPTIONS"
                          item-text="title" item-value="value" label="Type" dense>
                </v-select>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="record.website" label="Website" dense></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea outlined v-model="record.about" label="About" dense></v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-text v-if="confirmDelete">
          <v-alert type="warning" dense text :icon="icons.mdiAlert">
            <p>If you delete an organization, all related records will be deleted! Are you sure?</p>
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
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiCloudUploadOutline,
  mdiEyeOutline,
  mdiPencilOutline,
  mdiPlus,
  mdiDelete,
  mdiAlert,
} from '@mdi/js'
import {ref, computed} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";

export default {
  setup(props, context) {
    const isVisible = ref(false);
    const record = ref({});
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
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
      axios.delete(`bycing_org/organization/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Organization #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      var data = Object.assign({}, record.value);
      saving.value = true;
      if (logoChosenFileData.value) {
        data.logo = logoChosenFileData.value;
      } else if (data.logo !== null) {
        delete data.logo;
      }
      var url = "bycing_org/organization",
          httpMethod = axios.post,
          successMsg = "Organization created successfully.";
      if (isEditMode.value) {
        url = `bycing_org/organization/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Organization updated successfully."
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

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r) => {
      record.value = Object.assign({}, r);
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      clearChosenLogo();
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
      clearChosenLogo,
      logoChosenFile,
      logoChosenFileData,
      logoImageRef,
      onChangeLogoFile,
      hide,
      show,
      save,
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiEyeOutline,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiCloudUploadOutline,
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>
