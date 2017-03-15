// detecgt the compilation settings
const PROD = process.env.NODE_ENV == 'production';

// load the webpack engine
const webpack = require('webpack');

// load webpack plugins
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const AssetsPlugin = require('assets-webpack-plugin');
const path = require('path');
const dist_dir = PROD ? 'prod' : 'dev';
const optimizers = PROD ? [
      new webpack.optimize.UglifyJsPlugin({
        compress: { warnings: false },
        minimize: true
      }),
      new OptimizeCssAssetsPlugin({
        assetNameRegExp: /\.css$/g,
        cssProcessor: require('cssnano'),
        cssProcessorOptions: { discardComments: {removeAll: true } },
        canPrint: true
      })
    ] : [
    ];
const plugins = [
      new webpack.ProvidePlugin({
        $: "jquery",
        jQuery: "jquery"
      }),
      new ExtractTextPlugin({ filename: PROD ? '[name].css' : '[name].[contenthash].css', allChunks: true })
    ].concat(optimizers).concat([
      new AssetsPlugin({
        path: path.join(__dirname, '../static/' + dist_dir),
        filename: 'assets.json'
      })
    ]);

// config the webpack
module.exports = {
  entry: {
    main: [
      './sass/main.scss',
      './src/main.js'
    ]
  },
  output: {
    path: path.join(__dirname, "../static/" + dist_dir),
    publicPath: '',
    filename: PROD ? '[name].js' : '[name].[chunkhash].js'
  },
  resolve: {
    extensions: ['*', '.js', '.vue'],
    modules: ['node_modules', 'src', 'themes']
  },
  plugins: plugins,
  module: {
    loaders: [
      // Vue and JavaScript Loader
      {
        test: /\.vue$/,
        loader: 'babel-loader!vue-loader',
        include: [path.resolve(__dirname, './src')]
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: [path.resolve(__dirname, './src')]
      },
      // CSS, SASS, Fonts and Resources Loader
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract({
          fallbackLoader: 'style-loader',
          loader: 'css-loader!postcss-loader',
        })
      },
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract({
          fallbackLoader: 'style-loader',
          loader: 'css-loader!postcss-loader!resolve-url-loader!sass-loader?sourceMap',
        })
      },
      {
        test: /\.less$/,
        loader: ExtractTextPlugin.extract({
          fallbackLoader: 'style-loader',
          loader: 'css-loader!postcss-loader!resolve-url-loader!less-loader?sourceMap',
        })
      },
      { test: /\.(woff2?|svg|ttf|eot)$/, loader: 'url-loader?limit=10000' },
      { test: /\.(png|jpg|gif)$/, loader: 'file-loader'},
    ]
  }
};