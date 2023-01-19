<template>
  <div>
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field hide-details label="Attachment Title(Optional)" v-model="newRecord.attachment_title"></v-text-field>
      </v-col>
      <v-col cols="12" md="6">
        <v-file-input multiple label="Choose Attachment" hide-details show-size class="mb-1" v-model="newRecord.files" :loading="uploading">
          <template v-slot:append-outer>
            <v-btn small color="primary" @click="uploadFiles()" :disabled="!(newRecord.files && newRecord.files.length)" :loading="uploading">
              <v-icon left>
                {{ icons.mdiCloudUploadOutline }}
              </v-icon>
              <span class="d-none d-sm-block">Upload</span>
            </v-btn>

          </template>
        </v-file-input>
      </v-col>
    </v-row>
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
      <template #item.create_datetime="{item}">
        <span class="pr-1">{{ $utils.formatDate(item.create_datetime, 'M/D/YY') }}</span>
        <span class="text-caption">{{ $utils.formatDate(item.create_datetime, 'HH:mm') }}</span>
      </template>
      <template #item.upload_by="{item}">
        <span>{{item._upload_by? item._upload_by.username: 'N/A'}}</span>
      </template>
      <template #item.title="{item}">
        <span>{{item.title || '-'}}</span>
      </template>
      <!-- actions -->
      <template #item.actions="{item}">
        <div class="d-flex align-end justify-end">
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn icon small v-bind="attrs" v-on="on" :href="item.file" target="_blank">
                <v-icon size="18">
                  {{ icons.mdiDownload }}
                </v-icon>
              </v-btn>
            </template>
            <span>Download Attachment</span>
          </v-tooltip>

          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn icon small v-bind="attrs" v-on="on" @click="deleteRecord(item)">
                <v-icon size="18">
                  {{ icons.mdiDelete }}
                </v-icon>
              </v-btn>
            </template>
            <span>Delete Attachment</span>
          </v-tooltip>

        </div>
      </template>

    </v-data-table>
  </div>

</template>

<script>
import {ref, watch} from "@vue/composition-api";
import {
  convertModelToFormData,
  notifyDefaultServerError,
  notifySuccess,
  refineVTableOptions
} from "@/composables/utils";
import axios from "@/axios";
import {
  mdiDelete,
  mdiDownload,
  mdiCloudUploadOutline,
} from "@mdi/js";
import store from "@/store";
import {routeNames} from "@/router";

export default {
  props: {
    event: {
      type: Object,
      required: true
    },
  },
  setup(props) {
    const records = ref([]);
    const pagination = ref({total: 0});
    const loading = ref(false);
    const uploading = ref(false);
    const tableOptions = ref({});
    const newRecord = ref({});
    const tableColumns = [
      {text: '#ID', value: 'id', sortable: false},
      {text: 'TITLE', value: 'title', sortable: false},
      {text: 'FILE NAME', value: 'file_name', sortable: false},
      {text: 'UPLOAD BY', value: 'upload_by', sortable: false},
      {text: 'CREATED AT', value: 'create_datetime', sortable: false},
      {text: 'ACTIONS', value: 'actions', align: 'end', sortable: false}
    ];

    const loadRecords = (page) => {
      if (page) {
        tableOptions.value.page = page;
      }
      const params = Object.assign({}, refineVTableOptions(tableOptions.value));
      loading.value = true;
      axios.get(`cycling_org/event/${props.event.id}/attachment`, {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
        pagination.value = response.data.pagination;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    const deleteRecord = (item) => {
      axios.delete(`cycling_org/event/${props.event.id}/attachment/${item.id}`).then((response) => {
        notifySuccess(`Attachment #${item.id} deleted.`);
        loadRecords();
      }, (error) => {
        notifyDefaultServerError(error, true);
      });

    };

    const uploadFiles = () => {
      var formData = convertModelToFormData(newRecord.value),
          headers = { headers: { "Content-Type": "multipart/form-data" } };
      uploading.value = true;
      axios.post(`cycling_org/event/${props.event.id}/attachment`, formData, headers).then((response) => {
        uploading.value = false;
        loadRecords(0);
        newRecord.value = {};
        notifySuccess(`uploaded ${response.data.attachments.length} files successfully.`);
      }, (error) => {
        uploading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    return {
      records,
      tableColumns,
      tableOptions,
      loading,
      uploading,
      pagination,
      loadRecords,
      uploadFiles,
      deleteRecord,
      newRecord,

      icons: {
        mdiDelete,
        mdiDownload,
        mdiCloudUploadOutline,
      },
    }
  },
}
</script>

<style scoped>

</style>
