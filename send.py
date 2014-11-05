#!/usr/bin/env python

# https://github.com/vbuterin/pybitcointools
from pybitcointools.bci import pushtx

SIGNED_FILE = 'data/signed.dat'

print "ElectrumToBIP32 send.py (ONLINE)"

# Read signed transactions from disk
with open('data/signed.dat', 'r') as f:
    signed_transactions = f.readlines()
print "\nRead {0} signed transactions from file: {1}\n".format(len(signed_transactions), SIGNED_FILE)

# Send transactions
confirmation = raw_input('Send transaction(s)? [y/N] ')

if confirmation.lower() in ['y', 'yes']:
    for transaction in signed_transactions:
        print('DEBUG: {0}'.format(transaction))
        transaction = transaction.rstrip()
        # pushtx(transaction)
    print('Sent transactions.')

# Monitor for confirmations
