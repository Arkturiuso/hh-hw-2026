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


def test_create_user_converts_id_to_int() -> None:
    switchboard = Switchboard()
    
    user = switchboard.create_user("3", "Pedro Grunge" , "+70009998887")
    
    assert isinstance(user.id, int)
    assert user.id == 3


def test_create_user_returns_correct_type() -> None:
    switchboard = Switchboard()
    
    first_user = switchboard.create_user("1", "Alice Laren", "+79990000000")
    assert isinstance(first_user, LocalUser)
    
    second_user = switchboard.create_user("2", "Gilbert North", "+22233344455")
    assert isinstance(second_user, ForeignUser)


def test_caller_and_receiver_phone_location() -> None:
    switchboard = Switchboard()

    new_call = switchboard.register_call(
        "4,Charlie Green,+70009998887,5,John Pork,+488997766554"
    )

    assert switchboard.is_local_phone_number(new_call.caller.phone)
    assert not switchboard.is_local_phone_number(new_call.receiver.phone)


def test_caller_and_receiver_data_correctly_processed() -> None:
    switchboard = Switchboard()

    new_call = switchboard.register_call(
        "1,Jack Sparrow,+71234567891,2,John Snow,+20987654321"
    )

    assert new_call.caller.id == 1
    assert new_call.caller.fullname == 'Jack Sparrow'
    assert new_call.caller.phone == '+71234567891'

    assert new_call.receiver.id == 2
    assert new_call.receiver.fullname == 'John Snow'
    assert new_call.receiver.phone == '+20987654321'

    assert new_call.caller is not new_call.receiver


def test_register_call_with_spaces_in_names() -> None:
    switchboard = Switchboard()
    
    new_call = switchboard.register_call(
        "2,     Charlie Green   ,+70009998887,3,  John Pork     ,+488997766554"
    )
    
    assert new_call.caller.fullname == "Charlie Green"
    assert new_call.receiver.fullname == "John Pork"
