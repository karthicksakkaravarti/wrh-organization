<template>
  <v-card
    flat
    class="mt-5"
  >
    <v-form @submit.prevent="changePassword">
      <div class="px-3">
        <v-card-text class="pt-5">
          <v-row>
            <v-col
              cols="12"
              sm="8"
              md="6"
            >
              <!-- current password -->
              <v-text-field
                v-model="passwords.current_password"
                :type="visiblePasswords.current_password ? 'text' : 'password'"
                :append-icon="visiblePasswords.current_password ? icons.mdiEyeOffOutline:icons.mdiEyeOutline"
                label="Current Password"
                outlined
                dense
                @click:append="visiblePasswords.current_password = !visiblePasswords.current_password"
              ></v-text-field>

              <!-- new password -->
              <v-text-field
                v-model="passwords.new_password"
                :type="visiblePasswords.new_password ? 'text' : 'password'"
                :append-icon="visiblePasswords.new_password ? icons.mdiEyeOffOutline:icons.mdiEyeOutline"
                label="New Password"
                outlined
                dense
                hint="Make sure password contains at least one digit with min 8 chars"
                persistent-hint
                @click:append="visiblePasswords.new_password = !visiblePasswords.new_password"

              ></v-text-field>

              <!-- confirm password -->
              <v-text-field
                v-model="passwords.re_new_password"
                :type="visiblePasswords.re_new_password ? 'text' : 'password'"
                :append-icon="visiblePasswords.re_new_password ? icons.mdiEyeOffOutline:icons.mdiEyeOutline"
                label="Confirm New Password"
                outlined
                dense
                persistent-hint
                class="mt-3"
                :rules="[confirmedValidator(passwords.re_new_password,passwords.new_password)]"
                @click:append="visiblePasswords.re_new_password = !visiblePasswords.re_new_password"
              ></v-text-field>
            </v-col>

            <v-col
              cols="12"
              sm="4"
              md="6"
              class="d-none d-sm-flex justify-center position-relative"
            >
              <v-img
                contain
                max-width="170"
                src="@/assets/images/3d-characters/pose-m-1.png"
                class="security-character"
              ></v-img>
            </v-col>
          </v-row>
        </v-card-text>
      </div>

      <!-- divider -->
      <v-divider></v-divider>

      <div class="pa-3">
        <v-card-title class="flex-nowrap">
          <v-icon class="text--primary me-3">
            {{ icons.mdiKeyOutline }}
          </v-icon>
          <span class="text-break">Two-factor authentication</span>
        </v-card-title>

        <v-card-text class="two-factor-auth text-center mx-auto">
          <v-avatar
            color="primary"
            class="v-avatar-light-bg primary--text mb-4"
            rounded
          >
            <v-icon
              size="25"
              color="primary"
            >
              {{ icons.mdiLockOpenOutline }}
            </v-icon>
          </v-avatar>
          <p class="text-base text--primary font-weight-semibold">
            Two factor authentication is not enabled yet.
          </p>
          <p class="text-sm text--primary">
            Two-factor authentication adds an additional layer of
            security to your account by requiring more than just a
            password to log in. Learn more.
          </p>
        </v-card-text>

        <!-- action buttons -->
        <v-card-text>
          <v-btn
            color="primary"
            class="me-3 mt-3"
            type="submit"
          >
            Save changes
          </v-btn>
          <v-btn
            color="secondary"
            outlined
            class="mt-3"
            @click="resetPasswordForm()"
          >
            Cancel
          </v-btn>
        </v-card-text>
      </div>
    </v-form>
    <v-overlay :value="changingPassword" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </v-card>
</template>

<script>
// eslint-disable-next-line object-curly-newline
import { mdiKeyOutline, mdiLockOpenOutline, mdiEyeOffOutline, mdiEyeOutline } from '@mdi/js'
import { reactive, ref } from '@vue/composition-api'
import { passwordValidator, confirmedValidator } from '@core/utils/validation'
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import axios from "@/axios";
import EventBus from "@/EventBus";
import store from '@/store';

export default {
  setup() {
    const changingPassword = ref(false);
    const passwords = reactive({current_password: "", new_password: "", re_new_password: ""});
    const visiblePasswords = reactive({current_password: false, new_password: false, re_new_password: false});

    const resetPasswordForm = () => {
      Object.assign(passwords, {current_password: "", new_password: "", re_new_password: ""});
    };

    const changePassword = () => {
      changingPassword.value = true;
      axios.put("account/me/password", passwords).then(() => {
          store.commit('currentUser', {});
          resetPasswordForm();
          changingPassword.value = false;
          notifySuccess("Password changed successfully. please login again");
        }, (response) => {
          changingPassword.value = false;
          notifyDefaultServerError(response, true);
        }
      );
    };

    return {
      changingPassword,
      passwords,
      visiblePasswords,
      passwordValidator,
      confirmedValidator,
      changePassword,
      resetPasswordForm,
      icons: {
        mdiKeyOutline,
        mdiLockOpenOutline,
        mdiEyeOffOutline,
        mdiEyeOutline,
      },
    }
  },
}
</script>

<style lang="scss" scoped>
.two-factor-auth {
  max-width: 25rem;
}
.security-character {
  position: absolute;
  bottom: -0.5rem;
}
</style>
