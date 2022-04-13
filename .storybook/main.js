const webpackConfig = require("../webpack.config");

module.exports = {
  stories: ['../assets/js/**/*.stories.jsx'],
  addons: ['@storybook/addon-essentials'],
  webpackFinal: async config => {
    // do mutation to the config
    // config.resolve = webpackConfig.resolve;
    config.resolve = Object.assign(config.resolve, webpackConfig.resolve);
    return config;
  },
};
