import defects4cpp.processor


def test_checkout_fixed(tmp_path, gitenv):
    checkout = defects4cpp.processor.CheckoutCommand()
    project = "yara"
    number = "1"
    # Run twice
    checkout(f"{project} {number} --target {str(tmp_path)}".split())
    checkout(f"{project} {number} --target {str(tmp_path)}".split())


def test_checkout_buggy(tmp_path, gitenv):
    checkout = defects4cpp.processor.CheckoutCommand()
    project = "yara"
    number = "1"
    # Run twice
    checkout(f"{project} {number} --buggy --target {str(tmp_path)}".split())
    checkout(f"{project} {number} --buggy --target {str(tmp_path)}".split())
