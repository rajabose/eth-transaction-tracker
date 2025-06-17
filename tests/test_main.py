import pytest
from unittest.mock import Mock, patch
from src.main import TransactionTracker
from datetime import datetime

# Sample test data
SAMPLE_TRANSACTION = {
    'hash': '0x123',
    'blockNumber': '12345',
    'timeStamp': '1625097600',  # 2021-07-01 00:00:00
    'from': '0xabc',
    'to': '0xdef',
    'value': '1000000000000000000',  # 1 ETH
    'gasPrice': '20000000000',  # 20 Gwei
    'gasUsed': '21000',
    'isError': '0',
    'input': '0x',
    'tx_type': 'EXTERNAL'
}

SAMPLE_ERC20_TRANSACTION = {
    'hash': '0x456',
    'blockNumber': '12346',
    'timeStamp': '1625097600',
    'from': '0xabc',
    'to': '0xdef',
    'value': '1000000',  # 1 USDC
    'contractAddress': '0x123',
    'tokenSymbol': 'USDC',
    'tokenDecimal': '6',
    'gasPrice': '20000000000',
    'gasUsed': '65000',
    'isError': '0',
    'input': '0x',
    'tx_type': 'ERC20'
}

@pytest.fixture
def tracker():
    return TransactionTracker('0x123')

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {
        'status': '1',
        'result': [SAMPLE_TRANSACTION]
    }
    return mock

def test_transaction_tracker_initialization(tracker):
    """Test TransactionTracker initialization"""
    assert tracker.address == '0x123'
    assert tracker.transactions == []
    assert tracker.is_large_address is False
    assert tracker.transaction_count == 0

@patch('requests.get')
def test_make_api_request_success(mock_get, tracker, mock_response):
    """Test successful API request"""
    mock_get.return_value = mock_response
    result = tracker.make_api_request('https://api.etherscan.io/api', {'module': 'account'})
    assert result == [SAMPLE_TRANSACTION]

@patch('requests.get')
def test_make_api_request_failure(mock_get, tracker):
    """Test failed API request"""
    mock_get.side_effect = Exception('API Error')
    result = tracker.make_api_request('https://api.etherscan.io/api', {'module': 'account'})
    assert result == []

def test_process_transaction_normal(tracker):
    """Test processing a normal ETH transaction"""
    processed = tracker.process_transaction(SAMPLE_TRANSACTION)
    assert processed is not None
    assert processed['Transaction Hash'] == '0x123'
    assert processed['Transaction Type'] == 'External Transfer'
    assert processed['Value/Amount'] == 1.0  # 1 ETH
    assert processed['Gas Fee (ETH)'] == 0.00042  # 21000 * 20 Gwei

def test_process_transaction_erc20(tracker):
    """Test processing an ERC20 transaction"""
    processed = tracker.process_transaction(SAMPLE_ERC20_TRANSACTION)
    assert processed is not None
    assert processed['Transaction Hash'] == '0x456'
    assert processed['Transaction Type'] == 'ERC-20 Token Transfer'
    assert processed['Asset Symbol/Name'] == 'USDC'
    assert processed['Value/Amount'] == 1.0  # 1 USDC
    assert processed['Asset Contract Address'] == '0x123'

def test_process_transaction_invalid(tracker):
    """Test processing an invalid transaction"""
    invalid_tx = {'hash': '0x789'}  # Missing required fields
    processed = tracker.process_transaction(invalid_tx)
    assert processed is None

@patch('src.main.TransactionTracker.fetch_transactions')
def test_get_all_transactions(mock_fetch, tracker):
    """Test getting all transactions"""
    mock_fetch.return_value = [SAMPLE_TRANSACTION]
    transactions = tracker.get_all_transactions()
    assert len(transactions) == 1
    assert transactions[0]['hash'] == '0x123'

def test_process_small_transactions(tracker):
    """Test processing small transactions"""
    tracker.transactions = [SAMPLE_TRANSACTION, SAMPLE_ERC20_TRANSACTION]
    processed = tracker.process_small_transactions()
    assert len(processed) == 2
    assert processed[0]['Transaction Hash'] == '0x123'
    assert processed[1]['Transaction Hash'] == '0x456'

@patch('os.path.join')
@patch('pandas.DataFrame')
def test_save_transactions(mock_df, mock_path, tracker):
    """Test saving transactions"""
    mock_path.return_value = 'test.csv'
    mock_df_instance = Mock()
    mock_df.return_value = mock_df_instance
    
    tracker.save_transactions([{
        'Transaction Hash': '0x123',
        'Date & Time': '2021-07-01 00:00:00',
        'From Address': '0xabc',
        'To Address': '0xdef',
        'Transaction Type': 'External Transfer',
        'Value/Amount': 1.0,
        'Gas Fee (ETH)': 0.00042
    }])
    
    mock_df_instance.to_csv.assert_called_once()

def test_large_address_detection(tracker):
    """Test large address detection"""
    # Simulate fetching more than 10000 transactions
    tracker.transactions = [SAMPLE_TRANSACTION] * 10001
    tracker.is_large_address = False
    
    # Process transactions
    tracker.process_transactions()
    
    assert tracker.is_large_address is True 