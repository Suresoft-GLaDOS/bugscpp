Defects4cpp User Guide
======================

.. include:: ../../README.rst
   :start-after: .. begin example
   :end-before: .. end example

.. autoprogram:: bugscpp.processor.checkout:CheckoutCommand().parser
   :prog: bugscpp checkout

.. autoprogram:: bugscpp.processor.build:BuildCommand().parser
   :prog: bugscpp build

.. autoprogram:: bugscpp.processor.test:TestCommand().parser
   :prog: bugscpp test

.. _case-example:

Case Expression:

``,``
    | select distinctive cases
    | --case=1,2,3 will run 1, 2 and 3.

``-``
    | select a range of cases
    | --case=1-3 will run from 1 to 3.

``:``
    | expression after colon will be used to exclude cases
    | --case=1-5:1 will run from 1 to 5 except 1.
    | --case=1-5:1,2 will run from 1 to 5 except 1 and 2.
    | --case=1-5:3-5 will run from 1 to 5 except from 3 to 5.
