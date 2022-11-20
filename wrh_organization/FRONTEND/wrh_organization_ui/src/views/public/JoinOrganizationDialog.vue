<template>
  <v-dialog v-model="isVisible" persistent max-width="700px">
    <v-card>
       <v-card-title class="headline">
         Join to <span class="ml-2 font-weight-bold"> {{ organization.name }}</span>
         <v-spacer></v-spacer>
         <v-btn icon @click="isVisible=false">
           <v-icon>{{icons.mdiClose}}</v-icon>
         </v-btn>
       </v-card-title>
      <v-card-text v-if="alreadyJoined">
        <v-alert prominent outlined type="warning" :icon="icons.mdiAlertOutline">
          <v-row align="center">
            <v-col class="grow">
              You are already joined to this organization.
            </v-col>
            <v-col class="shrink">
              <v-btn color="primary" :to="{name: $rns.DASHBOARD_ORGANIZATION_PROFILE, params: {record_id: organization.id}}">
                Go to Organization
              </v-btn>
            </v-col>
          </v-row>
        </v-alert>
      </v-card-text>
      <v-card-text v-else-if="!$store.getters.isAuthenticated" >
        <v-alert prominent outlined type="warning" :icon="icons.mdiAlertOutline">
          <v-row align="center">
            <v-col class="grow">
              You have to login first.
            </v-col>
            <v-col class="shrink">
              <v-btn color="primary" :to="{name: $rns.AUTH, query: {next: $route.fullPath}}">
                Login
                <v-icon size="20">{{icons.mdiLogin}}</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-alert>
      </v-card-text>
      <v-form v-else @submit.prevent="join" v-model="formValid">
        <v-card-text class="pr-2 pl-2">
          <v-container v-if="schema">
            <v-row>
              <v-col cols="12">
                <span class="caption font-weight-semibold">
                  Join this organization by <template v-if="schema.length"> filling out the following form and</template> clicking Join!
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
          <v-btn type="submit" color="primary" :loading="joining" :disabled="!formValid">Join</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {ref, set} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess, notifyWarn} from "@/composables/utils";
import { mdiLinkVariant, mdiAlertOutline, mdiLogin, mdiClose } from '@mdi/js';
import {required} from "@core/utils/validation";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const record = ref({});
    const isVisible = ref(false);
    const alreadyJoined = ref(false);
    const joining = ref(false);
    const schema = ref(null);
    const formValid = ref(false);
    const uiFieldsData = ref({});

    const hide = () => {
      isVisible.value = false;
    };
    const show = () => {
      loadSchema();
      getJoinStatus();
      uiFieldsData.value = {};
      joining.value = false;
      isVisible.value = true;
    };

    const loadSchema = () => {
      let params = {exfields: "member_fields_schema", fields: "member_fields_schema"};
      axios.get(`bycing_org/organization/${props.organization.id}`, {params: params}).then((response) => {
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

    const join = () => {
      joining.value = true;
      axios.post(`bycing_org/organization/${props.organization.id}/join`, record.value).then((response) => {
        joining.value = false;
        notifySuccess("You joined successfully.");
        context.emit('join-successed');
        hide();
      }, (error) => {
        joining.value = false;
        if (error.response.status === 409) {
          notifyWarn("You are already joined!");
          return context.emit('join-duplicated');
        }
        notifyDefaultServerError(error, true);
      });
    };

    const getJoinStatus = () => {
      axios.get(`bycing_org/organization/${props.organization.id}/join`).then((response) => {
        alreadyJoined.value = response.data.is_member;
      }, (error) => {
        notifyDefaultServerError(error, true);
      });
    };

    return {
      isVisible,
      joining,
      alreadyJoined,
      schema,
      record,
      uiFieldsData,
      formValid,
      show,
      hide,
      join,
      loadSchema,
      rules: {
        required
      },
      icons: {
        mdiLinkVariant,
        mdiAlertOutline,
        mdiLogin,
        mdiClose,
      }
    }
  },
}
</script>

