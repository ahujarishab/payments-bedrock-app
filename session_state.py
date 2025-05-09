import streamlit as st

def initialize_session_state():
    """
    Initialize all required session state variables
    """
    if 'json_data' not in st.session_state:
        st.session_state.json_data = None
    if 'response' not in st.session_state:
        st.session_state.response = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'payment_history' not in st.session_state:
        st.session_state.payment_history = []
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = "payment_orchestrator"

def get_default_json_template():
    """
    Return the default JSON template for payment processing
    """
    return '''{
  "header": {
    "MerchantID": "Mrt1234567890",   
    "OrderNumber": "AP005678",
    "LocalDateTime": "241104160510",
    "TransactionID": "12456890242",
    "TerminalID": "20",
    "SettleIndicator": "true",
    "UniqueRequestNumber": "TEST95765432"
  },
  "request": {
    "RequestType": "Sale",
    "InputType": "Keyed",
    "DeviceType": "I" 
  },                
  "PaymentDetails": {
    "PaymentType": "Credit",           
    "Media": "MC"     
  },
  "CardDetails": {
    "AccountType": "PAN",
    "AccountNumber": "6006199750003330026",
    "CardVerificationValue": "356",
    "Expiration": "04/29",
    "Amount": "12.00",
    "CurrencyCode": "678" 
  },
  "CustomerDetails": {
    "CustomerName": "John Doe",
    "CustomerID": "12345678901",
    "EmailID": "john.doe@example.com",
    "AddressVerification": {
      "Address1": "4011, Stary Cir Dr",
      "Address2": "Travis",
      "City": "Austin",
      "CountryCode": "US",
      "State": "Texas",
      "Postalcode": "1234-78730"
    }
  }
}'''