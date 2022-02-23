const countryList = require('country-list');

export const UI_VERSION_HEADER_NAME = "x-ui-version";

export const GENDER_OPTIONS = [
  { value: "m", title: "Male" },
  { value: "f", title: "Female" },
  { value: "o", title: "Other" },
  { value: "u", title: "Unknown" }
];
export const GENDER_MAP = {};
GENDER_OPTIONS.forEach(function(v) {
  GENDER_MAP[v.value] = v;
});

export const COUNTRY_OPTIONS = countryList.getData();
export const COUNTRY_MAP = {};
COUNTRY_OPTIONS.forEach(function(v) {
  COUNTRY_MAP[v.code] = v;
});
