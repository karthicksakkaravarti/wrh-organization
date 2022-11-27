<template>
  <v-dialog v-model="isVisible" persistent max-width="700px">
    <v-card>
       <v-card-title class="headline">
         {{alreadyJoined? 'Re-Join': 'Join'}} to <span class="ml-2 font-weight-bold"> {{ organization.name }}</span>
         <v-spacer></v-spacer>
         <v-btn icon @click="isVisible=false">
           <v-icon>{{icons.mdiClose}}</v-icon>
         </v-btn>
       </v-card-title>
      <v-card-text v-if="alreadyJoined && !currentMembership.is_admin">
        <v-alert dense color="info" text class="mb-0">
          <p class="mb-1">
            You have an <v-chip small color="warning" v-if="currentMembership.is_expiring">Expiring</v-chip> active plan.
          </p>
          <p class="mb-1">Your plan date will be extended to the newly selected plan if you rejoin again.</p>
          <p class="mb-1">
            Your current plan expires on: <strong>{{currentMembership.exp_date? $utils.formatDate(currentMembership.exp_date, 'MMM D, YYYY'): 'Never!'}}</strong>
          </p>
        </v-alert>
      </v-card-text>
      <v-card-text v-if="!$store.getters.isAuthenticated" >
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
      <v-card-text v-else-if="currentMembership && currentMembership.is_admin">
        <v-alert dense color="info" text class="mb-0">
          <p class="mb-1">
            You are an <v-chip small color="warning">Admin</v-chip> member of this organization.
          </p>
          <p class="mb-1">Your membership plan will not expire, unless the organization drop your grant!</p>
          <p class="mb-1">
            You dont need to renew your membership!
          </p>
        </v-alert>
      </v-card-text>
      <v-form v-else @submit.prevent="onSubmit()" v-model="formValid">
        <v-card-text class="pr-2 pl-2" v-if="schema">
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="caption font-weight-semibold">
                  Join this organization by <template v-if="schema.length"> filling out the following form and</template> choosing your plan!
                </span>
              </v-col>
              <v-col cols="12" :md="f.type == 'text' || (f.choices && f.choices.length > 0)? 12: 6"
                     v-for="f in schema" :key="f.name">
                <template v-if="f.choices && f.choices.length > 0">
                  <p class="caption mb-0">{{f.title}}:</p>
                  <div v-if="f.multiple" class="d-flex flex-wrap demo-space-x mt-0">
                    <v-checkbox v-for="(c, cIdx) in f.choices" v-model="memberFields[f.name]"
                                class="mt-0 mb-0 pt-0" :label="c.title" :value="c.value" :key="cIdx" hide-details></v-checkbox>
                  </div>
                  <v-radio-group v-else v-model="memberFields[f.name]" hide-details class="mt-0"
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
                      v-model.number="memberFields[f.name]"
                      :label="f.title"
                      type="number"
                      :step="f.type=='integer'? 1: 'any'"
                      :rules="f.required? [rules.required]: []"
                  ></v-text-field>
                </template>
                <template v-else-if="f.type=='percent'">
                  <v-text-field
                      dense
                      v-model.number="memberFields[f.name]"
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
                      v-model="memberFields[f.name]"
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
                          v-model="memberFields[f.name]"
                          :label="f.title"
                          :rules="f.required? [rules.required]: []"
                          class="pt-0 mt-0 mb-5"
                          :append-icon="f.type=='time'? icons.mdiClockOutline: icons.mdiCalendar"
                          v-bind="attrs"
                          v-on="on"
                          readonly>
                      </v-text-field>
                    </template>
                    <v-time-picker v-if="f.type=='time'" v-model="memberFields[f.name]" color="primary"
                                   @click:minute="uiFieldsData[`menu__${f.name}`] = false"></v-time-picker>
                    <v-date-picker v-else v-model="memberFields[f.name]" color="primary"
                                   @input="uiFieldsData[`menu__${f.name}`] = false"></v-date-picker>
                  </v-menu>
                </template>
                <template v-else-if="f.type=='datetime'">
                  <v-datetime-picker v-model="memberFields[f.name]" :label="f.title"
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
                      v-model="memberFields[f.name]"
                      :label="f.title"
                      :rules="f.required? [rules.required]: []"
                      rows="2"
                  ></v-textarea>
                </template>
                <template v-else>
                  <v-text-field
                      dense
                      v-model.trim="memberFields[f.name]"
                      :label="f.title"
                      :rules="f.required? [rules.required]: []"
                      type="text"
                  ></v-text-field>
                </template>
              </v-col>
            </v-row>
          </v-container>
          <v-divider></v-divider>
        </v-card-text>
        <v-card-text>
          <h3 class="mb-2">
            Choose a membership plan:
          </h3>
          <v-alert v-if="membershipPlans && !membershipPlans.length" dense text color="warning" class="mt-2 text-center">
            <p>No membership plan defined on this organiztion.</p>
            <p>You cannot join!</p>
          </v-alert>
          <v-row class="mb-1">
            <v-col cols="12" md="4" v-for="plan in (membershipPlans || [])" :key="plan.id">
              <v-card @click="selectedPlan=plan"
                      :elevation="selectedPlan && selectedPlan.id==plan.id? 10: 6"
                      :class="{'selected-plan': selectedPlan && selectedPlan.id==plan.id}"
                      :color="(selectedPlan && selectedPlan.id==plan.id)? 'warning': 'light'"
              >
                <v-card-text>
                  <v-chip color="info" label small
                          class="current-plan-label"
                          v-if="currentMembership && currentMembership.membership_plan && (currentMembership.membership_plan.id == plan.id)">Current</v-chip>
                  <div class="text-center">
                    <h1 class="text-2xl font-weight-medium">
                      {{ ($const.ORGANIZATION_MEMBERSHIP_PLAN_MAP[plan.period] || {}).title || plan.period }}
                    </h1>
                    <p>{{ plan.title || '-' }}</p>
                  </div>
                  <div class="text-center">
                    <sup class="text-sm text-primary">$</sup>
                    <span class="pricing-basic-value text-5xl primary--text font-weight-semibold">
                      {{plan.price}}
                    </span>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text>
          <h3 class="mb-2">
            If you would like, you can donate us!
          </h3>
          <v-row>
            <v-col cols="12">
              <v-text-field type="number" label="Donate value:" v-model="donateValue" prefix="$" min="0" outlined dense hide-details>
                <template v-slot:append-outer>
                  <v-btn-toggle v-model="donateValue" class="donate-btn-group" ref="donateBtnGroupRef">
                    <v-btn :value="p" v-for="p in [5, 10, 20, 50, 100]" :key="p" color="success" outlined class="donate-btn">
                      ${{p}}
                    </v-btn>
                  </v-btn-toggle>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text v-if="membershipPrice">
          <v-row class="mb-1">
            <v-col cols="12">
              <h4>You will be charged <strong class="error--text">${{membershipPrice}}</strong> to join this organization:</h4>
            </v-col>
          </v-row>
          <stripe-element-card v-if="stripePubKey"
                               ref="cardPaymentRef"
                               :pk="stripePubKey"
                               @token="tokenCreated"
                               @error="v => joining = false"
                               @element-ready="() => stripeElementIsReady=true"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined @click="hide()">Cancel</v-btn>
          <v-btn type="submit" color="primary" :loading="joining"
                 :disabled="!formValid || (!!membershipPrice && !stripeElementIsReady)|| !selectedPlan">
            {{alreadyJoined? 'Re-Join': 'Join'}}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {computed, ref, set} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess, notifyWarn} from "@/composables/utils";
