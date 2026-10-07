const path = require('path');
const root = path.resolve(__dirname, '..');
global.window = {};
require(path.join(root, 'www/js/brain_biz.js'));
require(path.join(root, 'www/js/brain_wisdom.js'));
require(path.join(root, 'www/js/expertBrain.js'));

console.log('Businesses loaded: ' + (window.BIZ_BATCH || []).length);
console.log('Wisdom loaded: ' + (window.WISDOM_BATCH || []).length);
console.log('');

function t(q) {
  console.log('=== QUERY: ' + q + ' ===');
  var r = window.buildExpertReply(q);
  if (!r) {
    console.log('(NO BRAIN MATCH - falls back to old logic)');
  } else {
    var text = r[0] || '';
    console.log(text.substring(0, 260));
  }
  console.log('');
}

t('how do I make charcoal soap?');
t('how do I make neem soap?');
t('how do I make solar cooker?');
t('how do I make liquid soap?');
t('how do I make honey?');
t('how do I start stingless bee farming?');
t('how do I make interlocking bricks?');
t('what is cash flow?');
