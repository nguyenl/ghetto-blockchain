# ghetto-blockchain
A toy blockchain database written in Python.

I wanted to learn about creating my own block chain network, so I
built this.  This is obviously not production ready, but has a few
features.

The ledger itself can be used as a python library module, or it can be
run as a process that can be interfaced via REST.

Be warned, I wanted to create this in a single work day, so it's not the prettiest code.

# Features

* Save arbitrary data to the database (the ledger).
* Stores transaction history as a block chain.
* Block chain ledger can be verified by the block chain.
* Persisting the ledger:
 * In standalone mode, the blockchain can be persisted to disk as a json file.
 * As a peer, the blockchain is persisted and read from a redis store.
* RESTful API for viewing and updating the block chain.
* Can syncrhonize between two separate block chain instances to act as a network.

# Missing Features

* Not production ready. No cryptographically strong gaurantees, since this is a skunk works project.
* No consensus algorithm. Is susceptible to Byzantine Generals Problem.
* No security implmenetations
 * Traffic not encrypted
 * Identify of peers not secure
* Peers cannot resolve a conflict automatically once a conflict occurs.
* One peer cannot seed another peer that has just joined.
