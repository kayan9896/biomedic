module.exports = {
  presets: [
    '@babel/preset-env',
    ['@babel/preset-react', {
      runtime: 'automatic' // This is recommended for React 17+
    }]
  ]
};