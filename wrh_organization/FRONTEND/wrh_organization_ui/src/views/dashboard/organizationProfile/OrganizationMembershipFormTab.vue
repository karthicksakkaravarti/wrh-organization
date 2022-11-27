<template>
  <div class="organization-member-fields-tab">
    <v-form @submit.prevent="save()" v-model="formValid">

      <v-card class="mb-1">
        <v-card-text class="d-flex align-center flex-wrap pb-0">
          <div class="d-flex align-center pb-5">
            <h2>Membership Pricing Plans</h2>
            <span class="caption ml-1">define plans of membership</span>
          </div>
        </v-card-text>
        <v-simple-table>
          <template #default>
            <thead>
            <tr>
              <th class="">#</th>
              <th class="">Period (*)</th>
              <th class="">Price (*)</th>
              <th class="">Title</th>
              <th class="plans-actions text-center">Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(field, idx) in membershipPlans" :key="idx">
              <td class="">
                <span class="font-weight-semibold">{{ idx + 1 }}</span>
              </td>
              <td class="">
                <v-select v-model="field.period" :items="$const.ORGANIZATION_MEMBERSHIP_PLAN_OPTIONS"
                          single-line hide-details dense item-text="title" item-value="value" :rules="[rules.required]">
                  <template #selection="data">
                    {{data.item.title}} <small class="caption ml-1">({{data.item.days}} days)</small>
                  </template>
                  <template #item="data">
                    {{data.item.title}} <small class="caption ml-1">({{data.item.days}} days)</small>
                  </template>
                </v-select>
              </td>
              <td class="">
                <v-text-field type="number" placeholder="Price" v-model="field.price" prefix="$" min="0"
                              single-line hide-details dense validate-on-blur/>
              </td>
              <td class="">
                <v-text-field placeholder="Title (optional)" v-model="field.title"
                              single-line hide-details dense validate-on-blur/>
              </td>
              <td class="plans-actions text-center">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn v-on="on" v-bind="attrs" icon @click="insertAfter(membershipPlans, idx, {})" tabindex="-1" x-small color="success"
                           outlined class="mr-1">
                      <v-icon>{{icons.mdiPlus}}</v-icon>
                    </v-btn>
                  </template>
                  <span>Insert a row after this</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn v-on="on" v-bind="attrs" icon @click="membershipPlans.splice(idx, 1)" tabindex="-1" x-small
                           color="error" outlined class="mr-1">
                      <v-icon>{{icons.mdiDelete}}</v-icon>
                    </v-btn>
                  </template>
                  <span>Remove</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn v-on="on" v-bind="attrs" icon @click="moveUp(membershipPlans, idx)" tabindex="-1" x-small color="secondary"
                           outlined :disabled="idx == 0">
                      <v-icon>{{icons.mdiArrowUpThin}}</v-icon>
                    </v-btn>
                  </template>
                  <span>Move up</span>
                </v-tooltip>
              </td>
            </tr>
            <tr v-if="membershipPlans.length == 0">
              <td colspan="5" class="text-center">
                No Plan Defined!
                <v-btn @click="insertAfter(membershipPlans, undefined, {})" plain small color="primary">
                  <v-icon small>{{icons.mdiPlusCircleOutline}}</v-icon> Add New
                </v-btn>
              </td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>

      </v-card>

      <v-card>
        <v-card-text class="d-flex align-center flex-wrap pb-0">
          <div class="d-flex align-center pb-5">
            <h2>Member Fields</h2>
            <span class="caption ml-1">define extra fields of organization members</span>
          </div>
        </v-card-text>
        <v-simple-table>
          <template #default>
            <thead>
            <tr>
              <th class="">#</th>
              <th class="">Title (*)</th>
              <th class="">Required?</th>
              <th class="">Private?</th>
              <th class="">Type (*)</th>
              <th class="fields-actions text-center">Actions</th>
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
                    <v-btn v-on="on" v-bind="attrs" icon @click="insertAfter(schema, idx, {type: 'string'})" tabindex="-1" x-small color="success"
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
                    <v-btn v-on="on" v-bind="attrs" icon @click="moveUp(schema, idx)" tabindex="-1" x-small color="secondary"
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
                <v-btn @click="insertAfter(schema, undefined, {type: 'string'})" plain small color="primary">
                  <v-icon small>{{icons.mdiPlusCircleOutline}}</v-icon> Add New
                </v-btn>
              </td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="secondary" outlined @click="loadRecord()">Reset</v-btn>
          <v-btn color="primary" type="submit" :loading="saving" :disabled="!formValid">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
    <organization-member-fields-setting-dialog ref="fieldsSettingDialogRef"></organization-member-fields-setting-dialog>
    <v-overlay :value="saving || loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>

import {notifyDefaultServerError, notifySuccess, randomId, refineVTableOptions} from "@/composables/utils";
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
    const membershipPlans = ref([]);
    const saving = ref(false);
    const formValid = ref(false);
    const loading = ref(false);

    const loadRecord = () => {
      loading.value = true;
      let params = {exfields: "member_fields_schema,membership_plans", fields: "member_fields_schema,membership_plans"};
      axios.get(`bycing_org/organization/${props.organization.id}`, {params: params}).then((response) => {
        loading.value = false;
        schema.value = response.data.member_fields_schema || [];
        membershipPlans.value = response.data.membership_plans || [];
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true);
      });

    };

    const moveUp = (list, idx) => {
      if (idx <= 0) {
        return;
      }
      var origin = list[idx];
      list[idx] = list[idx - 1];
      set(list, idx - 1, origin);
    };

    const insertAfter = (list, idx, defaultValue) => {
      if (idx === undefined) {
        list.push(defaultValue);
      } else {
        list.splice(idx + 1, 0, defaultValue);
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
      var memberFields = [];
      schema.value.forEach(f => {
        var r = Object.assign({}, f);
        if (!r.name) {
          r.name = fieldTitleToName(r.title);
        }
        memberFields.push(r);
      });
      var plans = [];
      membershipPlans.value.forEach(f => {
        var r = Object.assign({}, f);
        if (!r.id) {
          r.id = randomId().toString();
        }
        plans.push(r);
      });
      var postData = {
        member_fields_schema: memberFields,
        membership_plans: plans
      };
      axios.patch(`bycing_org/organization/${props.organization.id}?exfields=member_fields_schema,membership_plans&fields=member_fields_schema,membership_plans`,
          postData).then((response) => {
        saving.value = false;
        schema.value = response.data.member_fields_schema;
        membershipPlans.value = response.data.membership_plans || [];
        notifySuccess("membership fields updated successfully.");
        context.emit('save-successed');
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    onMounted(() => {
      loadRecord();
    });

    return {
      loading,
      saving,
      formValid,
      schema,
      membershipPlans,
      moveUp,
      insertAfter,
      fieldTitleToName,
      loadRecord,
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
  th.fields-actions {
    min-width: 150px;
    width: 150px;
  }

  th.plans-actions {
    min-width: 120px;
    width: 120px;
  }
</style>
