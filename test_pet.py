from jsonschema import validate
import pytest
import schemas
import api_helpers
import logging
from hamcrest import assert_that, contains_string

'''
TODO: Finish this test by...
1) Troubleshooting and fixing the test failure
The purpose of this test is to validate the response matches the expected schema defined in schemas.py
'''
def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 200

    # Validate the response schema against the defined schema in schemas.py
    validate(instance=response.json(), schema=schemas.pet)

'''
TODO: Finish this test by...
1) Extending the parameterization to include all available statuses
2) Validate the appropriate response code
3) Validate the 'status' property in the response is equal to the expected status
4) Validate the schema for each object in the response
'''

# 1) Extending the parameterization to include all available statuses
@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_find_by_status_200(status):
    test_endpoint = "/pets/findByStatus"
    params = {"status": status}

    # Make the API request
    response = api_helpers.get_api_data(test_endpoint, params)

    # 2) Validate the appropriate response code
    # Verify we got a successful response code
    assert response.status_code == 200

    # Get the list of pets from response
    pets = response.json()
    # Validate response is a list
    assert isinstance(pets, list)

    # 3) Validate the 'status' property in the response is equal to the expected status
    # 4) Validate the schema for each object in the response
    for pet in pets:
        assert pet['status'] == status, f"Pet property status is different than {status}"
        validate(instance=pet, schema=schemas.pet)

'''
TODO: Finish this test by...
1) Testing and validating the appropriate 404 response for /pets/{pet_id}
2) Parameterizing the test for any edge cases
'''
@pytest.mark.parametrize("pet_id, description", [(999, "non-existent ID"),
                                                 (0.9, "floating number"),
                                                 (-1, "negative ID")])
def test_get_by_id_404(pet_id, description):
    # Try to get a pet that doesn't exist or with invalid ID format
    test_endpoint = f"/pets/{pet_id}"

    response = api_helpers.get_api_data(test_endpoint)

    # Verify we get a 404 Not Found response
    assert response.status_code == 404, f"Expected 404 for {description}, got {response.status_code}"

    # Try to parse JSON response if available
    # Some 404s return JSON (API errors), others return HTML (Flask route errors)
    try:
        response_data = response.json()
        assert 'message' in response_data
        assert_that(response_data['message'], contains_string("not found"))
    except ValueError:
        # HTML 404 from Flask - this is expected for invalid route patterns
        assert "404" in response.text or "Not Found" in response.text


# Additional test for invalid ID format (string IDs)
@pytest.mark.parametrize("pet_id", [
    "abc",           # Pure letters
    "12test",        # Numbers + letters
    "test123",       # Letters + numbers
    "1.5",           # Decimal/float string
    "1e10",          # Scientific notation
    "pet-1",         # With special characters
    "pet_1",         # With underscore
    " ",             # Single space
    "   ",           # Multiple spaces
])
def test_get_by_invalid_id_format_404(pet_id):
    # Try to get a pet with invalid ID format
    test_endpoint = f"/pets/{pet_id}"

    response = api_helpers.get_api_data(test_endpoint)

    # Flask returns 404 for routes that don't match the int type converter
    assert response.status_code == 404


# Test creating pet with invalid enum values 'type' or 'status':
@pytest.mark.xfail(reason="BUG#4 - API POST /pets/ doesn't validate enum values, allows creating pets with "
                          "invalid type or status")
@pytest.mark.parametrize("pet_data", [
    {'id': 100, 'name': 'test', 'type': 'bird', 'status': 'available'},  # Invalid type
    {'id': 101, 'name': 'test', 'type': 'cat', 'status': 'reserved'},  # Invalid status
])
def test_create_pet_invalid_enum_400(pet_data):
    """Test creating pet with invalid enum values"""
    response = api_helpers.post_api_data('/pets/', pet_data)
    assert response.status_code == 400
