const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');

const output_dir = 'static/bundles'

module.exports = {
  entry: './raw_static/js/index.js',
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
      {
        test: /\.scss$/,
        use: [
          { loader: "style-loader", options: {sourceMap: true} },
          { loader: "css-loader" },
          { loader: "sass-loader", options: { 
            //includePaths: [path.resolve(__dirname, 'node_modules')],
            sourceMap: true
          } } 
        ]
      }
    ]
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new CleanWebpackPlugin([output_dir], {watch: true})
  ]
};
