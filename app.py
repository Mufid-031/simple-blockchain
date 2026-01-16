import sys

from uuid import uuid4

from flask import Flask 
from flask.globals import request
from flask.json import jsonify

from blockchain import Blockchain


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

# Routes
@app.route('/blockchain', methods=['GET'])
def full_chain():
  response = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain)
  }
  
  return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine_block():
  blockchain.add_transaction(
    sender="0",
    receiver=node_identifier,
    amount=1
  )
  
  last_block_hash = blockchain.hash_block(blockchain.last_block)
  
  index = len(blockchain.chain)
  nonce = blockchain.proof_of_work(
    index=index,
    hash_of_previous_block=last_block_hash,
    transactions=blockchain.current_transactions
  )
  
  block = blockchain.append_block(
    hash_of_previous_block=last_block_hash,
    nonce=nonce
  )
  
  response = {
    'message': 'Block baru telah ditambahkan (mined)',
    'index': block['index'],
    'hash_of_previous_block': block['hash_of_previous_block'],
    'nonce': block['nonce'],
    'transactions': block['transactions'],
  }
  
  return jsonify(response), 200
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  values = request.get_json()
  
  required_fields = ['sender', 'receiver', 'amount']
  if not all(k in values for k in required_fields):
    return ('Missing fields', 400)
  
  index = blockchain.add_transaction(
    sender=values['sender'], 
    receiver=values['receiver'],
    amount=values['amount']
  )
  
  response = {
    'message': f'Transaksi akan ditambahkan ke block {index}'
  }
  
  return (jsonify(response), 201)

@app.route('/nodes/register', methods=['POST'])
def add_node():
  values = request.get_json()
  nodes = values.get('nodes')
  
  if nodes is None:
    return ("Error: No nodes", 400)
  
  for node in nodes:
    blockchain.add_node(node)
    
  response = {
    'message': 'Node baru telah ditambahkan',
    'nodes': list(blockchain.nodes)
  }
  
  return (jsonify(response), 201)
  
@app.route('/nodes/sync', methods=['GET'])
def sync_nodes():
  update = blockchain.update_blockchain()
  
  if update:
    response = {
      'message': 'Blockchain telah diperbarui',
      'chain': blockchain.chain
    }
  else:
    response = {
      'message': 'Blockchain sudah menggunakan chain terbaru',
      'chain': blockchain.chain
    }
    
  return jsonify(response), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(sys.argv[1]))