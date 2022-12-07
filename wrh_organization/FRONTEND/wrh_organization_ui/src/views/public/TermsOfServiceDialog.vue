<template>
  <v-dialog v-model="isVisible" max-width="800px">
    <v-card>
      <v-card-title class="headline">
        Terms of Service
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <div v-html="termsOfService || ''"></div>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error" outlined @click="hide()">Close</v-btn>
      </v-card-actions>
    </v-card>
    <v-overlay :value="loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </v-dialog>
</template>

<script>
import {ref, watch} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess, notifyWarn} from "@/composables/utils";
import { mdiLinkVariant, mdiAlertOutline, mdiLogin, mdiClose } from '@mdi/js';
import {required} from "@core/utils/validation";
import { StripeElementCard } from '@vue-stripe/vue-stripe';

export default {
  props: {
  },
  setup(props, context) {
    const termsOfService = ref(null);
    const isVisible = ref(false);
    const loading = ref(false);

    const hide = () => {
      isVisible.value = false;
    };
    const show = () => {
      loadTermsOfService();
      isVisible.value = true;
    };

    const loadTermsOfService = () => {
      loading.value = true;
      axios.get("bycing_org/global_pref/site_ui__terms_of_service").then(response => {
        loading.value = false;
        termsOfService.value = response.data;
      }, error => {
        loading.value = true;
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isVisible,
      loading,
      termsOfService,
      loadTermsOfService,
      hide,
      show,
    }
  },
}
</script>

<style scoped>
</style>
