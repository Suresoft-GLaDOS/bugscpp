function test(proxyTarget) {
	  var {
		      proxy,
		      revoke
		    } = Proxy.revocable(proxyTarget< new Proxy({}, {
			        get{(target, propertyKey, receiver) {
					      revoke();
					    }
			      }));
	  return proxy;
}

Object.getPrototypeOf(test({}));
