<template>
  <v-dialog v-model="isVisible" persistent width="500">
    <v-card>
      <v-card-title class="headline">
        Verify {{verifyType}}
      </v-card-title>
      <div v-show="stage == 'send'">
        <v-card-text>
          <p>To verify your {{verifyType}}, we are going to send a code to <strong>{{to}}</strong>.</p>
          <p><strong>Are you sure?</strong></p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" outlined @click="hide()">Cancel</v-btn>
          <v-btn color="success" @click="sendVerifyCode()" :loading="sending">Yes, Send code</v-btn>
        </v-card-actions>
      </div>
      <div v-show="stage == 'verify'">
        <v-card-text align="center">
          We have sent a code to {{to}}.<br>
          Enter 6-digit numbers received on your {{verifyType}}:
        </v-card-text>

        <div class="ma-auto position-relative" style="max-width: 300px">
          <v-otp-input v-model="code" :disabled="verifying" @finish="onFinishEnterCode" type="number" ref="otpInputRef">
          </v-otp-input>
          <v-overlay absolute :value="verifying">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
          </v-overlay>
        </div>
        <v-card-text align="center">{{expiryCounter}} seconds to expire code ...</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" outlined @click="hide()">Cancel</v-btn>
          <v-btn color="success" @click="stage = 'send'">Resend</v-btn>
        </v-card-actions>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref } from '@vue/composition-api'
import axios from "@/axios";
import EventBus from "@/EventBus";
import {notifyDefaultServerError} from "@/composables/utils";

export default {
  setup(props, context) {
    const stage = ref('send');
    const isVisible = ref(false);
    const verifying = ref(false);
    const sending = ref(false);
    const verifyType = ref('email');
    const to = ref('');
    const code = ref('');
    const otpInputRef = ref(null);
    const expiryCounter = ref(0);

    const hide = () => {
      isVisible.value = false;
    };
    const show = (type, _to) => {
      verifyType.value = type || 'email';
      to.value = _to || '';
      isVisible.value = true;
      code.value = '';
      stage.value = 'send';
    };
    const startExpiryCounter = () => {
      if (!isVisible.value) {
        expiryCounter.value = 0;
        return;
      }
      if(expiryCounter.value > 0) {
        setTimeout(() => {
          expiryCounter.value -= 1;
          startExpiryCounter()
        }, 1000)
      }
    };

    const sendVerifyCode = () => {
      sending.value = true;
      axios.post(`bycing_org/member/me/send_${verifyType.value}_verify_code`).then((response) => {
          sending.value = false;
          stage.value = 'verify';
          expiryCounter.value = response.data.expiry;
          startExpiryCounter();
          setTimeout(() => {
            otpInputRef.value.focus();
          }, 10);
        }, (error) => {
          sending.value = false;
          notifyDefaultServerError(error, true);
        }
      );
    };

    const onFinishEnterCode = (code) => {
      verifying.value = true;
      axios.post(`bycing_org/member/me/${verifyType.value}_verify`, {code: code}).then(() => {
          verifying.value = false;
          hide();
          context.emit('verify-successed', verifyType.value, to.value);
        }, (error) => {
          verifying.value = false;
          if (error.response.status === 400 ) {
            context.emit('verify-failed', verifyType.value, to.value);
          } else {
            notifyDefaultServerError(error, true);
          }
        }
      );
    };

    return {
      stage,
      isVisible,
      verifyType,
      to,
      code,
      verifying,
      sending,
      otpInputRef,
      onFinishEnterCode,
      sendVerifyCode,
      expiryCounter,
      show,
      hide
    }
  },
}
</script>
 
