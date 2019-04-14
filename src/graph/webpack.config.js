// webpack.config.js

// require
const webpack = require("webpack");
var path = require("path");

// ユーザ定義変数
const jsdir = path.join('src','js');
const outputdir = 'dist';
const targetjs = ['graph']//['index','tasks'];

//
let entryjs = {};
targetjs.forEach( function(name) {
    entryjs[name] = path.join(__dirname, jsdir, name, name + '.js');
});

const config = {
  mode: 'development',
  entry: entryjs,
  output: {
    path: path.resolve(__dirname, outputdir),
    filename: '[name].js'
  },
  target:'electron-renderer',  // 追加 renderer用
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: path.resolve(__dirname, 'node_modules'),
        loader: 'babel-loader',
        options: {
            presets: [
                'env',
                'react',
            ]
        }
      },
      {
          test: /\.css$/,
          exclude: path.resolve(__dirname, 'node_modules'),
          use: {
              loader: 'css-loader',
          },
      },
    ]
  },
  plugins: [
  ],
};


module.exports = config;

