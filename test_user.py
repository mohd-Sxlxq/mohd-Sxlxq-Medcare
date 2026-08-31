from backend.user import (
    authenticate_user,
    get_connection_code,
    verify_connection_code,
    connect_caregiver_to_senior,
    get_my_seniors,
    get_connected_caregivers
)


print("================================")
print("TESTING LOGIN")
print("================================")

# Existing Senior account
senior_role = authenticate_user(
    "senior_test1",
    "Test@12345"
)

print("Senior login role:", senior_role)


print("\n================================")
print("TESTING SENIOR-CAREGIVER CONNECTION")
print("================================")


# =========================================================
# GET SENIOR CONNECTION CODE
# =========================================================

print("\nGetting Senior connection code...")

connection_code = get_connection_code(
    "senior_test1"
)

print("Connection code:", connection_code)


# =========================================================
# VERIFY CONNECTION CODE
# =========================================================

print("\nVerifying connection code...")

code_valid = verify_connection_code(
    connection_code
)

print("Code valid:", code_valid)


# =========================================================
# LOGIN AS CAREGIVER
# =========================================================

print("\nLogging in as Caregiver...")

caregiver_role = authenticate_user(
    "caregiver_test1",
    "Test@12345"
)

print("Caregiver login role:", caregiver_role)


# =========================================================
# CONNECT CAREGIVER
# =========================================================

print("\nConnecting caregiver to Senior...")

connection_result = connect_caregiver_to_senior(
    connection_code,
    "caregiver_test1"
)

print("Connection result:", connection_result)


# =========================================================
# GET CAREGIVER'S SENIORS
# =========================================================

print("\nGetting caregiver's connected Seniors...")

seniors = get_my_seniors(
    "caregiver_test1"
)

print("Caregiver's Seniors:", seniors)


# =========================================================
# GET SENIOR'S CAREGIVERS
# =========================================================

print("\nGetting Senior's connected Caregivers...")

caregivers = get_connected_caregivers(
    "senior_test1"
)

print("Senior's Caregivers:", caregivers)