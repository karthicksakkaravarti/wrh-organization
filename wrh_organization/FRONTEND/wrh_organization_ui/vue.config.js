const path = require('path')
const { mergeSassVariables } = require('@vuetify/cli-plugin-utils')
const PUBLIC_PATH = "/static/vue/";
const BACKEND_URL = process.env.VUE_APP_SERVER_BASE_URL || "http://localhost:8000";


module.exports = {
  publicPath: PUBLIC_PATH,
  productionSourceMap: true,
  lintOnSave: false,
  transpileDependencies: ['vuetify'],
  configureWebpack: {
    resolve: {
      alias: {
        '@themeConfig': path.resolve(__dirname, 'themeConfig.js'),
        '@core': path.resolve(__dirname, 'src/@core'),
        '@axios': path.resolve(__dirname, 'src/plugins/axios.js'),
        '@user-variables': path.resolve(__dirname, 'src/styles/variables.scss'),
        apexcharts: path.resolve(__dirname, 'node_modules/apexcharts-clevision'),
      },
    },
  },
  chainWebpack: config => {
    const modules = ['vue-modules', 'vue', 'normal-modules', 'normal']
    modules.forEach(match => {
      config.module
        .rule('sass')
        .oneOf(match)
        .use('sass-loader')
        .tap(opt => mergeSassVariables(opt, "'@/styles/variables.scss'"))
      config.module
        .rule('scss')
        .oneOf(match)
        .use('sass-loader')
        .tap(opt => mergeSassVariables(opt, "'@/styles/variables.scss';"))
    })
  },
  devServer: {
    setup: function(app) {
      app.get("/", function(req, res) {
        res.redirect(PUBLIC_PATH);
      });
    },
    disableHostCheck: true,
    watchOptions: {
      poll: true
    },
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true
      },
      "/user/login": {
        target: BACKEND_URL,
        changeOrigin: true
      },
      "/user/change_password/": {
        target: BACKEND_URL,
        changeOrigin: true
      },
      "/static/dj": {
        target: BACKEND_URL,
        changeOrigin: true
      },
      "/media/": {
        target: BACKEND_URL,
        changeOrigin: true
      },
      "/ws": {
        target: BACKEND_URL,
        changeOrigin: true,
        ws: true
      }
    }
  }
};
