<template>
  <div class="organization-member-fields-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <h2>Member Fields</h2>
          <span class="caption ml-1">define extra fields of organization members</span>
        </div>
      </v-card-text>
      <v-form @submit.prevent="save()" v-model="formValid">
        <v-simple-table>
          <template #default>
            <thead>
            <tr>
              <th class="">#</th>
              <th class="">Title (*)</th>
              <th class="">Required?</th>
              <th class="">Private?</th>
              <th class="">Type (*)</th>
              <th class="actions text-center">Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(field, idx) in schema" :key="idx">
              <td class="">
                <span class="font-weight-semibold">{{ idx + 1 }}</span>
              </td>
              <td class="">
                <v-text-field placeholder="Title" v-model="field.title" single-line hide-details dense validate-on-blur
                              :rules="[rules.required]" />
              </td>
              <td class="">
                 <v-checkbox v-model="field.required" hide-details></v-checkbox>
              </td>
              <td class="">
                 <v-checkbox v-model="field.private" hide-details></v-checkbox>
              </td>
              <td class="">
                <v-select v-model="field.type" :items="$const.MEMBER_FIELDS_SCHEMA_TYPE_OPTIONS"
                          single-line hide-details dense item-text="title" item-value="value" :rules="[rules.required]">
                </v-select>
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
                    <v-btn v-on="on" v-bind="attrs" icon @click="$refs.fieldsSettingDialogRef.show(field)" tabindex="-1" x-small color="primary"
                           outlined class="mr-1">
                      <v-icon>{{icons.mdiCogOutline}}</v-icon>
                    </v-btn>
                  </template>
                  <span>More Settings</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn v-on="on" v-bind="attrs" icon @click="schema.splice(idx, 1)" tabindex="-1" x-small
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
            <tr v-if="schema.length == 0">
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
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="secondary" outlined @click="loadSchema()">Reset</v-btn>
          <v-btn color="primary" type="submit" :loading="saving" :disabled="!formValid">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
    <organization-member-fields-setting-dialog ref="fieldsSettingDialogRef"></organization-member-fields-setting-dialog>
    <v-overlay :value="saving || loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>

import {notifyDefaultServerError, notifySuccess, refineVTableOptions} from "@/composables/utils";
import axios from "@/axios";
import {onMounted, ref, set} from "@vue/composition-api";
import {required} from "@core/utils/validation";
import {
  mdiPlusCircleOutline,
  mdiPlus,
  mdiCogOutline,
  mdiDelete,
  mdiArrowUpThin,
} from "@mdi/js"
import OrganizationMemberFieldsSettingDialog
  from "@/views/dashboard/organizationProfile/OrganizationMemberFieldsSettingDialog";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  components: {OrganizationMemberFieldsSettingDialog},
  setup(props, context) {
    const schema = ref([]);
    const saving = ref(false);
    const formValid = ref(false);
    const loading = ref(false);

    const loadSchema = () => {
      loading.value = true;
      let params = {exfields: "member_fields_schema", fields: "member_fields_schema"};
      axios.get(`bycing_org/organization/${props.organization.id}`, {params: params}).then((response) => {
        loading.value = false;
        schema.value = response.data.member_fields_schema || [];
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true);
      });

    };

    const moveUp = (idx) => {
      if (idx <= 0) {
        return;
      }
      var origin = schema.value[idx];
      schema.value[idx] = schema.value[idx - 1];
      set(schema.value, idx - 1, origin);
    };

    const insertAfter = (idx) => {
      if (idx === undefined) {
        schema.value.push({ type: "string" });
      } else {
        schema.value.splice(idx + 1, 0, { type: "string" });
      }
    };

    const fieldTitleToName = (title) => {
      if (!title) {
        return title;
      }
      title = title.trim().toLowerCase().split(/\W+/);
      if (!title[title.length -1]) {
        title = title.slice(0, -1)
      }
      return title.join("_");
    };

    const save = () => {
      saving.value = true;
      var postData = [];
      schema.value.forEach(f => {
        var r = Object.assign({}, f);
        if (!r.name) {
          r.name = fieldTitleToName(r.title);
        }
        postData.push(r);
      });
      axios.patch(`bycing_org/organization/${props.organization.id}?exfields=member_fields_schema&fields=member_fields_schema`,
          {member_fields_schema: postData}).then((response) => {
        saving.value = false;
        schema.value = response.data.member_fields_schema;
        notifySuccess("member fields saved successfully.");
        context.emit('save-successed');
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    onMounted(() => {
      loadSchema();
    });

    return {
      loading,
      saving,
      formValid,
      schema,
      moveUp,
      insertAfter,
      fieldTitleToName,
      loadSchema,
      save,
      rules: {
        required
      },
      icons: {
        mdiPlusCircleOutline,
        mdiPlus,
        mdiCogOutline,
        mdiDelete,
        mdiArrowUpThin,
      }
    }
  },
}
</script>

<style scoped>
  th.actions {
    min-width: 150px;
    width: 150px;
  }
</style>
