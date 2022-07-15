function testAdvanceStringIndex(lastIndex) {
  let exec_count = 0;
  let last_last_index = -1;
  let fake_re = {
    exec: () => {
      return exec_count++ == 0 ? [""] : null;
    },

    get lastIndex() {
      return lastIndex;
    },

    set lastIndex(value) {
    },

    get global() {
      return true;
    }
  };

  RegExp.prototype[Symbol.match].call(fake_re, "abc");
}

testAdvanceStringIndex(0x7ffffff);
