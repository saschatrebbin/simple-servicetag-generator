'use strict';

// Execute the actual shared script, with just the browser APIs it needs.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const partial = fs.readFileSync(
    path.join(__dirname, '../app/templates/partials/clipboard.tpl'), 'utf8'
);
const match = partial.match(/^\s*<script>\s*([\s\S]*?)\s*<\/script>\s*$/);
assert.ok(match, 'the shared partial must contain one static script');

function environment() {
    const values = {
        'id-0': '  first & <id>  ',
        'id-1': ' second  id ',
        'long-0': '  long & <one>  ',
        'short-0': ' short 1 ',
        'long-1': ' long  two ',
        'short-1': '  short2  '
    };
    const elements = Object.fromEntries(Object.entries(values).map(([id, text]) => [
        id, { textContent: text, innerText: 'incorrect collapsed value', style: {} }
    ]));
    const writes = [];
    const timers = [];
    const context = {
        document: {
            getElementById(id) {
                assert.ok(elements[id], `unknown element ${id}`);
                return elements[id];
            },
            querySelectorAll(selector) {
                if (selector === '.id-value') return [elements['id-0'], elements['id-1']];
                if (selector === '.identifier-list li') return [{}, {}];
                throw new Error(`unexpected selector ${selector}`);
            }
        },
        navigator: { clipboard: { writeText(text) { writes.push(text); return Promise.resolve(); } } },
        setTimeout(callback) { timers.push(callback); }
    };
    vm.runInNewContext(match[1], context, { filename: 'clipboard.tpl' });
    return { context, elements, timers, values, writes };
}

test('copy one Nano ID preserves all spaces and shows feedback', async () => {
    const { context, elements, timers, values, writes } = environment();
    context.copyOne(1);
    await Promise.resolve();
    assert.deepEqual(writes, [values['id-1']]);
    assert.equal(elements['id-1'].style.background, '#d4edda');
    timers[0]();
    assert.equal(elements['id-1'].style.background, '');
});

test('copy all Nano IDs preserves their contents and line separation', () => {
    const { context, values, writes } = environment();
    context.copyAllNano();
    assert.deepEqual(writes, [values['id-0'] + '\n' + values['id-1']]);
});

test('copy identifier long, short, and both preserves their contents', () => {
    const { context, values, writes } = environment();
    context.copyValue(0, 'long');
    context.copyValue(0, 'short');
    context.copyValue(0, 'both');
    assert.deepEqual(writes, [
        values['long-0'],
        values['short-0'],
        values['long-0'] + ' (' + values['short-0'] + ')'
    ]);
});

test('copy all identifiers preserves their contents and line separation', () => {
    const { context, values, writes } = environment();
    context.copyAllIdentifiers();
    assert.deepEqual(writes, [
        values['long-0'] + ' (' + values['short-0'] + ')\n' +
        values['long-1'] + ' (' + values['short-1'] + ')'
    ]);
});
