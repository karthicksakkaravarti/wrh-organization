<template>
  <div>
    <v-card v-if="organization">
      <v-card-title class="headline" :class="{'pt-1 pb-1': organization.logo}">
        {{alreadyJoined? 'Re-Join': 'Join'}} to <span class="ml-2 font-weight-bold"> {{ organization.name }}</span>
        <v-spacer></v-spacer>
        <v-avatar size="60" class="avatar-center" v-if="organization.logo" color="black">
          <v-img :src="organization.logo"></v-img>
        </v-avatar>
      </v-card-title>
      <v-divider></v-divider>

      <v-form @submit.prevent="onSubmit()" v-model="formValid" class="mt-3">
        <v-card-text>
          <template v-if="$store.getters.isAuthenticated">
            <h3 class="mb-2">
              1. You Have an account on WRH. <v-icon color="success">{{ icons.mdiAccountCheck }}</v-icon>
              <span class="caption">
                (logged in by <span class="primary--text font-weight-bold">{{$store.state.currentUser.username}}</span>)
              </span>
            </h3>

          </template>
          <template v-else-if="accountMode == 'sign-up'">
            <h3 class="mb-2">
              1. Sign up on WRH:
              <span class="caption">
                (already have an account? <a href="javascript:" @click="accountMode='sign-in'; isPasswordVisible=false">Sign in</a>)
              </span>
            </h3>
            <v-row>
              <v-col cols="12" class="pb-0">
                <v-text-field v-model="registerForm.email" outlined :append-icon="icons.mdiEmailOutline" label="E-mail"
                              placeholder="E-mail" hide-details
                              :rules="[rules.required, rules.emailValidator]" dense>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="pb-0">
                <v-text-field v-model="registerForm.first_name" outlined label="First Name" placeholder="First Name"
                  hide-details :rules="[rules.required]" dense>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="pb-0">
                <v-text-field v-model="registerForm.last_name" outlined label="Last Name" placeholder="Last Name"
                              hide-details :rules="[rules.required]" dense>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="pb-0">
                <v-text-field v-model="registerForm.password" outlined :type="isPasswordVisible ? 'text' : 'password'"
                  label="Password" placeholder="Password"
                              :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline" class=""
                  hint="Password should contains at least 1 digit with min 8 chars" persistent-hint
                              :rules="[rules.required]" dense @click:append="isPasswordVisible = !isPasswordVisible">
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="pb-0">
                <v-text-field v-model="registerForm.confirm_password" outlined
                              :type="isPasswordVisible ? 'text' : 'password'" label="Confirm Password"
                              placeholder="Confirm Password" class=""
                  :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline"
                  :rules="[rules.required, rules.confirmedValidator(registerForm.confirm_password, registerForm.password)]"
                  dense @click:append="isPasswordVisible = !isPasswordVisible"
                >
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="pb-0">
                <v-select outlined v-model="registerForm.gender" :items="$const.GENDER_OPTIONS" item-text="title"
                    item-value="value" label="Gender" dense hide-details :rules="[rules.required]">
                </v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu ref="birthDateMenuRef" v-model="showBirthDateMenu" :close-on-content-click="false"
                        transition="scale-transition" offset-y min-width="auto">
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field v-model="registerForm.birth_date" label="Birth Date" :append-icon="icons.mdiCalendar"
                      readonly v-bind="attrs" v-on="on" :rules="[rules.required]" outlined hide-details
                      dense>
                    </v-text-field>
                  </template>

                  <v-date-picker ref="birthDatePickerRef" v-model="registerForm.birth_date"
                                 :active-picker.sync="birthDateActivePicker" :max="new Date().toISOString().slice(0, 10)"
                                 min="1940-01-01" color="primary" @change="(d) => {$refs.birthDateMenuRef.save(d)}">
                  </v-date-picker>
                </v-menu>
              </v-col>
            </v-row>
          </template>
          <template v-else>
            <h3 class="mb-2">
              1. Sign in on WRH:
              <span class="caption">
                (don't have account? <a href="javascript:" @click="accountMode='sign-up'; isPasswordVisible=false">Sign up</a>)
              </span>
            </h3>
            <v-text-field v-model="loginForm.username" outlined dense label="Username" placeholder="Username"
                          hide-details class="mb-2" :rules="[rules.required]"></v-text-field>

            <v-text-field v-model="loginForm.password" outlined dense :type="isPasswordVisible ? 'text' : 'password'"
                          :append-icon="isPasswordVisible ? icons.mdiEyeOffOutline : icons.mdiEyeOutline"
                          @click:append="isPasswordVisible = !isPasswordVisible" class="mb-2"
                          label="Password" placeholder="Password" hide-details :rules="[rules.required]"></v-text-field>
            <v-btn
              block
              type="button"
              color="primary"
              class=""
              :loading="logining"
              @click="login()"
            >
              Login
            </v-btn>
          </template>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text v-if="schema" :class="{disabled: accountMode == 'sign-in'}">
          <h3 class="mb-2">
            2. Fill out organization form:
          </h3>
          <member-fields-schema-cmp :schema="schema" :member-fields="memberFields"></member-fields-schema-cmp>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text :class="{disabled: accountMode == 'sign-in'}">
          <h3 class="mb-2">
            3. Choose a membership plan:
          </h3>
          <v-alert v-if="membershipPlans && !membershipPlans.length" dense text color="warning" class="mt-2 text-center">
            <p>No membership plan defined on this organiztion.</p>
            <p>You cannot join!</p>
          </v-alert>
          <v-alert dense color="error" text class="" v-if="currentMembership && currentMembership.is_admin">
            <p class="mb-1">
              You are an <v-chip small color="info">Admin</v-chip> member of this organization.
            </p>
            <p class="mb-1">Your membership plan won't expire unless the organization drops your grant!</p>
            <p class="mb-1">
              You dont need to renew your membership!
            </p>
          </v-alert>
          <v-alert dense color="info" text class="" v-else-if="alreadyJoined && !currentMembership.is_admin">
            <p class="mb-1">
              You have an <v-chip small color="warning" v-if="currentMembership.is_expiring">Expiring</v-chip> active plan.
            </p>
            <p class="mb-1">Your plan date will be extended to the newly selected plan if you rejoin again.</p>
            <p class="mb-1">
              Your current plan expires on: <strong>{{currentMembership.exp_date? $utils.formatDate(currentMembership.exp_date, 'MMM D, YYYY'): 'Never!'}}</strong>
            </p>
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
        <v-card-text :class="{disabled: accountMode == 'sign-in'}">
          <h5 class="mb-2">
            If you would like, you can donate us!
          </h5>
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
        <v-card-text v-if="membershipPrice" :class="{disabled: accountMode == 'sign-in'}">
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
        <v-divider></v-divider>

        <v-card-actions>
        <turnstile-component v-if="turnstileSiteKey" ref="turnstileCmpRef"
                             id="signup-and-join-turnstile-widget"
                             :sitekey="turnstileSiteKey"
                             @verify="onVerifyTurnstile" @expire="$refs.turnstileCmpRef.reset()" @fail="onFailTurnstile"
                             @timeout="onFailTurnstile"></turnstile-component>

          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined :to="{name: $rns.PUBLIC_ORG_PROFILE, params:{record_id: organization.id}}">Cancel</v-btn>
          <v-btn type="submit" color="primary" :loading="joining"
                 :disabled="!formValid || (!!membershipPrice && !stripeElementIsReady)|| !selectedPlan || accountMode=='sign-in' || !turnstileToken || (currentMembership && currentMembership.is_admin)">
            {{alreadyJoined? 'Re-Join': 'Join'}}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </div>
</template>

<script>
import {
  mdiEmailOutline,
  mdiPhoneOutline,
  mdiCalendar,
  mdiEyeOutline,
  mdiEyeOffOutline,
  mdiLinkVariant,
  mdiAlertOutline,
  mdiLogin,
  mdiClose,
  mdiAccountCheck,
} from '@mdi/js'
import {computed, onMounted, onUnmounted, ref, set, watch} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifyError, notifySuccess, notifyWarn} from "@/composables/utils";
import {required, confirmedValidator, emailValidator} from "@core/utils/validation";
import { StripeElementCard } from '@vue-stripe/vue-stripe';
import {useRouter} from "@core/utils";
import store from "@/store";
import {routeNames} from "@/router";
import EventBus from "@/EventBus";
import TurnstileComponent from "@/components/TurnstileComponent.vue";
import MemberFieldsSchemaCmp from "@/views/public/MemberFieldsSchemaCmp.vue";

