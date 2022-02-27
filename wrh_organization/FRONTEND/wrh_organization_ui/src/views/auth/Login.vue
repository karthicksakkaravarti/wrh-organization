<template>
  <v-card class="auth-card">
    <!-- logo -->
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

    <!-- title -->
    <v-card-text>
      <p class="text-2xl font-weight-semibold text--primary mb-2">
        Login to Wrh-Organization
      </p>
      <p class="mb-2">
        Please sign-in to your account and start the adventure
      </p>
    </v-card-text>

    <!-- login form -->
    <v-card-text>
      <v-form @submit.prevent="login()" v-model="formValid">
        <v-text-field
          v-model="loginForm.username"
          outlined
          label="Username"
          placeholder="Username"
          hide-details
          class="mb-3"
          :rules="[rules.required]"
        ></v-text-field>

        <v-text-field
          v-model="loginForm.password"
          outlined
          :type="isPasswordVisible ? 'text' : 'password'"
          label="Password"
          placeholder="Password"
          :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline"
          hide-details
          :rules="[rules.required]"
          @click:append="isPasswordVisible = !isPasswordVisible"
        ></v-text-field>

        <div class="d-flex align-center justify-space-between flex-wrap">
          <v-checkbox
            label="Remember Me"
            hide-details
            class="me-3 mt-1"
          >
          </v-checkbox>

          <!-- forgot link -->
          <a class="mt-1" @click="$emit('change-page', 'ForgotPassword')">
            Forgot Password?
          </a>
        </div>

        <v-btn
          block
          type="submit"
          color="primary"
          class="mt-6"
          :loading="logining"
          :disabled="!formValid"
        >
          Login
        </v-btn>
      </v-form>
    </v-card-text>

    <!-- create new account  -->
    <v-card-text class="d-flex align-center justify-center flex-wrap mt-2">
      <span class="me-2">
        New on our platform?
      </span>
      <a @click="$emit('change-page', 'Register')">
        Create an account
      </a>
    </v-card-text>

    <!-- divider -->
    <v-card-text class="d-flex align-center mt-2">
      <v-divider></v-divider>
      <span class="mx-5">or</span>
      <v-divider></v-divider>
    </v-card-text>

    <!-- social links -->
    <v-card-actions class="d-flex justify-center">
      <v-btn
        v-for="link in socialLink"
        :key="link.icon"
        icon
        class="ms-1"
      >
        <v-icon :color="$vuetify.theme.dark ? link.colorInDark : link.color">
          {{ link.icon }}
        </v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>

</template>

<script>
// eslint-disable-next-line object-curly-newline
import { mdiFacebook, mdiTwitter, mdiGithub, mdiGoogle, mdiEyeOutline, mdiEyeOffOutline } from '@mdi/js'
import { ref } from '@vue/composition-api'
import themeConfig from '@themeConfig'
import { required, emailValidator, passwordValidator, confirmedValidator } from '@core/utils/validation'
import axios from "@/axios";
import store from "@/store";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import EventBus from "@/EventBus";

export default {
  setup() {
    const isPasswordVisible = ref(false);
    const logining = ref(false);
    const formValid = ref(false);

    const loginForm = ref({});

    const socialLink = [
      {
        icon: mdiFacebook,
        color: '#4267b2',
        colorInDark: '#4267b2',
      },
      {
        icon: mdiTwitter,
        color: '#1da1f2',
        colorInDark: '#1da1f2',
      },
      {
        icon: mdiGithub,
        color: '#272727',
        colorInDark: '#fff',
      },
      {
        icon: mdiGoogle,
        color: '#db4437',
        colorInDark: '#db4437',
      },
    ];

    const login = () => {
      logining.value = true;
      axios.post("account/session", loginForm.value).then((response) => {
        store.state.currentUser = response.data;
        logining.value = false;
        notifySuccess("Welcome to WRH!", 5000);
      }, (error) => {
        logining.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isPasswordVisible,
      loginForm,
      socialLink,
      logining,
      formValid,
      login,

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
