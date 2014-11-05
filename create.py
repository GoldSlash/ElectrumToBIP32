#!/usr/bin/env python

import random

# https://github.com/vbuterin/pybitcointools
from pybitcointools.deterministic import electrum_address, bip32_ckd, bip32_extract_key, pubkey_to_address
from pybitcointools.bci import history, unspent
from pybitcointools.transaction import mktx

ELECTRUM_GAP_LIMIT = 5
SATOSHI_PER_BITCOIN = 100000000
STANDARD_TX_FEE = 10000         # 0.0001 BTC
MIN_TX_VALUE = 10000            # 0.0001 BTC
MAX_TX_VALUE = 500000000        # 5 BTC
UNSIGNED_FILE = 'data/unsigned.dat'

print "ElectrumToBIP32 create.py (ONLINE)"

# Discover unspent outputs
discovered = []
electrum_mpk = raw_input('\nEnter MPK for Electrum wallet: ')
value_discovered = 0
for chain in (0, 1):
    gap = 0
    key_index = 0
    print "\nDiscovery for Electrum {0} chain:".format('receiving' if chain == 0 else 'change')
    while gap < ELECTRUM_GAP_LIMIT:
        address = electrum_address(electrum_mpk, key_index, chain)
        print "Checking %s for history..." % address,
        if history(address):
            gap = 0
            unspent_outputs = unspent(address)
            if unspent_outputs:
                value = sum([unspent_output['value'] for unspent_output in unspent_outputs])
                value_btc = float(value) / SATOSHI_PER_BITCOIN
                print "{0} BTC found".format(value_btc)
                d = {"chain": chain, "key_index": key_index, "address": address,
                     "unspent_outputs": unspent_outputs, "value": value}
                discovered.append(d)
                value_discovered += value
            else:
                print "all spent"
        else:
            print "no history"
            gap += 1
        key_index += 1
value_discovered_btc = float(value_discovered) / SATOSHI_PER_BITCOIN
print "Discovered {0} BTC in {1} addresses.\n".format(value_discovered_btc, len(discovered))

# Discover unused destination addresses
destinations = []
bip32_mpk = raw_input('Enter MPK for BIP32 wallet: ')
print "\nDiscovery for BIP32 chain:"
key_index = 0
destinations_needed = len(discovered) * 2
while len(destinations) < destinations_needed:
    extended_public_key = bip32_ckd(bip32_mpk, key_index)
    public_key = bip32_extract_key(extended_public_key)
    address = pubkey_to_address(public_key)
    print "Checking %s for history..." % address,
    if not history(address):
        print "no history"
        destinations.append(address)
    else:
        print "history found"
    key_index += 1
print "Discovered {0} unused addresses.\n".format(len(destinations))

# Create unsigned transactions
transactions = []
raw_input('Press any key to create unsigned transactions.')
for d in discovered:
    tx_destination_1 = destinations.pop(0)
    tx_destination_2 = destinations.pop(0)

    # Calculate transaction output values
    min_value = MIN_TX_VALUE
    max_value = min(MAX_TX_VALUE, d['value'] - STANDARD_TX_FEE)
    tx_value_1 = random.randint(min_value, max_value)
    tx_value_2 = d['value'] - (tx_value_1 + STANDARD_TX_FEE)

    tx_inputs = d['unspent_outputs']
    tx_outputs = [tx_destination_1 + ':' + str(tx_value_1), tx_destination_2 + ':' + str(tx_value_2)]
    raw_transaction = mktx(tx_inputs, tx_outputs)
    transactions.append((d['chain'], d['key_index'], raw_transaction))

# Write unsigned transactions and chain/indexes to disk
with open(UNSIGNED_FILE, 'w') as f:
    for chain, key_index, raw_transaction in transactions:
        f.write(str(chain)+':'+str(key_index)+':'+raw_transaction+'\n')

print('\nWrote {0} unsigned transactions to file: {1}'.format(len(transactions), UNSIGNED_FILE))