export default {
  components: {MemberFieldsSchemaCmp, TurnstileComponent, StripeElementCard},
  props: {
  },
  setup(props, context) {
    const { route, router } = useRouter();
    const logining = ref(false);
    const turnstileToken = ref({});
    const showBirthDateMenu = ref(false);
    const birthDateActivePicker = ref(null);
    const birthDatePickerRef = ref(null);
    const isPasswordVisible = ref(false);
    const organization = ref({});
    const memberFields = ref({});
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
    const accountMode = ref('sign-up');
    const loginForm = ref({});
    const registerForm = ref({});
    const turnstileSiteKey = ref(null);

    const orgId = route.value.params.record_id;

    const membershipPrice = computed(() => ((selectedPlan.value || {}).price || 0) * 1 + (donateValue.value || 0) * 1);
    const alreadyJoined = computed(() => (!!currentMembership.value && !currentMembership.value.is_expired));

    watch(showBirthDateMenu, val => {
      val && setTimeout(() => (birthDateActivePicker.value = 'YEAR'))
    });

    onMounted(() => {
      loadGlobalConfKeys();
      loadOrganization();
      getCurrentPlan();
      EventBus.on("user:change-state", onUpdateCurrentUser);
    });

    onUnmounted(() => {
      EventBus.off("user:change-state", onUpdateCurrentUser);
    });

    const loadGlobalConfKeys = () => {
      axios.get("cycling_org/global_conf").then(
        response => {
          turnstileSiteKey.value = response.data.TURNSTILE_SITE_KEY;
          stripePubKey.value = response.data.STRIPE_PUBLISHABLE_KEY;
        },
        error => {
          notifyDefaultServerError(error, true);
        }
      );
    };

    const onVerifyTurnstile = (token) => {
      turnstileToken.value = token;
    };

    const onFailTurnstile = () => {
      notifyError('Something is wrong. refresh the page and try again!')
    };

    const onUpdateCurrentUser = () => {
      getCurrentPlan();
    };

    const login = () => {
      logining.value = true;
      axios.post("account/session", loginForm.value).then((response) => {
        store.commit('currentUser', response.data);
        logining.value = false;
        accountMode.value = null;
        loginForm.value = {};
      }, (error) => {
        logining.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const loadOrganization = () => {
      let params = {exfields: "member_fields_schema,membership_plans"};
      axios.get(`cycling_org/organization/${orgId}`, {params: params}).then((response) => {
        organization.value = response.data;
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
        turnstile_token: turnstileToken.value,
        membership: {
          member_fields: memberFields.value, token: token, plan_id: selectedPlan.value.id, donation: donateValue.value
        }
      };
      if (accountMode.value === 'sign-up') {
        data.register = registerForm.value;
      }
      axios.post(`cycling_org/organization/${orgId}/signup_and_join`, data).then((response) => {
        joining.value = false;
        var msg = `You ${alreadyJoined.value? 'Renewed membership': 'Joined'} successfully.`;
        if (!response.data._member._user.is_active) {
          msg += ' We Sent you an activation email. please activate your account!'
        }
        notifySuccess(msg);
        router.push({name: routeNames.PUBLIC_ORG_PROFILE, params: {record_id: orgId}});
      }, (error) => {
        joining.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const tokenCreated = (token) => {
      join(token.id);
    };

    const getCurrentPlan = () => {
      if (!store.getters.isAuthenticated) {
        currentMembership.value = null;
        memberFields.value = {};
        return
      }
      axios.get(`cycling_org/organization/${orgId}/join`).then((response) => {
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
      turnstileToken,
      logining,
      showBirthDateMenu,
      birthDateActivePicker,
      birthDatePickerRef,
      accountMode,
      loginForm,
      registerForm,
      organization,
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
      loadGlobalConfKeys,
      turnstileSiteKey,
      onVerifyTurnstile,
      onFailTurnstile,
      join,
      login,
      onSubmit,
      loadOrganization,
      tokenCreated,
      isPasswordVisible,
      rules: {
        required, confirmedValidator, emailValidator
      },
      icons: {
        mdiLinkVariant,
        mdiAlertOutline,
        mdiLogin,
        mdiClose,
        mdiEyeOutline,
        mdiEyeOffOutline,
        mdiCalendar,
        mdiPhoneOutline,
        mdiEmailOutline,
        mdiAccountCheck,
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
  .v-card__text.disabled {
    opacity: 0.3;
    pointer-events: none;
  }

</style>
