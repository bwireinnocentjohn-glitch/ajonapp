const path = require('path');
const root = path.resolve(__dirname, '..');
global.window = {};
require(path.join(root, 'www/js/brain_biz.js'));
require(path.join(root, 'www/js/brain_wisdom.js'));
require(path.join(root, 'www/js/expertBrain.js'));

function t(q) {
  var r = window.buildExpertReply(q);
  var head = (r && r[0]) ? r[0].split('\n')[0].substring(0, 80) : '(no match)';
  console.log(q + '  →  ' + head);
}

t('how do I make groundnut oil?');
t('how do I make black soap?');
t('how do I make plastic pavers?');
t('how do I make beeswax wraps?');
t('how do I start cricket farming?');
t('how do I make compost?');
t('how do I make yoghurt?');
t('how do I make shea butter?');
t('how do I make mandazi?');
t('how do I make biogas?');
t('what is a KPI?');
t('what is CAC?');
t('what is shea butter?');
