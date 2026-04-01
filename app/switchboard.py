from __future__ import annotations

from dataclasses import dataclass

import re

from app.users import User, LocalUser, ForeignUser



LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls_count: int = 0

    @staticmethod
    def strip_all(*args: str) -> tuple[str, ...]:
        return tuple(arg.strip() for arg in args)
    
    @staticmethod 
    def parse_id(id: str) -> int:
        if not re.match(r'^[1-9]\d*$', id):
            raise ValueError(f"Invalid user id: {id}")
        return int(id)
        
    @staticmethod
    def is_valid_fullname(fullname: str) -> bool:
        if not all(char.isalpha() or char.isspace() for char in fullname):
            return False
        
        fullname_parts = fullname.split()
        return len(fullname_parts) in (2, 3)
     
    @staticmethod
    def is_valid_local_phone(phone_number: str) -> bool:
        pattern = r'^\+7\d{10}$'
        return bool(re.match(pattern, phone_number))

    @staticmethod
    def is_valid_foreign_phone(phone_number: str) -> bool:
        pattern = r'^\+[1-68-9]\d{8,}$'
        return bool(re.match(pattern, phone_number))
    
    def is_duplicate_call(self, caller_id: int, receiver_id: int) -> bool: 
        for active_call in self._active_calls:
            if (caller_id == active_call.caller.id and
                receiver_id == active_call.receiver.id):
                return True
        return False

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,reciever_id,reciever_name,reciever_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        raw_parts = raw_call.split(',')
        if len(raw_parts) != 6:
            raise ValueError(f"Expected 6 fields. Got {len(raw_parts)}")
        
        cleaned_parts = self.strip_all(*raw_parts)
        caller_parts = cleaned_parts[:3]
        receiver_parts = cleaned_parts[3:]

        caller = self.create_user(*caller_parts)
        receiver = self.create_user(*receiver_parts)

        if caller.id == receiver.id:
            raise ValueError("Caller cannot call himself")
        
        if self.is_duplicate_call(caller.id, receiver.id):
            raise ValueError(f'Duplicate call from {caller.id} to {receiver.id}')
        
        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        return active_call
    
    def create_user(self, user_id: str, user_fullname: str, user_phone_number: str) -> User:
        numeric_user_id = self.parse_id(user_id)
        if not self.is_valid_fullname(user_fullname):
            raise ValueError(f"Invalid fullname: {user_fullname}")

        if self.is_valid_local_phone(user_phone_number):
            return LocalUser(numeric_user_id, user_fullname, user_phone_number)

        if self.is_valid_foreign_phone(user_phone_number):
            return ForeignUser(numeric_user_id, user_fullname, user_phone_number)
        raise ValueError(f"Invalid phone number: {user_phone_number}")

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count

