from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Product')  # Asegúrate de que la tabla existe

# Create (POST /product)
@app.route('/product', methods=['POST'])
def create_product():
    data = request.json
    if 'product' not in data:
        return jsonify({'error': 'Missing product key'}), 400
    try:
        table.put_item(Item=data)
        return jsonify({'message': 'Product created'}), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

# Read (GET /product/<id>)
@app.route('/product/<string:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        response = table.get_item(Key={'product': product_id})
        if 'Item' not in response:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(response['Item']), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

# Update (PUT /product/<id>)
@app.route('/product/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    try:
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in data])
        expr_names = {f"#{k}": k for k in data}
        expr_values = {f":{k}": v for k, v in data.items()}

        result = table.update_item(
            Key={'product': product_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW"
        )
        return jsonify(result.get('Attributes', {})), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

# Delete (DELETE /product/<id>)
@app.route('/product/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        table.delete_item(Key={'product': product_id})
        return jsonify({'message': 'Product deleted'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

# List (GET /products)
@app.route('/products', methods=['GET'])
def list_products():
    try:
        response = table.scan()
        return jsonify(response.get('Items', [])), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
