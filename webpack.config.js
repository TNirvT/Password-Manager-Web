const path = require('path');

module.exports = {
  entry: './website/static/base.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'website/static')
  }
};
