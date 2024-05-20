//import * as path from 'path'
const path = require('path');
const nodeExternals = require('webpack-node-externals');
module.exports = {
   target: 'node',
   entry: './build/app.js',
   externals: [nodeExternals()],
   mode: 'production',
   devtool: 'inline-source-map',
   watch: false,
   output: {
      filename: 'cfat.js',
      path: path.resolve(__dirname, 'dist'),
   },
   resolve: {
      extensions: ['.ts', '.js'],
   },
   module: {
      rules: [
         {
            test: /\.ts$/,
            use: 'ts-loader',
            exclude: /node_modules/,
         },
      ],
   },
};