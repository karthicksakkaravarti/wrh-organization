<template>
  <v-card class="auth-card">
    <v-card-title class="d-flex align-center justify-center py-7">
      <router-link
        :to="{name: $rns.ROOT}"
        class="d-flex align-center"
      >
        <v-img
          :src="appLogo"
          max-height="30px"
          max-width="30px"
          alt="logo"
          contain
          class="me-3 "
        ></v-img>

        <h2 class="text-2xl font-weight-semibold">
          {{ appName }}
        </h2>
      </router-link>
    </v-card-title>

    <v-card-text>
      <p class="text-2xl font-weight-semibold text--primary mb-2">
        Forgot Password? 🔒
      </p>
      <p class="mb-2">
        Enter your email and we'll send you instructions to reset your password
      </p>
    </v-card-text>

    <!-- login form -->
    <v-card-text>
      <v-form @submit.prevent="sendRecoverPassword()" v-model="formValid">
        <v-text-field
          v-model="forgotForm.email"
          outlined
          label="E-mail"
          placeholder="E-mail"
          hide-details
          class="mb-4"
          :rules="[rules.required, rules.emailValidator]"
        ></v-text-field>

        <v-btn
          block
          type="submit"
          color="primary"
          class="mt-6"
          :loading="requesting"
          :disabled="!formValid"
        >
          Send reset link
        </v-btn>
      </v-form>
    </v-card-text>

    <v-card-actions class="d-flex justify-center align-center">
      <a class="d-flex align-center text-sm" @click="$emit('change-page', 'Login')">
        <v-icon
          size="24"
          color="primary"
        >
          {{ icons.mdiChevronLeft }}
        </v-icon>
        <span>Back to login</span>
      </a>
    </v-card-actions>
  </v-card>

</template>

<script>
// eslint-disable-next-line object-curly-newline
import { mdiEyeOutline, mdiEyeOffOutline } from '@mdi/js'
import { ref } from '@vue/composition-api'
import themeConfig from '@themeConfig'
import { required, emailValidator, passwordValidator, confirmedValidator } from '@core/utils/validation'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";

export default {
  setup(props, context) {
    const isPasswordVisible = ref(false);
    const requesting = ref(false);
    const formValid = ref(false);

    const forgotForm = ref({});

    const sendRecoverPassword = () => {
      requesting.value = true;
      axios.post("bycing_org/users/registration/send_recover_password", forgotForm.value).then((response) => {
        requesting.value = false;
        notifySuccess("Reset password link sent to your email! please check your email.");
        context.emit("change-page", "Login");
      }, (error) => {
        requesting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isPasswordVisible,
      forgotForm,
      requesting,
      formValid,
      sendRecoverPassword,

      rules: {
        required, emailValidator
      },

      // Icons
      icons: {
        mdiEyeOutline,
        mdiEyeOffOutline,
      },

      // themeConfig
      appName: themeConfig.app.name,
      appLogo: themeConfig.app.logo,
    }
  },
}
</script>
