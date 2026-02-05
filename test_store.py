from jsonschema import validate
import pytest
import schemas
from api_helpers import get_api_data, post_api_data, patch_api_data


@pytest.fixture(scope="function")
def create_test_order():
    """
    Fixture to create a fresh order for each test run.
    Finds an available pet and creates an order automatically.
    Scope: function - creates new order for each test that uses this fixture.
    """
    # Find an available pet
    available_pets_response = get_api_data('/pets/findByStatus', params={'status': 'available'})
    available_pets = available_pets_response.json()

    if len(available_pets) == 0:
        pytest.skip("No available pets to create order")

    pet_id = available_pets[0]['id']

    # Create an order
    order_data = {'pet_id': pet_id}
    response = post_api_data('/store/order', order_data)

    return {
        'order_id': response.json()['id'],
        'pet_id': pet_id,
        'response': response
    }


'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id} 
2) *Optional* Consider using @pytest.fixture to create unique test data for each run 
3) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test 
4) Validate the response codes and values 
5) Validate the response message "Order and pet status updated successfully" 
'''
def test_patch_order_by_id(create_test_order):
    """Test updating an order status via PATCH request"""
    # Get order details from fixture
    order_id = create_test_order['order_id']
    pet_id = create_test_order['pet_id']
    create_response = create_test_order['response']

    # Verify order was created successfully
    assert create_response.status_code == 201

    # Validate the created order matches the Order schema
    created_order = create_response.json()
    validate(instance=created_order, schema=schemas.order)

    # Validate order ID format (UUID)
    assert order_id is not None, "Order ID should not be None"
    assert isinstance(order_id, str), "Order ID should be a string (UUID)"
    assert len(order_id) == 36, "UUID should be 36 characters (with hyphens)"

    # Update the order status to 'sold'
    update_data = {'status': 'sold'}
    patch_response = patch_api_data(f'/store/order/{order_id}', update_data)

    # Verify the PATCH request was successful
    assert patch_response.status_code == 200

    # Verify the success message
    response_json = patch_response.json()
    assert response_json['message'] == "Order and pet status updated successfully"

    # Verify the pet's status was also updated
    pet_response = get_api_data(f'/pets/{pet_id}')
    pet_data = pet_response.json()
    assert pet_data['status'] == 'sold'

    # Validate the pet still matches the Pet schema
    validate(instance=pet_data, schema=schemas.pet)

    # Verify order ID remains unique by creating another order
    available_pets_response = get_api_data('/pets/findByStatus', params={'status': 'available'})
    available_pets = available_pets_response.json()

    if len(available_pets) > 0:
        second_order_data = {'pet_id': available_pets[0]['id']}
        second_order_response = post_api_data('/store/order', second_order_data)

        if second_order_response.status_code == 201:
            second_order = second_order_response.json()

            # Validate second order schema
            validate(instance=second_order, schema=schemas.order)

            second_order_id = second_order['id']
            # Verify the two order IDs are unique
            assert order_id != second_order_id, "Order IDs should be unique"