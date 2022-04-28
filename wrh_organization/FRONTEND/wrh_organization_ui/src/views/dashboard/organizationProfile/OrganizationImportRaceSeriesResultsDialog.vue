<template>
  <v-dialog v-model="isVisible" persistent width="500">
    <v-card class="org-import-members-card">
      <v-form @submit.prevent="importCsv()">
        <v-card-title class="headline">
          Import Race Series Results From CSV
        </v-card-title>
        <v-card-text v-if="raceSeries">
          <div>Race Series: <span class="font-weight-semibold">{{raceSeries.name}}</span></div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text>
          <v-file-input show-size :prepend-icon="icons.mdiFileExcel" label="Choose a CSV file" hide-details
                        @change="onChangeFile"
                        accept=".csv" ref="csvFileRef"></v-file-input>
        </v-card-text>
        <v-card-text>
          <app-card-actions action-collapse flat outlined ref="csvColsCardRef">
            <template #title>
              <v-icon class="mr-2">{{icons.mdiInformationOutline}}</v-icon> CSV Columns
            </template>
            <v-card-text>
              Your csv file should contains this required columns:
              <ul>
                <li>id</li>
                <li>category</li>
                <li>category_place</li>
              </ul>
            </v-card-text>
          </app-card-actions>

        </v-card-text>
        <v-card-text v-if="failedRecords && failedRecords.length">
          <app-card-actions action-collapse flat outlined color="warning">
            <template #title>
              <v-icon>{{icons.mdiAlertOutline}}</v-icon> Failed Records
            </template>
            <pre class="failed-records">{{JSON.stringify(failedRecords, null, 2)}}</pre>
          </app-card-actions>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
          <v-btn color="primary" type="submit" :loading="importing" :disabled="!csvFile">Import</v-btn>
        </v-card-actions>

      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {mdiFileExcel, mdiInformationOutline, mdiAlertOutline} from '@mdi/js';
import { ref } from '@vue/composition-api';
import axios from "@/axios";
import {notifyDefaultServerError, notifyInfo} from "@/composables/utils";
import AppCardActions from "@core/components/app-card-actions/AppCardActions";

export default {
  components: {AppCardActions},
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const importing = ref(false);
    const csvFile = ref(null);
    const csvFileRef = ref(null);
    const csvColsCardRef = ref(null);
    const failedRecords = ref([]);
    const raceSeries = ref(null);

    const hide = () => {
      isVisible.value = false;
    };

    const show = (_raceSeries) => {
      csvFile.value = null;
      importing.value = false;
      failedRecords.value = [];
      isVisible.value = true;
      raceSeries.value = _raceSeries;
    };

    const onChangeFile = (file) => {
      csvFile.value = file || null;
    };

    const importCsv = () => {
      importing.value = true;
      var formData = new FormData(),
          orgId = props.organization.id,
          raceSeriesId = raceSeries.value.id;
      formData.append('file', csvFile.value);
      axios.post( `bycing_org/race_series_result/organization/${orgId}/race_series/${raceSeriesId}/import_from_csv`,
          formData, {headers: {'Content-Type': 'multipart/form-data'}}
      ).then((response) => {
        importing.value = false;
        context.emit('import-successed');
        notifyInfo(`Race Series Results imported. ${response.data.successed} successed. ${response.data.failed.length} failed.`);
        failedRecords.value = response.data.failed;
        csvFileRef.value.clearableCallback();
        if (failedRecords.value && failedRecords.value.length && !csvColsCardRef.value.isContentCollapsed) {
          csvColsCardRef.value.triggerCollapse();
        }
      }, (error) => {
        importing.value = false;
        notifyDefaultServerError(error, true);
      });
    };
    
    return {
      isVisible,
      importing,
      csvFile,
      csvFileRef,
      csvColsCardRef,
      show,
      hide,
      importCsv,
      onChangeFile,
      failedRecords,
      raceSeries,
      icons: {
        mdiFileExcel,
        mdiInformationOutline,
        mdiAlertOutline
      }
    }
  },
}
</script>

<style>
.org-import-members-card .v-card .v-card__title {
  padding: 10px !important;
}
.org-import-members-card pre.failed-records {
  max-height: 300px;
  overflow: auto;
}
</style>
