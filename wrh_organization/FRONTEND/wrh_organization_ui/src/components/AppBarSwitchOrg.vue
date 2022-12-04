<template>
  <v-menu
    offset-y
    left
    nudge-bottom="14"
    min-width="230"
    content-class="switch-org-menu-content"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="primary" dark outlined v-bind="attrs" v-on="on" class="mr-4" @click="loadOrganizations()">
        <v-icon color="primary">
          {{icons.mdiHomeSwitch}}
        </v-icon>
        <span class="d-none d-sm-block">Switch Org</span>
        <v-icon color="primary">
          {{attrs['aria-expanded'] == 'false'? icons.mdiChevronDown: icons.mdiChevronUp}}
        </v-icon>
      </v-btn>
    </template>
    <v-list two-line>
      <v-list-item v-if="loading" class="d-block text-center pt-2">
        <v-progress-circular indeterminate color="primary" width="3"></v-progress-circular>
      </v-list-item>
      <v-list-item v-else-if="!(organizations || []).length" class="d-block text-center pt-2">
        No Organization!
      </v-list-item>
      <template v-else v-for="org in (organizations || [])">
        <v-list-item :key="org.id" :to="{name: $rns.PUBLIC_ORG_PROFILE, params:{record_id: org.id}}">
          <v-list-item-avatar class="v-avatar-light-bg success--text success">
            <v-img v-if="org.logo" :src="org.logo"></v-img>
            <span v-else class="font-weight-medium">
              {{ avatarText(org.name) }}
            </span>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title>
              <span v-if="$store.getters.defaultRegionalOrg == org.id" class="font-weight-medium">
                <v-icon size="20" color="warning">{{icons.mdiStar}}</v-icon>
                {{ org.name }}
              </span>
              <span v-else>
                {{org.name}}
              </span>

              <v-chip x-small :color="($const.ORGANIZATION_TYPE_MAP[org.type] || {}).css"
                      :class="`v-chip-light-bg ${($const.ORGANIZATION_TYPE_MAP[org.type] || {}).css}--text`">
                {{($const.ORGANIZATION_TYPE_MAP[org.type] || {}).title || org.type}}
              </v-chip>

            </v-list-item-title>
          </v-list-item-content>

        </v-list-item>
      </template>

    </v-list>
  </v-menu>
</template>

<script>
import {
  mdiHomeSwitch,
  mdiStar,
  mdiChevronDown,
  mdiChevronUp,
} from '@mdi/js'
import axios from "@/axios";
import EventBus from "@/EventBus";
import store from "@/store";
import {avatarText} from "@core/utils/filter";
import {notifyDefaultServerError} from "@/composables/utils";
import {onMounted, ref} from "@vue/composition-api";

export default {
  setup() {
    const organizations = ref(null);
    const loading = ref(false);

    const loadOrganizations = () => {
      if (loading.value || organizations.value) {
        return;
      }
      loading.value = true;
      var params = {
        page_size: 0,
        my: true,
        order_by: 'type,-id'
      };
      axios.get(`bycing_org/organization`, {params: params}).then((response) => {
        loading.value = false;
        var defaultOrg = store.getters.defaultRegionalOrg;
        var results = response.data.results;
        if (defaultOrg) {
          results.sort((o1, o2) => {
            return o1.id === defaultOrg? -1: o2.id === defaultOrg? 1: 0
          });
        }
        organizations.value = results;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    return {
      loadOrganizations,
      organizations,
      loading,
      avatarText,
      icons: {
        mdiHomeSwitch,
        mdiStar,
        mdiChevronDown,
        mdiChevronUp,
      },
    }
  },
}
</script>

<style lang="scss">
.switch-org-menu-content {
  .v-list-item {
    min-height: 3rem !important;
  }
}
</style>
