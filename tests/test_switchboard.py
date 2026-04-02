import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_parse_id() -> None:
    switchboard = Switchboard()
    
    assert switchboard.parse_id("1") == 1
    assert switchboard.parse_id("123") == 123
    
    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("12З")
    
    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("O0O")
    
    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("4.7")

    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("4 7")

    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("0")

    with pytest.raises(ValueError, match="Invalid user id"):
        switchboard.parse_id("-3")


def test_is_valid_fullname() -> None:
    """Проверка валидации полного имени"""
    switchboard = Switchboard()
    

    assert switchboard.is_valid_fullname("Ivan Ivanov") is True 
    assert switchboard.is_valid_fullname("Ivan Ivanovich Ivanov") is True
    assert switchboard.is_valid_fullname("  Ivan Ivanov    ") is True 
    
    assert switchboard.is_valid_fullname("Ivan") is False
    assert switchboard.is_valid_fullname("") is False
    assert switchboard.is_valid_fullname("Ivan Ivanov Ali Ivanovich") is False
    assert switchboard.is_valid_fullname("2 3") is False


def test_is_valid_foreign_phone() -> None:
    switchboard = Switchboard()
    
    assert switchboard.is_valid_foreign_phone("+15551234567") is True
    assert switchboard.is_valid_foreign_phone("+431234567") is True
    
    assert switchboard.is_valid_foreign_phone("+7567824567") is False
    assert switchboard.is_valid_foreign_phone("+44 201 234 56 78") is False
    assert switchboard.is_valid_foreign_phone("15551234567") is False
    assert switchboard.is_valid_foreign_phone("+7123OOO") is False


def test_phone_number_edge_cases() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match='Invalid phone number'):
        switchboard.register_call("5,Jane Doe,+331,6,Alex Doe,+442012345678")
    
    with pytest.raises(ValueError, match='Invalid phone number'):
        switchboard.register_call("4,John Doe,33123456567,6,Alex Doe,+442012345678")
    
    with pytest.raises(ValueError, match='Invalid phone number'):
        switchboard.register_call("5,Jane Doe,+442012345678,6,Alex Doe,+44-201-234-56-78")

    with pytest.raises(ValueError, match='Invalid phone number'):
        switchboard.register_call("4,John Doe,+7123З0123,6,Alex Doe,+442012345678")

    
def test_caller_and_receiver_phone_location() -> None:
    switchboard = Switchboard()

    new_call = switchboard.register_call(
        "4,Charlie Green,+70009998887,5,John Pork,+488997766554"
    )

    assert switchboard.is_valid_local_phone(new_call.caller.phone)
    assert switchboard.is_valid_foreign_phone(new_call.receiver.phone)


def test_create_user_returns_correct_type() -> None:
    switchboard = Switchboard()
    
    first_user = switchboard.create_user("1", "Alice Laren", "+79990000000")
    assert isinstance(first_user, LocalUser)
    
    second_user = switchboard.create_user("2", "Gilbert North", "+22233344455")
    assert isinstance(second_user, ForeignUser)


def test_register_call_with_spaces_in_names() -> None:
    switchboard = Switchboard()
    
    new_call = switchboard.register_call(
        "2,     Charlie Green   ,+70009998887,3,  John Pork     ,+488997766554"
    )
    
    assert new_call.caller.fullname == "Charlie Green"
    assert new_call.receiver.fullname == "John Pork"


def test_register_call_with_invalid_fields_amount() -> None:
    switchboard = Switchboard()
    
    with pytest.raises(ValueError, match='Expected 6 fields.'):
        switchboard.register_call("1,Ivan,+79990000000,2,John")


def test_register_caller_unable_call_himself() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Caller cannot call himself"):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,1,Ivan Ivanov,+79990000000"
        )
    
    with pytest.raises(ValueError, match="Caller cannot call himself"):
        switchboard.register_call(
            "2,John Smith,+12222222222,2,John Smith,+12222222222"
        )


