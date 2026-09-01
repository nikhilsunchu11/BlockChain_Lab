import datetime
import hashlib
import json

from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        # Store all mined blocks and pending transactions
        self.chain = []
        self.transactions = []

        # Create the genesis block
        self.create_block(
            proof=1,
            previous_hash="0",
            transactions=[]
        )

    def create_block(self, proof, previous_hash, transactions):
        # Build a new block with the current timestamp and transaction list
        block = {
            "index" : len(self.chain) + 1,
            "timestamp" : str(datetime.datetime.now()),
            "transactions" : transactions,
            "proof" : proof,
            "previous_hash" : previous_hash
        }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        # Return the latest mined block
        return self.chain[-1]

    def hash(self, block):
        # Convert block data to a hash for integrity checking
        encoded_block = json.dumps(
            block,
            sort_keys=True
        ).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        # Find a number whose hash starts with 000 (mining challenge)
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(
                str(new_proof ** 2 - previous_proof ** 2).encode()
            ).hexdigest()

            if hash_operation[:3] == "000":
                return new_proof

            new_proof += 1

    def is_chain_valid(self, chain):
        # Verify all hashes and proof-of-work values in the chain
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]

            if block["previous_hash"] != self.hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            proof = block["proof"]

            hash_operation = hashlib.sha256(
                str(proof ** 2 - previous_proof ** 2).encode()
            ).hexdigest()

            if not hash_operation.startswith("000"):
                return False

            previous_block = block
            block_index += 1

        return True

    def create_transaction(self, sender, receiver, amount):
        # Store a new pending transaction before the next block is mined
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }

        self.transactions.append(transaction)

        return len(self.chain) + 1

    def mine_block(self):
        # Mine a new block only when at least one transaction is pending
        if not self.transactions:
            return None

        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]

        transactions = self.transactions
        self.transactions = []

        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)

        block = self.create_block(
            proof=proof,
            previous_hash=previous_hash,
            transactions=transactions
        )

        return block


app = Flask(__name__)

# Create a blockchain instance for the API server
blockchain = Blockchain()

@app.route("/get_chain", methods=["GET"])
def get_chain():
    # Return the complete blockchain and its current length
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    # Accept a JSON payload and queue a new transaction for mining
    data = request.get_json()

    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]

    block_index = blockchain.create_transaction(sender, receiver, amount)

    response = {
        "message": "Transaction added successfully",
        "block_index": block_index,
        "transaction": {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }
    }

    return jsonify(response), 201

@app.route("/mine_block", methods=["GET"])
def mine_block():
    # Mine the pending transactions into a new block
    block = blockchain.mine_block()

    if block is None:
        return jsonify({
            "message": "No transactions available. Block not mined."
        }), 400

    response = {
        "message": "Block mined successfully.",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }

    return jsonify(response), 200

@app.route("/is_valid", methods=["GET"])
def is_valid():
    # Check whether the blockchain has been tampered with
    valid = blockchain.is_chain_valid(blockchain.chain)

    if valid:
        response = {
            "message": "Blockchain is valid."
        }
    else:
        response = {
            "message": "Blockchain is not valid."
        }

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
