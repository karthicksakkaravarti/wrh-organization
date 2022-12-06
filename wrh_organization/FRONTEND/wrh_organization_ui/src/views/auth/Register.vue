<template>
  <v-card class="auth-card">
    <!-- logo -->
    <v-card-title class="d-flex align-center justify-center py-7">
      <router-link
        :to="{name: $rns.ROOT}"
        class="d-flex align-center text-decoration-none"
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
        Adventure starts here 🚀
      </p>
      <p class="mb-2">
        Make your bycing races easy and fun!
      </p>
    </v-card-text>

    <!-- register form -->
    <v-card-text>
      <v-form @submit.prevent="register()" v-model="formValid">
        <v-text-field
          v-model="registerForm.email"
          outlined
          :append-icon="icons.mdiEmailOutline"
          label="E-mail"
          placeholder="E-mail"
          hide-details
          class="mb-3"
          :rules="[rules.required, rules.emailValidator]"
          dense
        ></v-text-field>

        <v-text-field
          v-model="registerForm.first_name"
          outlined
          label="First Name"
          placeholder="First Name"
          hide-details
          class="mb-3"
          :rules="[rules.required]"
          dense
        ></v-text-field>

        <v-text-field
          v-model="registerForm.last_name"
          outlined
          label="Last Name"
          placeholder="Last Name"
          hide-details
          class="mb-3"
          :rules="[rules.required]"
          dense
        ></v-text-field>

        <v-text-field
          v-model="registerForm.password"
          outlined
          :type="isPasswordVisible ? 'text' : 'password'"
          label="Password"
          placeholder="Password"
          :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline"
          class=""
          hint="Password should contains at least 1 digit with min 8 chars"
          persistent-hint
          :rules="[rules.required]"
          dense
          @click:append="isPasswordVisible = !isPasswordVisible"
        ></v-text-field>

        <v-text-field
          v-model="registerForm.confirm_password"
          outlined
          :type="isPasswordVisible ? 'text' : 'password'"
          label="Confirm Password"
          placeholder="Confirm Password"
          :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline"
          :rules="[rules.required, rules.confirmedValidator(registerForm.confirm_password, registerForm.password)]"
          dense
          @click:append="isPasswordVisible = !isPasswordVisible"
        ></v-text-field>

        <v-select
            outlined
            v-model="registerForm.gender"
            :items="$const.GENDER_OPTIONS"
            item-text="title"
            item-value="value"
            label="Gender"
            dense
            :rules="[rules.required]"
        ></v-select>

        <v-menu
          ref="birthDateMenuRef"
          v-model="showBirthDateMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              v-model="registerForm.birth_date"
              label="Birth Date"
              :append-icon="icons.mdiCalendar"
              readonly
              v-bind="attrs"
              v-on="on"
              :rules="[rules.required]"
              outlined
              dense
            ></v-text-field>
          </template>

          <v-date-picker
            ref="birthDatePickerRef"
            v-model="registerForm.birth_date"
            :max="new Date().toISOString().slice(0, 10)"
            min="1940-01-01"
            color="primary"
            @change="(d) => {$refs.birthDateMenuRef.save(d)}"
          ></v-date-picker>
        </v-menu>

        <v-text-field
            v-model="registerForm.member.phone"
            v-mask="$utils.internationalPhoneMask"
            :append-icon="icons.mdiPhoneOutline"
            outlined
            dense
            label="Phone"
        >
        </v-text-field>

        <v-autocomplete
            v-model="registerForm.member.country"
            outlined
            dense
            label="Country"
            :items="$const.COUNTRY_OPTIONS"
            item-text="name"
            item-value="code"
        ></v-autocomplete>

        <v-checkbox
          hide-details
          class="mt-1 agree-terms"
          v-model="registerForm.agree_terms"
        >
          <template #label>
            <span class="">I agree to</span>
          </template>
          <template #append>
            <v-btn text color="primary" link small @click.capture="$refs.termsOfServiceDialogRef.show()" class="pl-0 pr-1 pb-1">
              privacy policy &amp; terms
            </v-btn>
          </template>
        </v-checkbox>

        <v-btn
          block
          type="submit"
          color="primary"
          class="mt-6"
          :loading="registering"
          :disabled="!registerForm.agree_terms || !formValid"
        >
          Sign Up
        </v-btn>
      </v-form>
    </v-card-text>

    <!-- create new account  -->
    <v-card-text class="d-flex align-center justify-center flex-wrap mt-2">
      <span class="me-2">
        Already have an account?
      </span>
      <a @click="$emit('change-page', 'Login')">
        Sign in instead
      </a>
    </v-card-text>

    <!-- divider -->
    <v-card-text class="d-flex align-center mt-2">
      <v-divider></v-divider>
      <span class="mx-5">or</span>
      <v-divider></v-divider>
    </v-card-text>

    <!-- social link -->
    <v-card-actions class="d-flex justify-center">
      <v-btn
        v-for="link in socialLink"
        :key="link.icon"
        icon
        class="ms-1"
      >
        <v-icon :color="$vuetify.theme.dark ? link.colorInDark:link.color">
          {{ link.icon }}
        </v-icon>
      </v-btn>
    </v-card-actions>
    <terms-of-service-dialog ref="termsOfServiceDialogRef"></terms-of-service-dialog>
  </v-card>
</template>

<script>
// eslint-disable-next-line object-curly-newline
import {
  mdiEmailOutline,
  mdiPhoneOutline,
  mdiCalendar,
  mdiFacebook,
  mdiTwitter,
  mdiGithub,
  mdiGoogle,
  mdiEyeOutline,
  mdiEyeOffOutline
} from '@mdi/js'
import { ref, watch } from '@vue/composition-api'
import themeConfig from '@themeConfig'
import { required, emailValidator, passwordValidator, confirmedValidator } from '@core/utils/validation'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import TermsOfServiceDialog from "@/views/public/TermsOfServiceDialog.vue";

export default {
  components: {TermsOfServiceDialog},
  setup(props, context) {
    const isPasswordVisible = ref(false);
    const registering = ref(false);
    const formValid = ref(false);
    const showBirthDateMenu = ref(false);
    const birthDatePickerRef = ref(null);
    const registerForm = ref({member: {country: "US"}});

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

    watch(showBirthDateMenu, val => {
      // eslint-disable-next-line no-return-assign
      val && setTimeout(() => (birthDatePickerRef.value.activePicker = 'YEAR'));
    });
    const register = () => {
      registering.value = true;
      axios.post("bycing_org/users/registration", registerForm.value).then((response) => {
        registering.value = false;
        notifySuccess("Activation link sent to your email! please check your email.");
        context.emit("change-page", "Login");
      }, (error) => {
        registering.value = false;
        notifyDefaultServerError(error, true);
      });
    };


    return {
      isPasswordVisible,
      registerForm,
      socialLink,
      registering,
      formValid,
      showBirthDateMenu,
      birthDatePickerRef,
      register,

      rules: {
        required, emailValidator, confirmedValidator
      },

      // Icons
      icons: {
        mdiEyeOutline,
        mdiEyeOffOutline,
        mdiCalendar,
        mdiPhoneOutline,
        mdiEmailOutline,
      },

      // themeConfig
      appName: themeConfig.app.name,
      appLogo: themeConfig.app.logo,
    }
  },
}
</script>
<style>
  .auth-card .agree-terms .v-input__control {
    width: auto;
    flex-grow: 0;
  }
</style>
