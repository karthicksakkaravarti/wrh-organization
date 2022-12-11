<template>
  <div class="organization-profile-categories-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <v-btn fab x-small color="info" class="mr-1" @click="loadRecords(1);">
            <v-icon>{{icons.mdiRefresh}}</v-icon>
          </v-btn>
          <v-btn v-if="organization.my_level.is_admin" small color="primary" class="me-1"
                 @click="$refs.formDialogRef.show()">
            <v-icon size="18" class="me-1">
              {{ icons.mdiPlus }}
            </v-icon>
            <span>New Category</span>
          </v-btn>
        </div>

        <v-spacer></v-spacer>

        <div class="d-flex align-center pb-5">
          <v-text-field
              :value="tableFiltering.search"
              @change="value => $set(tableFiltering, 'search', value)"
              @click:clear="$set(tableFiltering, 'search', null)"
              dense clearable hide-details
              placeholder="Search ..." class="me-3 search-input"
          ></v-text-field>

        </div>
      </v-card-text>

      <v-data-table
        :headers="tableColumns"
        :items="records"
        :options.sync="tableOptions"
        @update:options="loadRecords()"
        :server-items-length="pagination.total"
        :loading="loading"
        class="text-no-wrap"
        :footer-props="{'items-per-page-options': $const.DEFAULT_TABLE_PER_PAGE_OPTIONS, 'show-current-page': true, 'show-first-last-page': true}"
      >
        <template #item.title="{item}">
            <span class="text-truncate font-weight-semibold cursor-pointer" @click="$refs.formDialogRef.show(item)">
              {{item.title}}
            </span>
        </template>
        <template #item.create_by="{item}">
          <div class="d-flex align-center">
            <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
              <v-img v-if="item._create_by.avatar" :src="item._create_by.avatar"></v-img>
              <span v-else class="font-weight-medium">
                {{ avatarText(item._create_by.username) }}
              </span>
            </v-avatar>

            <div class="d-flex flex-column ms-3">
              <span class="text-xs">{{ item._create_by.username || '-' }}</span>
            </div>
          </div>
        </template>
        <template #item.create_datetime="{item}">
          <span class="pr-1">{{$utils.formatDate(item.create_datetime, 'M/D/YY')}}</span>
          <span class="text-caption">{{$utils.formatDate(item.create_datetime, 'HH:mm')}}</span>
        </template>

        <!-- actions -->
        <template #item.actions="{item}">
          <div class="d-flex align-end justify-end">
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon small v-bind="attrs" v-on="on" @click="$refs.formDialogRef.show(item)">
                  <v-icon size="18">
                    {{ icons.mdiPencilOutline }}
                  </v-icon>
                </v-btn>
              </template>
              <span>Edit</span>
            </v-tooltip>
          </div>
        </template>

      </v-data-table>
    </v-card>
    <organization-category-form-dialog :organization="organization" ref="formDialogRef" @save-successed="loadRecords(1)"
                                    @delete-successed="loadRecords(1)">
    </organization-category-form-dialog>
  </div>
</template>

<script>
import {
  mdiPlus,
  mdiPencilOutline,
  mdiRefresh,
} from '@mdi/js'

import { ref, reactive, watch, onMounted } from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import OrganizationCategoryFormDialog from "./OrganizationCategoryFormDialog";

export default {
  components: {OrganizationCategoryFormDialog},
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const tableOptions = ref({});
    const tableFiltering = ref({});

    const tableColumns = [
      {text: '#ID', value: 'id', align: 'start',},
      {text: 'TITLE', value: 'title'},
      {text: 'CREATED BY', value: 'create_by'},
      {text: 'CREATED AT', value: 'create_datetime'},
    ];
    if (props.organization.my_level.is_admin) {
      tableColumns.push({text: 'ACTIONS', value: 'actions', align: 'end', sortable: false,})
    }

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({organization: props.organization.id}, tableFiltering.value, refineVTableOptions(tableOptions.value));
      loading.value = true;
      axios.get("cycling_org/category/", {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });
    };
    watch(() => tableFiltering, (currentValue, oldValue) => {
        loadRecords(1);
      },
      { deep: true }
    );

    onMounted(() => {
    });

    return {
      records,
      tableColumns,
      tableOptions,
      tableFiltering,
      loading,
      pagination,
      loadRecords,
      icons: {
        mdiPlus,
        mdiPencilOutline,
        mdiRefresh,
      },
    }
  },
}
</script>

<style lang="scss">
.organization-profile-categories-tab {
  .search-input {
    max-width: 10.625rem;
  }
  td.event-td {
    max-width: 250px;
  }
}
</style>
