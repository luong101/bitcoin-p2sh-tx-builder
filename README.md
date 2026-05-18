# Bitcoin P2SH Multisig Transaction Engine

AA small Python utility that demonstrates creating, funding, and spending from a 2-of-2 P2SH (multisignature) Bitcoin wallet on Testnet. The code in this repository builds raw transactions, estimates fees using a dummy transaction to compute virtual bytes, signs inputs with two private keys to satisfy OP_CHECKMULTISIG, and broadcasts serialized transactions via the Mempool.space Testnet4 API.

## Features
- P2SH Address Generation: create a 2-of-2 redeem script and P2SH address.
- Direct UTXO Management: query UTXOs from Mempool.space Testnet4.
- Dynamic Fee Estimation: create a dummy transaction with placeholder signatures to measure virtual size (vbytes), then apply a live fee rate.
- Raw Transaction Construction & Broadcast: construct, sign with two private keys, serialize and broadcast raw hex transactions.

## Tech Stack
* **Language:** Python
* **Libraries:** `bitcoinutils`, `requests`
* **APIs:** Mempool.space (Testnet4)

## Project Structure
- Source/setup_multisig.py — generates two private keys, their public keys, the 2-of-2 redeem script and the corresponding P2SH address, and writes these items to `list.txt`.
- Source/setup_recipient.py — generates a recipient P2PKH key/address and appends it to `list.txt`.
- Source/spend_multisig.py — reads `list.txt`, fetches UTXOs for the P2SH address, builds a dummy transaction to estimate the serialized vbytes, calculates the fee using mempool.space recommended rates, signs the transaction with both private keys, serializes, and broadcasts it to mempool.space/testnet4.
- Source/list.txt — local file used to share generated keys/addresses between scripts. This file is present in the repository for demo purposes; do not commit real keys.

## Technical Insights & Trade-offs
Working with raw Bitcoin Script and P2SH architectures presented several interesting technical trade-offs:

### Advantages of P2SH Multisig
* **Enhanced Security:** Compromise of a single key does not lead to loss of funds, making it ideal for organizational custody.
* **Reduced UTXO Size:** By embedding the complex redeem script in the transaction input (ScriptSig) at the time of spending, rather than the output (ScriptPubKey), the UTXO set is kept small.

### Limitations & Challenges
* **Higher Transaction Fees:** Because the `scriptSig` in multisig transactions requires multiple signatures and the full redeem script, the overall transaction size in virtual bytes (vB) is larger than standard P2PKH, resulting in higher miner fees.
* **Dynamic Fee Volatility:** Network fees fluctuate rapidly. To solve this, I engineered a solution that builds a "fake" transaction with dummy signatures to calculate the exact serialized byte size, which is then multiplied by the live API fee rate before constructing the *actual* transaction.
* **Testnet Anomalies:** Initially faced issues with abnormally high fees on Testnet3, requiring a migration to Testnet4 for reliable transaction broadcasting.
