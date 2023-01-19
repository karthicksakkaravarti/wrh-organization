import * as momentLib from "moment";
import { createToastInterface } from "vue-toastification";
import {Config} from "@/Config";
import {conformToMask} from 'text-mask-core';
import {countries} from "@/composables/countries";
import _ from "lodash";

export const moment = momentLib;
export const lodash = _;
export const countryPhoneCodes = {};
countries.forEach(v => {
  if (!v.phone_code) return;
  var codes = v.phone_code.split(",");
  codes.forEach(c => {
    countryPhoneCodes[c] = v.code;
  })
});


export const toast = createToastInterface({
  transition: "Vue-Toastification__fade",
  maxToasts: 20,
  newestOnTop: true
});

export const getQueryParams = (params, url) => {
  let href = url;
  let reg = new RegExp("[?&]" + params + "=([^&#]*)", "i");
  let queryString = reg.exec(href);
  return queryString ? queryString[1] : null;
};

export const getParameterByName = (name, url) => {
  name = name.replace(/[[]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
};

export const addQSParm = (url, name, value, override) => {
  override = override === undefined ? true : override;
  if (value instanceof Array) {
    value.forEach(v => {
      url = addQSParm(url, name, v, false);
    })
    return url;
  }
  var re = new RegExp("([?&]" + name + "=)[^&]+", "");

  function add(sep) {
    url += sep + name + "=" + encodeURIComponent(value);
  }

  function change() {
    url = url.replace(re, "$1" + encodeURIComponent(value));
  }

  if (url.indexOf("?") === -1) {
    add("?");
  } else {
    if (override && re.test(url)) {
      change();
    } else {
      add("&");
    }
  }
  return url;
};

export const combineURLs = (baseURL, relativeURL, getParams) => {
  var url = baseURL.replace(/\/+$/, "");
  if (relativeURL) {
    url = url + "/" + relativeURL.replace(/^\/+/, "");
  }
  _.each(getParams || {}, function(v, k) {
    url = addQSParm(url, k, v);
  });
  return url;
};

export const randomId = (n) => {
  n = n || 10;
  return Math.floor(Math.random() * Math.pow(10, n) + 1);
};

export const jsonParseSafe = (s, _default) => {
  try {
    return JSON.parse(s)
  } catch (e) {
    return _default;
  }
};

export const humanizeDate = (dt) => {
  if (!dt) {
      return;
  }
  dt = moment(dt);
  var now = moment(),
      format;
  if (now.year() === dt.year() && now.month() === dt.month() && now.date() === dt.date()) {
      format = 'h:mm a';
  } else if (now.year() === dt.year()) {
      format = 'MMM DD';
  } else {
      format = 'MMM D YYYY';
  }
  return dt.format(format)
};

export const formatDate = (value, fmt, _default) => {
  _default = _default === undefined ? "" : _default;
  if (!value) {
    return _default;
  }
  fmt = fmt === undefined ? "MMM D, YYYY HH:mm" : fmt;
  return moment(value).format(fmt);
};

export const formatTime = (value, fmt, _default) => {
  _default = _default === undefined ? "" : _default;
  if (!value) {
    return _default;
  }
  fmt = fmt === undefined ? "hh:mm A" : fmt;
  return moment.utc(`2000-01-01T${value}Z`).format(fmt);
};

export const closeAllNotify = () => {
  toast.clear();
};

export const notifyMessage = (msg, opts) => {
  opts = Object.assign({
    position: "top-center",
    timeout: 5000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: true,
    closeButton: "button",
    icon: true,
    rtl: false
  },opts || {});
  toast(msg, opts);
};

export const notifySuccess = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "success",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyError = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "error",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyWarn = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "warning",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyInfo = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "info",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyDefaultServerSuccess = (response, duration) => {
  duration = duration !== undefined ? duration : 5000;
  var defaultMsg = "Operation done successfully";
  notifySuccess(response.statusText || defaultMsg, duration);
};

export const notifyDefaultServerError = (error, showDetail, duration, extra_message) => {
  var response = error.response || error.request;
  var msg;
  if (response.status === 401) {
    return;
  }
  if (response.status === 502) {
    msg = `<strong class="text-dark">Server Temporary Unavailable!</strong>&nbsp; Down for maintenance! We will be back shortly.`
    return notifyError(msg, duration || 0);
  }
  duration = duration !== undefined ? duration : 50000;
  showDetail = showDetail !== undefined ? showDetail : true;
  notifyError({
    render: (h) => {
      var els = [];
      if (!response || response.status <= 0) {
        els.push(h('strong', 'Server Connection Error'));
      } else {
        els.push(h('strong', `${response.status}: ${response.statusText} | `));
        var jData = safeFromJson(response.data);
        if (showDetail && jData) {
          els.push(h('p', prettifyError(response.data)));
        }
        if (extra_message) {
          els.push(h('p', extra_message));
        }
      }
      return h('div', els);
    }
  }, duration);
};

export const safeFromJson = (s, nullIfFail) => {
  if (typeof s === "object") {
    return s;
  }
  nullIfFail = nullIfFail === undefined;
  try {
    return JSON.parse(s);
  } catch (e) {
    return nullIfFail ? null : s;
  }

};

export const prettifyError = (data) => {
  return JSON.stringify(data)
    .replace(/\[|\]|\}|\{/g, "")
    .replace(/\\"/g, '"')
    .replace('"non_field_errors":', "");
};

export const removeTrailingZero = (n, decimalPoint) => {
  if (n === undefined || n === null) {
    return n;
  }
  if (typeof n === "number" && decimalPoint !== undefined) {
    n = n.toFixed(decimalPoint);
  }
  if (typeof n !== "string") {
    n = n + "";
  }
  return n.replace(/(\.[0-9]*[1-9])0+$|\.0*$/, "$1");
};

export const ageFormat = (birth_date, showLabel, decimalCount) => {
  showLabel = showLabel === undefined ? true : showLabel;
  var age = moment().diff(birth_date, "years", !!decimalCount);
  age = decimalCount? removeTrailingZero(age, decimalCount): Math.floor(age);
  return `${age}${
    showLabel ? " years" : ""
  }`;
};

export const refineVTableOptions = (options) => {
  const newOpt = Object.assign({}, options);
  newOpt.page_size = newOpt.itemsPerPage === -1? 0: newOpt.itemsPerPage;
  newOpt.order_by = (newOpt.sortBy || []).map((o, i) => {
    return ((newOpt.sortDesc || [])[i]? '-': '') + o;
  }).join(',');
  ["itemsPerPage", "sortBy", "sortDesc", "groupBy", "groupDesc", "mustSort", "multiSort"].forEach(o => {
    delete newOpt[o];
  });
  return newOpt;
};

export const internationalPhoneMask = function(rawValue) {
  var number = (rawValue || "").replace(/\D/g, ""),
    codesDigit = ["+", /\d/];
  if (!rawValue.startsWith("+")) {
    codesDigit = (Config.DEFAULT_PHONE_COUNTRY_CODE || "+1").split("");
  } else if (number) {
    var countryCode,
      i = 1;
    while (i <= number.length && i <= 5) {
      countryCode = countryPhoneCodes[number.slice(0, i)];
      if (countryCode) {
        break;
      }
      codesDigit.push(/\d/);
      i++;
    }
    if (!countryCode) {
      codesDigit = ["+", /\d/];
    }
  }
  return codesDigit.concat([" ", "(", /[1-9]/, /\d/, /\d/, ")", " ", /\d/, /\d/, /\d/, "-", /\d/, /\d/, /\d/, /\d/]);
};

export const internationalPhoneFormat = (number, options) => {
  options = options || {};
  if (!number.startsWith("+")) {
    number = Config.DEFAULT_PHONE_COUNTRY_CODE + number;
  }
  if (!options.isRaw) {
    number = "+" + number.replace(/\D/g, "");
  }
  return number + (options.ext ? `,${options.ext}` : "");
};

export const formatPhone = (phone, options) => {
  options = options || {};
  var humanize = options.humanize === undefined ? true : options.humanize;
  var unmasked = conformToMask(phone, internationalPhoneMask(phone), {
    guide: !humanize
  });
  if (!humanize) {
    return unmasked.conformedValue;
  }
  var newPhone = unmasked.conformedValue;
  if (options.compact) {
    newPhone = newPhone.replace(/ \(|\) /g, "-");
  }
  if (newPhone.endsWith("-")) {
    newPhone = newPhone.slice(0, -1);
  }
  if (newPhone.startsWith(Config.DEFAULT_PHONE_COUNTRY_CODE)) {
    newPhone = newPhone.slice(Config.DEFAULT_PHONE_COUNTRY_CODE.length);
  }
  if (newPhone.startsWith("-")) {
    newPhone = newPhone.slice(1);
  }
  newPhone = newPhone.trim();
  if (options.ext) {
    newPhone = `${newPhone}x${options.ext}`;
  }
  return newPhone;
};

export const appendLinkToHeader = (url, rel='stylesheet') => {
  let link = document.createElement('link');
  link.rel = rel;
  link.href = url;
  document.head.appendChild(link)
};

export const appendStyleToHeader = (cssText) => {
  let style = document.createElement('style');
  style.innerText = cssText;
  document.head.appendChild(style)
};

export const appendScriptToHeader = (container, src, id, async=false, defer=false) => {
  if (container.getElementById(id)) {
    container.getElementById(id).remove();
  }
  var t = {};
  var js, fjs = container.getElementsByTagName('script')[0];
  js = container.createElement('script');
  js.id = id;
  js.src = src;
  if (async) {
    js.async = true;
  }
  if (defer) {
    js.defer = true;
  }
  fjs.parentNode.insertBefore(js, fjs);

  t._e = [];
  t.ready = function (f) {
    t._e.push(f);
  };

  return t;
};

export const emailIsValid = (email) => {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  return re.test(email);
};


export const convertModelToFormData = (model, form, namespace, filter) => {
  var formData = form || new FormData();
  var formKey;
  filter = filter === undefined ? k => k.startsWith("_") : filter;

  for (var propertyName in model) {
    if (
        !Object.prototype.hasOwnProperty.call(model, propertyName) ||
        model[propertyName] === undefined ||
        (filter && filter(propertyName))
    ) {
      continue;
    }
    if (namespace === undefined || (model instanceof FileList) || (model instanceof Array)) {
      formKey = namespace || propertyName
    } else {
      formKey = `${namespace}[${propertyName}]`;
    }
    if (model[propertyName] === null) {
      formData.append(formKey, "");
    } else if (model[propertyName] instanceof Date) {
      formData.append(formKey, model[propertyName].toISOString());
    } else if (model[propertyName] instanceof File) {
      formData.append(formKey, model[propertyName]);
    } else if (typeof model[propertyName] === "object") {
      convertModelToFormData(
          model[propertyName],
          formData,
          formKey,
          filter
      );
    } else {
      formData.append(formKey, model[propertyName].toString());
    }
  }
  return formData;
};
