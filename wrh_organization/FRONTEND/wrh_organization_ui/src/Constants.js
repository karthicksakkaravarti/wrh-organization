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

export const ORGANIZATION_TYPE_OPTIONS = [
  { value: "regional", title: "Regional", css: "success" },
  { value: "team", title: "Team", css: "primary" },
  { value: "advocacy_volunteer", title: "Advocacy, Volunteer", css: "info" },
];
export const ORGANIZATION_TYPE_MAP = {};
ORGANIZATION_TYPE_OPTIONS.forEach(function(v) {
  ORGANIZATION_TYPE_MAP[v.value] = v;
});

