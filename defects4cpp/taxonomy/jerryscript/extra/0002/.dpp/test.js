var a = new Int32Array(256);
try {
a.sort(function() {
    var o = new Proxy(this, {
        has: print,
        get: function() {
            a = true;
            return 30;
        }
    });
    var result = "";
    for (var p in o)
        result += o[p];
});
  assert(false);
} catch (e) {
  assert(e instanceof TypeError);
}
