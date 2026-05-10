This is a parser for CSV transaction history exported from Wise.

Download the CSV statement in Account // Statements and reports // Statements // Create a statement:

- Single currency
- CSV
- Off: Display transactions with fees shown

It is a plugin for `ofxstatement`_, based on `ofxstatement-transferwise`_

.. _ofxstatement: https://github.com/kedder/ofxstatement
.. _ofxstatement-transferwise: https://github.com/kedder/ofxstatement-transferwise

Usage
=====
::

  $ ofxstatement convert -t wise:USD statement_123456789_USD_2025-10-14_2026-05-10 statement_136821354_USD_2025-10-14_2026-05-10.ofx

Configuration
=============
::

  $ ofxstatement edit-config

and set e.g. the following:
::

  [wise:USD]
  plugin = wise
  currency = USD
  account = Wise USD
  
  [wise:EUR]
  plugin = wise
  currency = EUR
  account = Wise EUR