import { mdiLinkVariant, mdiAlertOutline, mdiLogin, mdiClose } from '@mdi/js';
import {required} from "@core/utils/validation";
import { StripeElementCard } from '@vue-stripe/vue-stripe';

export default {
  components: {StripeElementCard},
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const memberFields = ref({});
    const isVisible = ref(false);
    const currentMembership = ref(null);
    const selectedPlan = ref(null);
    const joining = ref(false);
    const schema = ref(null);
    const donateValue = ref(null);
    const stripePubKey = ref(null);
    const membershipPlans = ref(null);
    const formValid = ref(false);
    const uiFieldsData = ref({});
    const cardPaymentRef = ref(null);
    const stripeElementIsReady = ref(false);

    const membershipPrice = computed(() => ((selectedPlan.value || {}).price || 0) * 1 + (donateValue.value || 0) * 1);
    const alreadyJoined = computed(() => (!!currentMembership.value && !currentMembership.value.is_expired));

    const hide = () => {
      selectedPlan.value = null;
      donateValue.value = null;
      isVisible.value = false;
    };
    const show = () => {
      loadStripPubKey();
      loadOrgRecord();
      getCurrentPlan();
      uiFieldsData.value = {};
      joining.value = false;
      isVisible.value = true;
    };

    const loadStripPubKey = () => {
      axios.get("bycing_org/global_conf/STRIPE_PUBLISHABLE_KEY").then(
        response => {
          stripePubKey.value = response.data;
        },
        error => {
          notifyDefaultServerError(error, true);
        }
      );
    };

    const loadOrgRecord = () => {
      let params = {exfields: "member_fields_schema,membership_plans", fields: "member_fields_schema,membership_plans"};
      axios.get(`bycing_org/organization/${props.organization.id}`, {params: params}).then((response) => {
        membershipPlans.value = response.data.membership_plans || [];
        schema.value = response.data.member_fields_schema || [];
        schema.value.forEach(r => {
          if (r.multiple) {
            set(memberFields.value, r.name, memberFields.value[r.name] || []);
          }
        });

      }, (error) => {
        notifyDefaultServerError(error, true);
      });

    };

    const onSubmit = () => {
      if (membershipPrice.value) {
        joining.value = true;
        cardPaymentRef.value.submit();
      } else {
        join();
      }
    };

    const join = (token) => {
      if (membershipPrice.value && !token) {
        return notifyWarn("Payment is required!")
      }
      if (!selectedPlan.value) {
        return notifyWarn("Select a membership plan!")
      }
      joining.value = true;
      var data = {
        member_fields: memberFields.value, token: token, plan_id: selectedPlan.value.id, donation: donateValue.value
      };
      axios.post(`bycing_org/organization/${props.organization.id}/join`, data).then((response) => {
        joining.value = false;
        notifySuccess(`You ${alreadyJoined.value? 'Renewed membership': 'Joined'} successfully.`);
        context.emit('join-successed');
        hide();
      }, (error) => {
        joining.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const tokenCreated = (token) => {
      join(token.id);
    };

    const getCurrentPlan = () => {
      axios.get(`bycing_org/organization/${props.organization.id}/join`).then((response) => {
        currentMembership.value = response.data;
        memberFields.value = Object.assign({}, memberFields.value, currentMembership.value.member_fields)
      }, (error) => {
        if (error.response.status === 404 ) {
          currentMembership.value = null
        } else {
          notifyDefaultServerError(error, true);
        }
      });
    };

    return {
      isVisible,
      joining,
      alreadyJoined,
      schema,
      membershipPlans,
      memberFields,
      uiFieldsData,
      cardPaymentRef,
      stripeElementIsReady,
      membershipPrice,
      stripePubKey,
      formValid,
      currentMembership,
      selectedPlan,
      donateValue,
      loadStripPubKey,
      show,
      hide,
      join,
      onSubmit,
      loadOrgRecord,
      tokenCreated,
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

<style scoped>
  .current-plan-label {
    position: absolute;
    top: 0;
    left: 0;
  }
  .donate-btn-group {
    margin-top: -7px;
    margin-left: -7px;
  }

  .donate-btn {
    
  }

</style>
