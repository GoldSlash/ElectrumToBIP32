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

# Discover unspent outputs
discovered = []
electrum_mpk = raw_input('\nEnter MPK for Electrum wallet: ')
value_discovered = 0
for chain in range(2):
    gap = 0
    key_index = 0
    print "\nDiscovery for Electrum {0} chain:".format('receiving' if chain == 0 else 'change')
    while gap < ELECTRUM_GAP_LIMIT:
        address = electrum_address(electrum_mpk, key_index, chain)
        print "Checking %s for history..." % address,
        if len(history(address)) > 0:
            gap = 0
            unspent_outputs = unspent(address)
            if len(unspent_outputs) > 0:
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
while len(destinations) < len(discovered) * 2:
    extended_public_key = bip32_ckd(bip32_mpk, key_index)
    public_key = bip32_extract_key(extended_public_key)
    address = pubkey_to_address(public_key)
    print "Checking %s for history..." % address,
    if len(history(address)) == 0:
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
    transaction = mktx(tx_inputs, tx_outputs)
    transactions.append((d['chain'], d['key_index'], transaction))

    print "\nTransaction for {0} (chain: {1}  index: {2})".format(d['address'], d['chain'], d['key_index'])
    print "Inputs:"
    print "\t{0}".format(d['unspent_outputs'])
    print "Outputs:"
    print "\t{0} : {1}".format(tx_destination_1, tx_value_1)
    print "\t{0} : {1}".format(tx_destination_2, tx_value_2)

# Write unsigned transactions and key indexes to disk
with open('data/unsigned.dat', 'w') as f:
    for chain, key_index, transaction in transactions:
        f.write(str(chain)+':'+str(key_index)+':'+transaction+'\n')

print('\nWrote {0} unsigned transactions and key indexes to file: unsigned.dat'.format(len(transactions)))