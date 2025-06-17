# Ethereum Transaction Tracker - System Architecture

## Table of Contents
1. [Database Design](#database-design)
2. [System Architecture](#system-architecture)
3. [Complex Transaction Handling](#complex-transaction-handling)
4. [Trade-offs and Considerations](#trade-offs-and-considerations)
5. [Scalability Considerations](#scalability-considerations)

## Database Design

### Schema Design

```sql
-- Core Transactions Table
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    hash TEXT NOT NULL,
    block_number BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    value NUMERIC NOT NULL,
    gas_price NUMERIC NOT NULL,
    gas_used NUMERIC NOT NULL,
    status TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_hash (hash),
    INDEX idx_block_number (block_number),
    INDEX idx_from_address (from_address),
    INDEX idx_to_address (to_address)
);

-- Token Transfers Table
CREATE TABLE token_transfers (
    id UUID PRIMARY KEY,
    transaction_id UUID NOT NULL,
    token_address TEXT NOT NULL,
    token_type TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    token_id TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    INDEX idx_token_address (token_address),
    INDEX idx_from_address (from_address),
    INDEX idx_to_address (to_address)
);

-- Contract Interactions Table
CREATE TABLE contract_interactions (
    id UUID PRIMARY KEY,
    transaction_id UUID NOT NULL,
    contract_address TEXT NOT NULL,
    method_signature TEXT NOT NULL,
    input_data JSONB NOT NULL,
    decoded_data JSONB,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    INDEX idx_contract_address (contract_address)
);

-- Addresses Table
CREATE TABLE addresses (
    address TEXT PRIMARY KEY,
    first_seen_at TIMESTAMP NOT NULL,
    last_seen_at TIMESTAMP NOT NULL,
    transaction_count BIGINT NOT NULL,
    is_contract BOOLEAN NOT NULL,
    contract_type TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## System Architecture

### 1. Data Ingestion Layer

```python
class TransactionIngester:
    def __init__(self):
        self.blockchain_client = BlockchainClient()
        self.db = Database()
        self.cache = RedisCache()
        
    async def ingest_transactions(self, address):
        # Use WebSocket for real-time updates
        async for block in self.blockchain_client.subscribe_new_blocks():
            transactions = await self.process_block(block)
            await self.store_transactions(transactions)
            
    async def process_block(self, block):
        # Process transactions in parallel
        tasks = [self.process_transaction(tx) for tx in block.transactions]
        return await asyncio.gather(*tasks)
```

### 2. Caching Layer

```python
class TransactionCache:
    def __init__(self):
        self.redis = Redis()
        self.cache_ttl = 3600  # 1 hour
        
    async def get_transactions(self, address, filters):
        cache_key = f"tx:{address}:{hash(filters)}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
            
        data = await self.db.get_transactions(address, filters)
        await self.redis.set(cache_key, json.dumps(data), ex=self.cache_ttl)
        return data
```

### 3. API Layer

```python
class TransactionAPI:
    def __init__(self):
        self.ingester = TransactionIngester()
        self.cache = TransactionCache()
        
    async def get_transactions(self, address, filters):
        # Check cache first
        cached_data = await self.cache.get_transactions(address, filters)
        if cached_data:
            return cached_data
            
        # If not in cache, fetch from database
        return await self.db.get_transactions(address, filters)
```

## Complex Transaction Handling

### Uniswap Transaction Processing

```python
class UniswapTransactionProcessor:
    def process_liquidity_transaction(self, transaction):
        # 1. Decode Method
        method = self.abi_decoder.decode_method(transaction.input)
        
        # 2. Process Based on Method
        if method == "addLiquidity":
            return self.process_add_liquidity(transaction)
        elif method == "removeLiquidity":
            return self.process_remove_liquidity(transaction)
            
    def process_add_liquidity(self, transaction):
        # Extract parameters
        token_a = transaction.decoded_input['tokenA']
        token_b = transaction.decoded_input['tokenB']
        amount_a = transaction.decoded_input['amountADesired']
        amount_b = transaction.decoded_input['amountBDesired']
        
        # Get token prices
        price_a = self.price_oracle.get_price(token_a)
        price_b = self.price_oracle.get_price(token_b)
        
        # Calculate USD value
        usd_value = (amount_a * price_a) + (amount_b * price_b)
        
        return {
            'type': 'ADD_LIQUIDITY',
            'token_a': token_a,
            'token_b': token_b,
            'amount_a': amount_a,
            'amount_b': amount_b,
            'usd_value': usd_value,
            'timestamp': transaction.timestamp
        }
```

## Trade-offs and Considerations

### 1. Accuracy vs. Speed
- **Event Logs**
  - Pros: Accurate, complete data
  - Cons: Slower processing, more storage
  - Use Case: Critical financial operations

- **Transaction Input Data**
  - Pros: Faster processing, less storage
  - Cons: May miss some details
  - Use Case: Real-time monitoring

### 2. Storage vs. Computation
- **Raw Data Storage**
  - Pros: Complete data, flexible analysis
  - Cons: More storage, slower retrieval
  - Use Case: Historical analysis

- **Pre-computed Results**
  - Pros: Fast retrieval, less storage
  - Cons: Limited flexibility
  - Use Case: Real-time dashboards

### 3. Real-time vs. Batch Processing
- **Real-time Processing**
  - Pros: Immediate results
  - Cons: Higher resource usage
  - Use Case: Critical operations

- **Batch Processing**
  - Pros: Efficient resource usage
  - Cons: Delayed results
  - Use Case: Historical data analysis

## Scalability Considerations

### 1. Database Scaling
- Implement sharding based on address ranges
- Use read replicas for query-heavy operations
- Implement connection pooling

### 2. Caching Strategy
- Use Redis for hot data
- Implement cache invalidation policies
- Use CDN for static content

### 3. API Design
- Implement rate limiting
- Use pagination for large result sets
- Implement proper error handling

### 4. Monitoring and Logging
- Implement distributed tracing
- Use structured logging
- Set up alerting for critical metrics

## Future Considerations

1. **Blockchain Integration**
   - Support for multiple networks
   - Cross-chain transaction tracking
   - Layer 2 solutions

2. **Analytics**
   - Real-time analytics
   - Predictive analysis
   - Custom reporting

3. **Security**
   - Rate limiting
   - Input validation
   - Access control

4. **Performance**
   - Query optimization
   - Index optimization
   - Cache optimization 