from app.services.execution_service import execute_approved_action

# Test 1: Approved request
approved_request = {
    "approval_id": "APR-1001",
    "approval_status": "approved"
}

result = execute_approved_action(approved_request)

print("Approved Request:")
print(result)


# Test 2: Pending request
pending_request = {
    "approval_id": "APR-1002",
    "approval_status": "pending"
}

result2 = execute_approved_action(pending_request)

print("\nPending Request:")
print(result2)