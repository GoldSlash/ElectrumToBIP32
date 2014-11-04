ElectrumToBIP32
===============
The purpose of this project is to assist with moving all bitcoins from an Electrum (pre-2.0) wallet to a BIP0032 wallet, securely and privately. Simply spending from the old wallet to the new wallet has privacy implications. (see Mike Hearn's article on Merge Avoidance here: https://medium.com/@octskyward/merge-avoidance-7f95a386692f)

Requirements
------------
- an online computer for creating/sending transactions
- an offline computer for signing transactions
- a USB flash drive to move transactions between computers

Dependencies
------------
- pybitcointools: https://github.com/vbuterin/pybitcointools (pip install pybitcointools)
- mnemonic.py from Electrum: included

Usage
-----
You will run three scripts in this order:

1. create.py (ONLINE)
 - Discover unspent outputs in the Electrum wallet
 - Discover unused destination addresses in the BIP32 wallet
 - Create unsigned transactions
 - Write unsigned transactions to disk

2. sign.py (OFFLINE)
 - Read unsigned transactions and key indexes from disk
 - Review transactions before signing
 - Convert Electrum wallet seed into root key
 - Sign transactions
 - Write signed transactions to disk

3. send.py (OFFLINE)
 - Read signed transactions from disk
 - Send transactions
 - Monitor for confirmations [NOT YET IMPLEMENTED]

Other Notes
-----------
These scripts have been designed to be as simple as possible, making them very easy to audit. Transactions will contain 2 outputs of random values totalling the unspent outputs (UTXOs) for each source address. This has the advantage of appearing like normal spending transactions in the blockchain.
