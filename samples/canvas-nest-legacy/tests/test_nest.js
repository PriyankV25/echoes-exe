const assert = require('assert');
const CanvasNest = require('../src/canvas-nest');

describe('CanvasNest', () => {
    it('initializes properly', () => {
        const nest = new CanvasNest(null);
        assert.ok(nest);
    });
});
