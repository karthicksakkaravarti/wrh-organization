<template>
  <div class="member-profile-organization-tab">
    <v-card :disabled="loading">
      <v-card-text class="pb-0">
        <div class="d-flex justify-space-between pb-5">
          <div v-if="!loading">
            <v-tooltip v-if="is_singin" bottom>
              <template #activator="{ on, attrs }">
                <v-btn
                  v-bind="attrs"
                  v-on="on"
                  small
                  color="primary"
                  class="me-1"
                  @click="signOutFromCC"
                >
                  <span>Sign Out from CC</span>
                </v-btn>
              </template>
              <span>Sign Out from CC</span>
            </v-tooltip>
            <v-tooltip v-else bottom>
              <template #activator="{ on, attrs }">
                <v-btn
                  v-bind="attrs"
                  v-on="on"
                  small
                  color="primary"
                  class="me-1"
                  href="/accounts/constantcontact/login"
                >
                  <span>Authenticate with CC</span>
                </v-btn>
              </template>
              <span>Authenticate with CC</span>
            </v-tooltip>
          </div>

          <div v-if="is_singin">
            <v-autocomplete
              dense
              hide-details="auto"
              @change="loadCCListDetails"
              v-model="ccListSelect"
              v-if="ccList.length >= 1"
              :items="ccList"
              label="Choose List"
              item-value="list_id"
              item-text="name"
            ></v-autocomplete>
          </div>
        </div>

        <v-spacer></v-spacer>
      </v-card-text>
      <v-data-table
        :headers="tableColumns"
        :items="records"
        :loading="loading"
        class="text-no-wrap"
      >
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import {
  mdiAccountPlus,
  mdiPencilOutline,
  mdiEyeOutline,
  mdiAccountGroupOutline,
  mdiAccountMultipleOutline,
  mdiAccountCheck,
  mdiAccountCancel,
  mdiAccountCheckOutline,
  mdiFileExcelOutline,
  mdiSyncCircle,
  mdiCheckCircleOutline,
  mdiCloseCircleOutline,
  mdiRefresh,
} from "@mdi/js";

import { ref, reactive, watch, onMounted } from "@vue/composition-api";
import axios from "@/axios";
import {
  notifyDefaultServerError,
  refineVTableOptions,
} from "@/composables/utils";

export default {
  components: {},
  props: {},
  setup(props) {
    const records = ref([]);
    const is_singin = ref(false);
    const ccList = ref([]);
    const ccListSelect = ref();
    const loading = ref(false);
    const tableColumns = [
      { text: "Member Name", value: "" },
      { text: "Member Email", value: "" },
      { text: "Match Type", value: "" },
      { text: "Contact Name", value: "first_name" },
      { text: "Contact Email", value: "email_address.address" },
    ];

    const tableRowClass = (item) => {
      return `member-row${!item.is_active ? " inactive" : ""}`;
    };
    const signOutFromCC = () => {
      loading.value = true;
      axios.get(`/constantcontact/sign_out`).then(
        (response) => {
          loading.value = false;
          getCCStatus();
        },
        (error) => {
          loading.value = false;
          notifyDefaultServerError(error, true);
        }
      );
    };
    const loadCCListDetails = () => {
      loading.value = true;
      axios
        .get(`/constantcontact/contact_list_detail/${ccListSelect.value}/`)
        .then(
          (response) => {
            loading.value = false;
            records.value = response.data.contacts;
          },
          (error) => {
            loading.value = false;
            notifyDefaultServerError(error, true);
          }
        );
    };
    const loadCCList = () => {
      loading.value = true;
      axios.get(`/constantcontact/contact_list`).then(
        (response) => {
          loading.value = false;
          ccList.value = response.data.lists;
        },
        (error) => {
          loading.value = false;
          notifyDefaultServerError(error, true);
        }
      );
    };
    const getCCStatus = () => {
      loading.value = true;
      axios.get(`/constantcontact/cc_status`).then(
        (response) => {
          loading.value = false;
          is_singin.value = response.data.is_singin;
          console.log(is_singin.value);
          if (is_singin.value == true) {
            loadCCList();
          }
        },
        (error) => {
          loading.value = false;
          notifyDefaultServerError(error, true);
        }
      );
    };

    onMounted(getCCStatus);

    return {
      records,
      is_singin,
      ccList,
      ccListSelect,
      tableColumns,
      loading,
      signOutFromCC,
      getCCStatus,
      loadCCListDetails,
      loadCCList,
      tableRowClass,

      icons: {
        mdiAccountPlus,
        mdiPencilOutline,
        mdiEyeOutline,
        mdiAccountGroupOutline,
        mdiAccountMultipleOutline,
        mdiAccountCheck,
        mdiAccountCheckOutline,
        mdiFileExcelOutline,
        mdiSyncCircle,
        mdiCheckCircleOutline,
        mdiCloseCircleOutline,
        mdiAccountCancel,
        mdiRefresh,
      },
    };
  },
};
</script>

<style lang="scss">
.member-profile-organization-tab {
  a.title-link {
    color: inherit;
    text-decoration: none;
  }
  .organization-search {
    max-width: 10.625rem;
  }
  .organization-list-actions {
    max-width: 7.81rem;
  }
  table tr.member-row.inactive td:not(:last-child) {
    opacity: 0.5;
  }
}
</style>
