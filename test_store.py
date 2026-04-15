from jsonschema import validate
import pytest
import schemas
from api_helpers import get_api_data, post_api_data, patch_api_data, delete_api_data


@pytest.fixture(scope="function")
def create_test_order():
    """Finds an available pet and creates an order. Yields order details, cleans up after."""
    available_pets = get_api_data('/pets/findByStatus', params={'status': 'available'}).json()
    if not available_pets:
        pytest.skip("No available pets to create order")

    pet_id = available_pets[0]['id']
    order_response = post_api_data('/store/order', {'pet_id': pet_id})
    assert order_response.status_code == 201

    order_id = order_response.json()['id']
    yield {'order_id': order_id, 'pet_id': pet_id}

    # Teardown - reset pet status back to available for subsequent tests
    patch_api_data(f'/store/order/{order_id}', {'status': 'available'})

    # Cleanup - delete order and pet once DELETE endpoints are implemented
    delete_api_data(f'/store/order/{order_id}')
    delete_api_data(f'/pets/{pet_id}')

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
3) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
4) Validate the response codes and values
5) Validate the response message "Order and pet status updated successfully"
'''
@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_patch_order_by_id_200(create_test_order, status):
    order_id = create_test_order['order_id']
    pet_id = create_test_order['pet_id']

    response = patch_api_data(f'/store/order/{order_id}', {'status': status})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json()['message'] == "Order and pet status updated successfully"

    # Verify pet status was also updated as side effect
    pet_data = get_api_data(f'/pets/{pet_id}').json()
    assert pet_data['status'] == status
    validate(instance=pet_data, schema=schemas.pet)


@pytest.mark.xfail(reason="Invalid status returns 201 instead of 400")
def test_patch_order_by_id_400(create_test_order):
    response = patch_api_data(
        f'/store/order/{create_test_order["order_id"]}', {'status': 'not_available'}
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


def test_patch_order_by_id_404():
    # Use a valid UUID format that won't exist in the system
    response = patch_api_data('/store/order/00000000-0000-0000-0000-000000000000', {'status': 'sold'})
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def test_order_schema(create_test_order):
    order = {'id': create_test_order['order_id'], 'pet_id': create_test_order['pet_id']}
    validate(instance=order, schema=schemas.order)
    assert isinstance(order['id'], str)
    assert len(order['id']) == 36, "UUID should be 36 characters"