const path = require('path');

module.exports = {
  entry: {
    base: './website/static/base.js',
    content: './website/static/content.js',
  },
  output: {
    filename: '[name].bundle.js',
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
