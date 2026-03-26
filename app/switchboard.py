from __future__ import annotations

from dataclasses import dataclass

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
    def is_local_phone_number(phone_number: str) -> bool:
        return phone_number.startswith(LOCAL_PHONE_PREFIX)

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,reciever_id,reciever_name,reciever_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        raw_parts = raw_call.split(',')
        cleaned_parts = self.strip_all(*raw_parts)

        caller_parts = cleaned_parts[:3]
        receiver_parts = cleaned_parts[3:]

        caller = self.create_user(*caller_parts)
        receiver = self.create_user(*receiver_parts)
        
        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        return active_call
    
    def create_user(self, user_id: str, user_fullname: str, user_phone_number: str) -> User:
        user_id = int(user_id)
        if self.is_local_phone_number(user_phone_number):
            return LocalUser(user_id, user_fullname, user_phone_number)
        return ForeignUser(user_id, user_fullname, user_phone_number)

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count

