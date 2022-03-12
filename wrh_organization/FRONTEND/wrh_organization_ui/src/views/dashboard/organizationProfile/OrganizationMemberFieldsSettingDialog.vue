<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Entry Form Settings: <span class="error--text">{{fieldData.title}}</span></span>
      </v-card-title>
      <v-form @submit.prevent="save" v-model="formValid">
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <h2 class="text-xl font-weight-semibold">Fields Config</h2>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="fieldData.name" label="Unique Name" dense
                              :append-icon="nameLocked? icons.mdiLockOff: icons.mdiLockOpen"
                              @click:append="nameLocked = !nameLocked"
                              :readonly="nameLocked"
                              hint="leave blank to auto generate. Caution! changing this field will lose value of saved records!"
                              persistent-hint outlined></v-text-field>
              </v-col>
              <v-col cols="12">
                <h2 class="text-xl font-weight-semibold">Allowed Choices</h2>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <v-switch v-model="fieldData.multiple" label="Is Multiple Choices?" color="primary" hide-details class="pt-0 mt-0"></v-switch>
              </v-col>
              <v-col cols="12">
                <v-simple-table dense class="">
                  <template #default>
                    <thead>
                    <tr>
                      <th class="index">#</th>
                      <th class="">Title (*)</th>
                      <th class="">Value (*)</th>
                      <th class="actions text-center">Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="(choice, idx) in (fieldData.choices || [])" :key="idx">
                      <td class="">
                        <span class="font-weight-semibold">{{ idx + 1 }}</span>
                      </td>
                      <td class="">
                        <v-text-field placeholder="Title" v-model="choice.title" single-line hide-details dense validate-on-blur
                                      :rules="[rules.required]" />
                      </td>
                      <td class="">
                        <v-switch v-if="fieldData.type == 'boolean'" v-model="choice.value"
                                  :label="`${(choice.value || false).toString()}`" hide-details dense></v-switch>
                        <v-text-field v-else-if="fieldData.type == 'integer' || fieldData.type == 'number' || fieldData.type == 'float' || fieldData.type == 'percent'"
                               type="number"
                               placeholder="Value"
                               v-model.number="choice.value"
                               :step="fieldData.type == 'integer' || fieldData.type == 'percent'? 1: 'any'"
                               :min="fieldData.type == 'percent'? 0: null"
                               :max="fieldData.type == 'percent'? 100: null"
                               single-line hide-details dense validate-on-blur :rules="[rules.required]"
                        />
                        <v-text-field v-else placeholder="Value" v-model="choice.value"
                                      single-line hide-details dense validate-on-blur :rules="[rules.required]" />
                      </td>

                      <td class="actions text-center">
                        <v-tooltip bottom>
                          <template #activator="{ on, attrs }">
                            <v-btn v-on="on" v-bind="attrs" icon @click="insertAfter(idx)" tabindex="-1" x-small color="success"
                                   outlined class="mr-1">
                              <v-icon>{{icons.mdiPlus}}</v-icon>
                            </v-btn>
                          </template>
                          <span>Insert a row after this</span>
                        </v-tooltip>
                        <v-tooltip bottom>
                          <template #activator="{ on, attrs }">
                            <v-btn v-on="on" v-bind="attrs" icon @click="fieldData.choices.splice(idx, 1)" tabindex="-1" x-small
                                   color="error" outlined class="mr-1">
                              <v-icon>{{icons.mdiDelete}}</v-icon>
                            </v-btn>
                          </template>
                          <span>Remove</span>
                        </v-tooltip>
                        <v-tooltip bottom>
                          <template #activator="{ on, attrs }">
                            <v-btn v-on="on" v-bind="attrs" icon @click="moveUp(idx)" tabindex="-1" x-small color="secondary"
                                   outlined :disabled="idx == 0">
                              <v-icon>{{icons.mdiArrowUpThin}}</v-icon>
                            </v-btn>
                          </template>
                          <span>Move up</span>
                        </v-tooltip>
                      </td>
                    </tr>
                    <tr v-if="(fieldData.choices || []).length == 0">
                      <td colspan="5" class="text-center">
                        No Record!
                        <v-btn @click="insertAfter()" plain small color="primary">
                          <v-icon small>{{icons.mdiPlusCircleOutline}}</v-icon> Add New
                        </v-btn>
                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
          <v-btn color="primary" type="submit" :loading="saving" :disabled="!formValid">OK</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {ref, set} from '@vue/composition-api'
import {required} from "@core/utils/validation";
import {
  mdiArrowUpThin,
  mdiDelete,
  mdiPlus,
  mdiPlusCircleOutline,
  mdiLockOff,
  mdiLockOpen,
} from "@mdi/js";

export default {
  setup(props, context) {
    const isVisible = ref(false);
    const formValid = ref(false);
    const nameLocked = ref(true);
    const originFieldData = ref({});
    const fieldData = ref({choices: [], name: null});
    const saving = ref(false);

    const hide = () => {
      isVisible.value = false;
    };
    const show = (_fieldData) => {
      originFieldData.value = _fieldData;
      _fieldData = _fieldData || {};
      var clonedFieldData = Object.assign({}, _fieldData);
      clonedFieldData.choices = clonedFieldData.choices? clonedFieldData.choices.slice(): [];
      fieldData.value = clonedFieldData;
      isVisible.value = true;
      nameLocked.value = true
    };

    const save = () => {
      Object.assign(originFieldData.value, fieldData.value);
      hide();
    };

    const moveUp = (idx) => {
      if (idx <= 0) {
        return;
      }
      var origin = fieldData.value.choices[idx];
      fieldData.value.choices[idx] = fieldData.value.choices[idx - 1];
      set(fieldData.value.choices, idx - 1, origin);
    };

    const insertAfter = (idx) => {
      var newChoice = { title: "", value: "" };
      if (fieldData.value.type === 'boolean') {
        newChoice.value = false;
      }
      if (!fieldData.value.choices) {
        fieldData.value.choices = [];
      }
      if (idx === undefined) {
        fieldData.value.choices.push(newChoice);
      } else {
        fieldData.value.choices.splice(idx + 1, 0, newChoice);
      }
    };

    return {
      isVisible,
      formValid,
      nameLocked,
      saving,
      originFieldData,
      fieldData,
      hide,
      show,
      save,
      moveUp,
      insertAfter,
      rules: {
        required
      },
      icons: {
        mdiPlusCircleOutline,
        mdiPlus,
        mdiDelete,
        mdiArrowUpThin,
        mdiLockOff,
        mdiLockOpen,
      },
    }
  },
}
</script>

<style scoped>
  th.actions {
    min-width: 120px;
    width: 120px;
  }
</style>
