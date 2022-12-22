<template>
  <v-row>
    <v-col cols="12" v-if="!schema.length">
      <span class="caption">There is no form to fill out at this organization!</span>
    </v-col>
    <v-col cols="12" :md="f.type == 'text' || (f.choices && f.choices.length > 0)? 12: 6"
           v-for="f in schema" :key="f.name">
      <template v-if="f.choices && f.choices.length > 0">
        <p class="caption mb-0">{{ f.title }}:</p>
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
            <v-icon>{{ icons.mdiCalendar }}</v-icon>
          </template>
          <template #timeIcon>
            <v-icon>{{ icons.mdiClock }}</v-icon>
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
</template>

<script>
import {confirmedValidator, emailValidator, required} from "@core/utils/validation";
import {
  mdiCalendar,
} from "@mdi/js";

export default {
  props: {
    memberFields: {
      type: Object,
      required: true
    },
    schema: {
      type: Array,
      required: true
    }
  },
  setup(props, context) {
    return {
      rules: {
        required, confirmedValidator, emailValidator
      },
      icons: {
        mdiCalendar,
      }
    }
  }
}
</script>

<style scoped>

</style>
