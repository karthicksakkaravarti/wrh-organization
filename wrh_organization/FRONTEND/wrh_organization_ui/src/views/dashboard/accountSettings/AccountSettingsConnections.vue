<template>
  <div class="user-tab-connection" :class="{'no-member': !accountData.id}">
    <!-- social accounts -->
    <v-card class="mb-1">
      <v-card-title>
        Social Accounts
      </v-card-title>
      <v-card-subtitle>
        list of your social accounts
      </v-card-subtitle>
      <v-card-text>
        <v-list
          dense
          class="py-0"
        >
          <v-list-item
            v-for="(account,index) in $const.SOCIAL_ACCOUNTS"
            :key="account.title"
            :class="`px-0 ${index > 0 ?'mt-6':'mt-3'}`"
          >
            <v-img
              max-width="35"
              height="35"
              contain
              class="me-3"
              :src="require(`@/assets/images/logos/${account.img}`)"
            ></v-img>

            <div>
              <v-list-item-title class="text-sm">
                {{ account.title }}
              </v-list-item-title>
              <v-list-item-subtitle v-if="socialMediaData[account.name]">
                <a
                  :href="socialMediaData[account.name]"
                  target="_blank"
                  rel="nofollow"
                  class="text-decoration-none text-truncate"
                >
                  {{ socialMediaData[account.name] }}
                </a>
              </v-list-item-subtitle>
              <v-list-item-subtitle v-else>
                Not connected
              </v-list-item-subtitle>
            </div>

            <v-spacer></v-spacer>

            <v-btn color="secondary" outlined min-width="38" class="px-0" @click="$refs.socialDialogRef.show(socialMediaData, account.name, account.title, )">
              <v-icon size="20">
                {{ !socialMediaData[account.name]? icons.mdiLinkVariantPlus: icons.mdiPencilOutline }}
              </v-icon>
            </v-btn>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- connected accounts -->
    <v-card>
      <v-card-title>
        Connected Accounts
      </v-card-title>
      <v-card-subtitle>
        list of connected accounts to your profile
      </v-card-subtitle>

      <v-card-text class="pb-2">
        <v-list
          dense
          class="py-0"
        >
          <v-list-item
            v-for="account in $const.CONNECTED_ACCOUNTS"
            :key="account.title"
            class="px-0"
          >
            <v-img
              max-width="35"
              contain
              class="me-3"
              :src="require(`@/assets/images/logos/${account.img}`)"
            ></v-img>

            <div class="d-flex align-center flex-grow-1 flex-wrap">
              <div class="me-2">
                <v-list-item-title class="text-sm">
                  {{ account.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="mb-0">
                  {{ account.text }}
                </v-list-item-subtitle>
              </div>

              <v-spacer></v-spacer>

              <v-switch v-model="account.connected" disabled></v-switch>
            </div>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
    <account-settings-connection-dialog ref="socialDialogRef" @save-successed="loadSocialMedia()"></account-settings-connection-dialog>
    <v-overlay :value="loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>
import { mdiPencilOutline, mdiLinkVariantPlus } from '@mdi/js'
import axios from "@/axios";
import {nextTick, ref} from "@vue/composition-api/dist/vue-composition-api";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted} from "@vue/composition-api";
import AccountSettingsConnectionDialog from "@/views/dashboard/accountSettings/AccountSettingsConnectionDialog";

export default {
  components: {AccountSettingsConnectionDialog},
  setup() {
    const socialMediaData = ref({});
    const accountData = ref({user: {}});
    const loading = ref(false);

    const loadSocialMedia = () => {
      loading.value = true;
      axios.get("bycing_org/member/me", {params: {fields: 'id,social_media'}}).then((response) => {
        socialMediaData.value = response.data.social_media || {};
        accountData.value = response.data;
        loading.value = false;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    onMounted(() => {
      loadSocialMedia();
    });

    return {
      socialMediaData,
      accountData,
      loading,
      loadSocialMedia,
      icons: {
        mdiPencilOutline,
        mdiLinkVariantPlus,
      },
    }
  },
}
</script>

<style scoped>
  .no-member {
    opacity: 0.5;
    pointer-events: none;
  }
</style>
