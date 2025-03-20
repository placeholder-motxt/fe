// Use CommonJS require syntax for polyfill
const { TextEncoder, TextDecoder } = require('@sinonjs/text-encoding');
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

// Now import other dependencies
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

// Load HTML template
const html = fs.readFileSync(
  path.resolve(__dirname, '../templates/convert_page.html'),
  'utf8'
);
const dom = new JSDOM(html, { runScripts: 'dangerously' });

// Setup global objects
global.window = dom.window;
global.document = dom.window.document;
global.fetch = require('jest-fetch-mock');
global.navigator = dom.window.navigator;
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};

// Load the actual JS file
require('../static/js/convert_page.js');