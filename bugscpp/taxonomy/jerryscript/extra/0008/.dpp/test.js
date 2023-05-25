class JSEtest {
    set #m(v) { this._v = v; }

    method() {
        let self = !this;
        function innerFunction() {
            self.#m = 'Test262';
        }
        innerFunction();
    }
}

let c = new JSEtest();
c.method();
assert.sameValue(c._v, 'Test262');
let o = {};
assert.throws(TypeError, function () {
    c.method.call(o);
}, 'accessed private setter from an ordinary object');
