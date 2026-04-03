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
        self._calls_by_users: dict[int, list[ActiveCall]] = {}
        self._calls_by_callers: dict[int, list[ActiveCall]] = {}
        self._calls_by_receivers: dict[int, list[ActiveCall]] = {}
        self._active_calls_set: set[tuple[int, int]] = set()

    @staticmethod
    def strip_all(*args: str) -> tuple[str, ...]:
        return tuple(arg.strip() for arg in args)
    
    @staticmethod 
    def parse_id(id: str) -> int:
        if not id.isnumeric():
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
    
    def is_duplicate_call(self, call_participant_ids: tuple[int, int]) -> bool: 
        return call_participant_ids in self._active_calls_set

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
        call_participants_ids = (caller.id, receiver.id)

        if caller.id == receiver.id:
            raise ValueError("Caller cannot call himself")

        if self.is_duplicate_call(call_participants_ids):
            raise ValueError(f'Duplicate call from {caller.id} to {receiver.id}')
        
        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)
        self._active_calls_set.add(call_participants_ids)

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        self._calls_by_callers.setdefault(caller.id, []).append(active_call)
        
        self._calls_by_receivers.setdefault(receiver.id, []).append(active_call)
        
        self._calls_by_users.setdefault(caller.id, []).append(active_call)
        self._calls_by_users.setdefault(receiver.id, []).append(active_call)

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

    def show_call_info(self, call_index: int) -> str:
        if call_index >= len(self._active_calls) or call_index < 0:
            raise IndexError(f"Invalid call index: {call_index}")
        
        call = self._active_calls[call_index]
        return f'''Звонок #{call_index}
                    Отправитель: {call.caller.fullname} ({call.caller.phone})
                    Получатель: {call.receiver.fullname} ({call.receiver.phone})\n'''
    
    def find_user_calls(self, user_id: int) -> list[ActiveCall]:
        return self._calls_by_users.get(user_id, []).copy()

    def find_caller_calls(self, user_id: int) -> list[ActiveCall]:
        return self._calls_by_callers.get(user_id, []).copy()

    def find_receiver_calls(self, user_id: int) -> list[ActiveCall]:
        return self._calls_by_receivers.get(user_id, []).copy()
    
    def _remove_from_dicts(self, call: ActiveCall) -> None:
        caller_id = call.caller.id
        receiver_id = call.receiver.id
        
        self._calls_by_callers[caller_id].remove(call)
        if not self._calls_by_callers[caller_id]:
            del self._calls_by_callers[caller_id]
        
        self._calls_by_receivers[receiver_id].remove(call)
        if not self._calls_by_receivers[receiver_id]:
            del self._calls_by_receivers[receiver_id]
        
        for user_id in [caller_id, receiver_id]:
            self._calls_by_users[user_id].remove(call)
            if not self._calls_by_users[user_id]:
                del self._calls_by_users[user_id]
        
        self._active_calls_set.remove((caller_id, receiver_id))
    
    def end_call_by_index(self, call_index: int) -> ActiveCall:
        if call_index < 0 or call_index >= len(self._active_calls):
            raise IndexError(f"Invalid call index: {call_index}")
        
        ended_call = self._active_calls.pop(call_index)
        self._remove_from_dicts(ended_call)
        
        if ended_call.is_cross_border:
            self._cross_border_calls_count -= 1
        return ended_call
    
    def end_last_call(self) -> ActiveCall:
        if not self._active_calls:
            raise ValueError("No active calls")
        
        ended_call = self._active_calls.pop()
        self._remove_from_dicts(ended_call)
        
        if ended_call.is_cross_border:
            self._cross_border_calls_count -= 1
        return ended_call
    
    def end_all_calls(self) -> int:
        count = len(self._active_calls)
        self._active_calls.clear()
        self._calls_by_users.clear()
        self._calls_by_callers.clear()
        self._calls_by_receivers.clear()
        self._active_calls_set.clear()
        self._cross_border_calls_count = 0
        return count
    
    def get_all_active_participant_ids(self) -> set[int]:
        participants = set()
        for call in self._active_calls:
            participants.add(call.caller.id)
            participants.add(call.receiver.id)
        return participants

    def get_user_calls_count(self, user_id: int) -> int:
        return len(self.find_user_calls(user_id))

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count