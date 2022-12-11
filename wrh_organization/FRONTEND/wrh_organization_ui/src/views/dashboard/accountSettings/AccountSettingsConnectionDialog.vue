<template>
  <v-dialog v-model="isVisible" persistent width="500">
    <v-card>
      <v-card-title class="headline">
        {{ title }} Account
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-col cols="12">
            <v-text-field v-model="socialRecords[name]" :label="`${title} Link`" clearable
                          :prepend-icon="icons.mdiLinkVariant"></v-text-field>
          </v-col>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" outlined @click="hide()">Cancel</v-btn>
          <v-btn type="submit" color="success" :loading="saving">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref } from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import { mdiLinkVariant } from '@mdi/js';

export default {
  setup(props, context) {
    const isVisible = ref(false);
    const saving = ref(false);
    const socialRecords = ref({});
    const name = ref(null);
    const title = ref(null);

    const hide = () => {
      isVisible.value = false;
    };
    const show = (record, _name, _title) => {
      socialRecords.value = Object.assign({}, record);
      name.value = _name;
      title.value = _title;
      saving.value = false;
      isVisible.value = true;
    };

    const save = () => {
      saving.value = true;
      axios.patch("cycling_org/member/me", {social_media: socialRecords.value}).then((response) => {
        saving.value = false;
        notifySuccess("record saved successfully.");
        context.emit('save-successed');
        hide();
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isVisible,
      saving,
      socialRecords,
      name,
      title,
      show,
      hide,
      save,
      icons: {
        mdiLinkVariant
      }
    }
  },
}
</script>

