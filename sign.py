#!/usr/bin/env python

# https://github.com/spesmilo/electrum/blob/1.9.8/lib/mnemonic.py
from mnemonic import mn_decode as mnemonic_to_root_key

# https://github.com/vbuterin/pybitcointools
from pybitcointools.deterministic import electrum_privkey as electrum_private_key
from pybitcointools.transaction import sign

# Read unsigned transactions and chain/indexes from disk
with open('data/unsigned.dat', 'r') as f:
    unsigned_transactions = f.readlines()

# Review transactions before signing
print "\nReview transactions before continuing.\n"
for tx_data in unsigned_transactions:
    print "info about transaction here"
    print tx_data

# Convert Electrum wallet seed into root key
print "Warning: Do not continue unless you are offline."
electrum_seed = raw_input('Enter Electrum wallet seed: ')
word_list = str.split(electrum_seed)
root_key = mnemonic_to_root_key(word_list)

# Sign transactions
signed_transactions = []
for tx_data in unsigned_transactions:
    chain, key_index, transaction = tx_data.split(':')
    transaction = transaction.rstrip()
    private_key = electrum_private_key(root_key, key_index, chain)
    signed_transaction = sign(transaction, chain, private_key)
    signed_transactions.append(signed_transaction)

# Write signed transactions to disk
with open('data/signed.dat', 'w') as f:
    for transaction in signed_transactions:
        f.write(transaction+'\n')

print "Signing is complete."