def test_register_call_duplicate_calls_raise_error() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+12222222222"
    )
    
    with pytest.raises(ValueError, match="Duplicate call"):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,John Smith,+12222222222"
        )

    with pytest.raises(ValueError, match="Duplicate call"):
        switchboard.register_call(
            "1,Petrov Petr,+70009998887,2,Swen Rein,+488997766554"
        )


def test_register_call_different_order_calls_allowed() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+12222222222"
    )

    switchboard.register_call(
        "2,John Smith,+12222222222,1,Ivan Ivanov,+79990000000"
    )


def test_large_number_of_calls() -> None:
    switchboard = Switchboard()
    calls_count = 10_000
    
    for call in range(1, calls_count + 1):
        switchboard.register_call(
            f"{call},Ivanov Ivan,+79990000000,{call + 1},Petrov Petr,+15551234567"
        )
    
    assert switchboard.get_active_calls_count() == calls_count
    assert switchboard.get_cross_border_calls_count() == calls_count


def test_show_call_info() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    
    info = switchboard.show_call_info(0)
    assert 'Ivan Ivanov' in info
    assert 'John Smith' in info
    assert '+79990000000' in info
    assert '+15551234567' in info


def test_show_call_info_invalid_index() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    
    with pytest.raises(IndexError, match="Invalid call index"):
        switchboard.show_call_info(5)

    with pytest.raises(IndexError, match="Invalid call index"):
        switchboard.show_call_info(-1)


def test_find_user_calls() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("1,Ivan Ivanov,+79990000000,3,Peter Brown,+15551234568")
    
    calls = switchboard.find_user_calls(1)
    assert len(calls) == 2
    
    calls = switchboard.find_user_calls(4)
    assert len(calls) == 0


def test_find_caller_calls() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("2,John Smith,+15551234567,3,Peter Brown,+15551234568")
    
    calls = switchboard.find_caller_calls(1)
    assert len(calls) == 1

    calls = switchboard.find_caller_calls(3)
    assert len(calls) == 0


def test_find_receiver_calls() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("3,Peter Brown,+15551234568,1,Ivan Ivanov,+79990000000")
    
    calls = switchboard.find_receiver_calls(2)
    assert len(calls) == 1
    
    calls = switchboard.find_receiver_calls(3)
    assert len(calls) == 0


def test_end_call_by_index() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("3,Petr Petrov,+79991112233,4,Maria Grey,+15559876543")
    
    assert switchboard.get_active_calls_count() == 2
    
    ended_call = switchboard.end_call_by_index(0)
    assert ended_call.caller.id == 1
    assert switchboard.get_active_calls_count() == 1

    with pytest.raises(IndexError, match="Invalid call index"):
        switchboard.end_call_by_index(3)


def test_end_last_call() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("3,Petr Petrov,+79991112233,4,Maria Grey,+15559876543")
    
    ended_call = switchboard.end_last_call()
    assert ended_call.caller.id == 3
    assert switchboard.get_active_calls_count() == 1


def test_end_last_call_empty() -> None:
    switchboard = Switchboard()
    
    with pytest.raises(ValueError, match="No active calls"):
        switchboard.end_last_call()


def test_end_all_calls() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("3,Petr Petrov,+79991112233,4,Maria Grey,+15559876543")
    
    ended_calls_count = switchboard.end_all_calls()
    
    assert ended_calls_count == 2
    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0


def test_get_all_active_participant_ids() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("1,Ivan Ivanov,+79990000000,3,Petr Petrov,+15551234568")
    
    participants = switchboard.get_all_active_participant_ids()
    assert participants == {1, 2, 3}


def test_get_all_active_participant_ids_empty() -> None:
    switchboard = Switchboard()
    
    participants = switchboard.get_all_active_participant_ids()
    assert participants == set()


def test_get_user_calls_count() -> None:
    switchboard = Switchboard()
    switchboard.register_call("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567")
    switchboard.register_call("1,Ivan Ivanov,+79990000000,3,Petr Petrov,+15551234568")
    
    assert switchboard.get_user_calls_count(1) == 2
    assert switchboard.get_user_calls_count(2) == 1
    assert switchboard.get_user_calls_count(4) == 0