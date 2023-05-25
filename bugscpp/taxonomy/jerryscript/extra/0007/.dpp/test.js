function JSEtest(f, iters = 1000) {
  for (let i = 0; i < iters; i++) {
    f();
  }
}

function throwTDZ(f) {
  let threw = false;
  try {
    f();
  } catch (e) {
    ;
  }
}

JSEtest(function () {
  class M {
    get foo() {
      return this._x;
    }
    set foo(x) {
      this._x = x;
    }
  }

  function fooProp() {
    return 'foo';
  }

  class T1 extends M {
    constructor() {
      super.foo = 20;
    }
  }

  class T2 extends M {
    constructor() {
      super[fooProp()] = 20;
    }
  }

  class T3 extends M {
    constructor() {
      super[fooProp()];
    }
  }

  class T4 extends M {
    constructor() {
      super.foo;
    }
  }

  class T5 extends M {
    constructor() {
      (() => super.foo = 20)();
    }
  }

  class T6 extends M {
    constructor() {
      (() => super[fooProp()] = 20)();
    }
  }

  class T7 extends M {
    constructor() {
      (() => super[fooProp()])();
    }
  }

  class T8 extends M {
    constructor() {
      (() => super.foo)();
    }
  }

  throwTDZ(function () {
    new T1();
  });
  throwTDZ(function () {
    new T2();
  });
  throwTDZ(function () {
    new T3();
  });
  throwTDZ(function () {
    new T4();
  });
  throwTDZ(function () {
    new T5();
  });
  throwTDZ(function () {
    new T6();
  });
  throwTDZ(function () {
    new T7();
  });
  throwTDZ(function () {
    new T8();
  });
});
