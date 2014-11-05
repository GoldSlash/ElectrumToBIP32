#!/usr/bin/env python

# https://github.com/spesmilo/electrum/blob/1.9.8/lib/mnemonic.py
from mnemonic import mn_decode as mnemonic_to_root_key

# https://github.com/vbuterin/pybitcointools
from pybitcointools.deterministic import electrum_privkey
from pybitcointools.transaction import sign, deserialize, script_to_address

SATOSHI_PER_BITCOIN = 100000000
UNSIGNED_FILE = 'data/unsigned.dat'
SIGNED_FILE = 'data/signed.dat'

print "ElectrumToBIP32 sign.py (OFFLINE)"

# Read transaction data from disk
transactions = []
with open(UNSIGNED_FILE, 'r') as f:
    unsigned_transactions = f.readlines()
    print "\nRead {0} unsigned transactions from file: {1}".format(len(unsigned_transactions), UNSIGNED_FILE)
    for ut in unsigned_transactions:
        chain, key_index, raw_transaction = ut.rstrip().split(':')
        transactions.append({'chain': chain, 'key_index': key_index, 'raw_transaction': raw_transaction})

# Review transactions before signing
value_total = 0
for tx in transactions:
    print "\nfrom chain {0}, index {1}".format(tx['chain'], tx['key_index'])
    outputs = deserialize(tx['raw_transaction'])['outs']
    for output in outputs:
        destination = script_to_address(output['script'])
        value = output['value']
        value_total += value
        value_btc = float(value)/SATOSHI_PER_BITCOIN
        print "\tto {0}:  {1:,f} BTC".format(destination, value_btc)
value_total_btc = float(value_total) / SATOSHI_PER_BITCOIN
print "Total Value:  {0:,f} BTC (excluding network fees)".format(value_total_btc)
print "\nReview transactions before continuing."

# Convert Electrum wallet seed into root key
print "\nWarning: Do not continue unless you are offline."
electrum_seed = raw_input('Enter Electrum wallet seed: ')
word_list = str.split(electrum_seed)
root_key = mnemonic_to_root_key(word_list)

# Sign transactions
signed_transactions = []
for tx in transactions:
    private_key = electrum_privkey(root_key, tx['key_index'], tx['chain'])
    signed_transaction = sign(tx['raw_transaction'], tx['chain'], private_key)
    signed_transactions.append(signed_transaction)

# Write signed transactions to disk
with open(SIGNED_FILE, 'w') as f:
    for tx in signed_transactions:
        f.write(tx+'\n')

print "Wrote {0} signed transactions to file: {1}".format(len(signed_transactions), SIGNED_FILE)