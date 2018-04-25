This is the Readme for the Merkato Exchange Bot

The Exchange bot is designed for arbitrage and market making within the cryptocurrency ecosystem, and is under development.

Working specification

Create Exchange objects that can interact with their respective exchanges.

Create Merkato objects, which take Exchange objects as parameters, and each represent a running strategy. 

Strategies need to hold mutexes so that they don't interfere with each other.
