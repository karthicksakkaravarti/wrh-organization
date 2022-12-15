<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="800px"
  >
    <v-card class="profile-org-form">
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Organization #${record.id}`: 'New Organization'}}</span>
      </v-card-title>
      <v-tabs class="mb-5" v-model="tab">
        <v-tab>Basic Info</v-tab>
        <v-tab :disabled="!isEditMode">UI Preferences</v-tab>
        <v-tab-item class="pt-6">
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
                Allowed JPG, GIF or PNG. Max size of 10MB
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
                  <v-col cols="12" md="6">
                    <v-select v-model="record.type" :items="$const.ORGANIZATION_TYPE_OPTIONS"
                              item-text="title" item-value="value" label="Type" dense>
                    </v-select>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.website" label="Website" dense></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.email" label="E-mail" dense :rules="[rules.emailValidator]"></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.phone" v-mask="phoneMask" dense label="Phone"></v-text-field>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-autocomplete v-model="record.country" dense label="Country" :items="$const.COUNTRY_OPTIONS"
                                    item-text="name" item-value="code"></v-autocomplete>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.state" dense label="State"></v-text-field>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.city" dense label="City"></v-text-field>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field v-model="record.zipcode" dense label="Zipcode"></v-text-field>
                  </v-col>

                  <v-col cols="12">
                    <v-text-field v-model="record.address" dense label="Address"></v-text-field>
                  </v-col>

                  <v-col cols="12">
                    <v-textarea rows="2" v-model="record.about" label="About" dense></v-textarea>
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
            <v-divider></v-divider>
            <v-card-actions class="pt-5">
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
        </v-tab-item>
        <v-tab-item class="pt-6">
          <v-card-text>
            <h3 class="mb-2">Upload site banner image:</h3>
            <v-img
              :src="bannerChosenFileData || prefs.banner_image || require(`@/assets/images/misc/public-banner-bg-light.jpeg`)"
              height="200"
              class="grey darken-4 banner"
              :class="{'no-banner': !bannerChosenFileData && !prefs.banner_image}"
            ></v-img>
            <!-- upload photo -->
            <div>
              <v-btn small color="primary" class="me-3 mt-5" @click="bannerImageRef.click()">
                <v-icon class="d-sm-none">
                  {{ icons.mdiCloudUploadOutline }}
                </v-icon>
                <span class="d-none d-sm-block">Choose Banner</span>
              </v-btn>

              <input
                ref="bannerImageRef"
                type="file"
                accept=".jpeg,.png,.jpg,GIF"
                :hidden="true"
                @change="onChangeBannerFile"
              />

              <v-btn
                  small color="warning" outlined class="mt-5 mr-2" @click="clearChosenBanner()" :disabled="!bannerChosenFile">
                Reset
              </v-btn>
              <v-btn small color="error" outlined class="mt-5 mr-2" @click="clearChosenBanner(); prefs.banner_image=null">
                Delete
              </v-btn>

              <p class="text-sm mt-5">
                Allowed JPG, GIF or PNG. Max size of 10MB
              </p>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <h3 class="mb-2">Home page information board:</h3>
                <ckeditor :editor="editor" v-model="prefs.information_board_content" :config="$const.DEFAULT_CKEDITOR_CONFIG"></ckeditor>
              </v-col>
            </v-row>
          </v-card-text>
          <v-form @submit.prevent="savePrefs">
            <v-divider></v-divider>
            <v-card-actions class="pt-5">
              <v-spacer></v-spacer>
              <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
              <v-btn color="primary" type="submit" :loading="savingPrefs">Save</v-btn>
            </v-card-actions>
          </v-form>
        </v-tab-item>
      </v-tabs>
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
import {internationalPhoneMask, notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import {emailValidator} from "@core/utils/validation";
import {nextTick} from "@vue/composition-api/dist/vue-composition-api";
import CKEditor from '@ckeditor/ckeditor5-vue2';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';

export default {
  components: {
    ckeditor: CKEditor.component
  },
  setup(props, context) {
    const isVisible = ref(false);
    const tab = ref(0);
    const record = ref({});
    const prefs = ref({});
    const saving = ref(false);
    const savingPrefs = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const logoChosenFile = ref(null);
    const logoChosenFileData = ref(null);
    const logoImageRef = ref(null);
    const bannerChosenFile = ref(null);
    const bannerChosenFileData = ref(null);
    const bannerImageRef = ref(null);
    const phoneMask = ref(null);

    const isEditMode = computed(() => !!record.value.id);

    const clearChosenLogo = () => {
      logoChosenFile.value = null;
      logoChosenFileData.value = null;
      if (logoImageRef.value) {
        logoImageRef.value.value = null;
      }
    };

    const clearChosenBanner = () => {
      bannerChosenFile.value = null;
      bannerChosenFileData.value = null;
      if (bannerImageRef.value) {
        bannerImageRef.value.value = null;
      }
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

    const onChangeBannerFile = (event) => {
      if (event.target.files.length > 0) {
        bannerChosenFile.value = event.target.files[0];
        var f = bannerChosenFile.value,
          r = new FileReader();
        r.onloadend = (e) => {
          bannerChosenFileData.value = e.target.result;
        };
        r.readAsDataURL(f);
      }
    };

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`cycling_org/organization/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Organization #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const savePrefs = () => {
      var data = Object.assign({}, prefs.value);
      savingPrefs.value = true;
      if (bannerChosenFileData.value) {
        data.banner_image = bannerChosenFileData.value;
      } else if (data.banner_image !== null) {
        delete data.banner_image;
      }
      axios.patch(`cycling_org/organization/${record.value.id}/prefs`, data).then((response) => {
        savingPrefs.value = false;
        record.value.prefs = prefs.value = response.data;
        notifySuccess('Preferences Saved successfully.');
        hide();
        context.emit('save-successed', record.value);
      }, (error) => {
        savingPrefs.value = false;
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
      var url = "cycling_org/organization",
          httpMethod = axios.post,
          successMsg = "Organization created successfully.";
      if (isEditMode.value) {
        url = `cycling_org/organization/${record.value.id}`;
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

    const loadRecord = () => {
      axios.get(`cycling_org/organization/${record.value.id}`).then((response) => {
        record.value = response.data || {};
        prefs.value = record.value.prefs || {};
      }, (error) => {
        notifyDefaultServerError(error, true);
      });
    };

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r) => {
      tab.value = 0;
      phoneMask.value = null;
      record.value = Object.assign({}, r);
      prefs.value = Object.assign({}, record.value.prefs);
      if (isEditMode.value) {
        loadRecord();
      }
      nextTick(() => {
        phoneMask.value = internationalPhoneMask;
      });
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      savingPrefs.value = false;
      clearChosenLogo();
      clearChosenBanner();
      isVisible.value = true;
    };

    return {
      isVisible,
      tab,
      confirmDelete,
      isEditMode,
      record,
      prefs,
      saving,
      savingPrefs,
      deleting,
      deleteRecord,
      clearChosenLogo,
      clearChosenBanner,
      logoChosenFile,
      logoChosenFileData,
      logoImageRef,
      bannerChosenFile,
      bannerChosenFileData,
      bannerImageRef,
      onChangeLogoFile,
      onChangeBannerFile,
      hide,
      show,
      save,
      savePrefs,
      phoneMask,
      editor: ClassicEditor,
      rules: {
        emailValidator
      },
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

<style lang="scss" scoped>
  .banner {
    border: 1px solid #e9e9e9;
  }
  .banner.no-banner{
    opacity: 0.2;
  }
</style>
<style>
  .profile-org-form .ck-editor .ck-editor__main .ck-content {
    height: 200px;
  }
</style>
