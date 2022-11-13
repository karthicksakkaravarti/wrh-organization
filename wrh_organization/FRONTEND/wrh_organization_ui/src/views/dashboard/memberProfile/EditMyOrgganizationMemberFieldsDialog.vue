<template>
  <v-dialog v-model="isVisible" persistent max-width="700px">
    <v-card>
      <v-card-title class="headline">
        Membership info: <span class="ml-2 font-weight-bold"> {{ organization.name }}</span>
      </v-card-title>
      <v-form @submit.prevent="save" v-model="formValid">
        <v-card-text class="pr-2 pl-2">
          <v-container v-if="schema">
            <v-row>
              <v-col cols="12">
                <span v-if="!schema.length" class="caption font-weight-semibold warning--text">
                    No membership fields defined in this organization!
                </span>
                <span v-else class="caption font-weight-semibold">
                    Edit your membership fields of this organization.
                </span>
              </v-col>
              <v-col cols="12" :md="f.type == 'text' || (f.choices && f.choices.length > 0)? 12: 6"
                     v-for="f in schema" :key="f.name">
                <template v-if="f.choices && f.choices.length > 0">
                  <p class="caption mb-0">{{f.title}}:</p>
                  <div v-if="f.multiple" class="d-flex flex-wrap demo-space-x mt-0">
                    <v-checkbox v-for="(c, cIdx) in f.choices" v-model="record[f.name]"
                                class="mt-0 mb-0 pt-0" :label="c.title" :value="c.value" :key="cIdx" hide-details></v-checkbox>
                  </div>
                  <v-radio-group v-else v-model="record[f.name]" hide-details class="mt-0"
                                 :rules="f.required? [rules.required]: []">
                    <div class="d-flex flex-wrap demo-space-x mt-0">
                      <v-radio v-for="(c, cIdx) in f.choices" :label="c.title" :value="c.value" :key="cIdx"
                               class="mt-0 mb-0 pt-0"></v-radio>
                    </div>
                  </v-radio-group>
                </template>
                <template v-else-if="f.type=='integer' || f.type=='float' || f.type=='number'">
                  <v-text-field
                      dense
                      v-model.number="record[f.name]"
                      :label="f.title"
                      type="number"
                      :step="f.type=='integer'? 1: 'any'"
                      :rules="f.required? [rules.required]: []"
                  ></v-text-field>
                </template>
                <template v-else-if="f.type=='percent'">
                  <v-text-field
                      dense
                      v-model.number="record[f.name]"
                      :label="f.title"
                      :rules="f.required? [rules.required]: []"
                      type="number"
                      suffix="%"
                      min="0"
                      max="100"
                  ></v-text-field>
                </template>
                <template v-else-if="f.type=='boolean'">
                  <v-switch
                      v-model="record[f.name]"
                      :label="f.title"
                      dense
                      class="pt-0 mt-1"
                  ></v-switch>
                </template>
                <template v-else-if="f.type=='date' || f.type=='time'">
                  <v-menu v-model="uiFieldsData[`menu__${f.name}`]" :close-on-content-click="false"
                          :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                          v-model="record[f.name]"
                          :label="f.title"
                          :rules="f.required? [rules.required]: []"
                          class="pt-0 mt-0 mb-5"
                          :append-icon="f.type=='time'? icons.mdiClockOutline: icons.mdiCalendar"
                          v-bind="attrs"
                          v-on="on"
                          readonly>
                      </v-text-field>
                    </template>
                    <v-time-picker v-if="f.type=='time'" v-model="record[f.name]" color="primary"
                                   @click:minute="uiFieldsData[`menu__${f.name}`] = false"></v-time-picker>
                    <v-date-picker v-else v-model="record[f.name]" color="primary"
                                   @input="uiFieldsData[`menu__${f.name}`] = false"></v-date-picker>
                  </v-menu>
                </template>
                <template v-else-if="f.type=='datetime'">
                  <v-datetime-picker v-model="record[f.name]" :label="f.title"
                                     :text-field-props="{appendIcon: icons.mdiCalendar, class: 'pt-0 mt-0 mb-5', rules: f.required? [rules.required]: []}">
                    <template #dateIcon>
                      <v-icon>{{icons.mdiCalendar}}</v-icon>
                    </template>
                    <template #timeIcon>
                      <v-icon>{{icons.mdiClock}}</v-icon>
                    </template>
                  </v-datetime-picker>
                </template>
                <template v-else-if="f.type=='text'">
                  <v-textarea
                      dense
                      v-model="record[f.name]"
                      :label="f.title"
                      :rules="f.required? [rules.required]: []"
                      rows="2"
                  ></v-textarea>
                </template>
                <template v-else>
                  <v-text-field
                      dense
                      v-model.trim="record[f.name]"
                      :label="f.title"
                      :rules="f.required? [rules.required]: []"
                      type="text"
                  ></v-text-field>
                </template>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined @click="hide()">Cancel</v-btn>
          <v-btn type="submit" color="primary" :loading="saving" :disabled="!formValid || !schema || !schema.length">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
    <v-overlay :value="loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </v-dialog>
</template>

<script>
import {ref, set} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import { mdiLinkVariant } from '@mdi/js';
import {required} from "@core/utils/validation";

export default {
  props: {
  },
  setup(props, context) {
    const record = ref({});
    const organization = ref({});
    const isVisible = ref(false);
    const saving = ref(false);
    const loading = ref(false);
    const schema = ref(null);
    const formValid = ref(false);
    const uiFieldsData = ref({});

    const hide = () => {
      isVisible.value = false;
    };
    const show = (org) => {
      organization.value = org;
      schema.value = null;
      record.value = {};
      uiFieldsData.value = {};
      saving.value = false;
      loading.value = false;
      loadSchema();
      loadRecord();
      isVisible.value = true;
    };

    const loadSchema = () => {
      let params = {exfields: "member_fields_schema", fields: "member_fields_schema"};
      axios.get(`bycing_org/organization/${organization.value.id}`, {params: params}).then((response) => {
        schema.value = response.data.member_fields_schema || [];
        schema.value.forEach(r => {
          if (r.multiple) {
            set(record.value, r.name, []);
          }
        });

      }, (error) => {
        notifyDefaultServerError(error, true);
      });
    };

    const loadRecord = () => {
      loading.value = true;
      axios.get(`bycing_org/organization/${organization.value.id}/my_member_fields`).then((response) => {
        loading.value = false;
        record.value = response.data || {};
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      saving.value = true;
      axios.put(`bycing_org/organization/${organization.value.id}/my_member_fields`, record.value).then((response) => {
        saving.value = false;
        notifySuccess("Your membership info saved successfully.");
        context.emit('save-successed');
        hide();
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isVisible,
      saving,
      loading,
      schema,
      record,
      organization,
      uiFieldsData,
      formValid,
      show,
      hide,
      save,
      loadSchema,
      loadRecord,
      rules: {
        required
      },
      icons: {
        mdiLinkVariant
      }
    }
  },
}
</script>

