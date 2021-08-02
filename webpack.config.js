const path = require('path');

module.exports = {
  entry: './website/static/base.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'website/static')
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['*', '.js', '.jsx'],
  },
};
