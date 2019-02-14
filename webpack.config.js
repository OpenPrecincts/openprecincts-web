const path = require('path');
var BundleTracker = require('webpack-bundle-tracker');

const output_dir = 'static/bundles'

module.exports = {
  entry: './js/index.js',
  output: {
    path: path.resolve(output_dir),
    filename: "[name]-[hash].js",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        // query: { plugins: ['transform-runtime'] } 
      },
    ]
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ]
};
