from .schema import Message

def cut_messages(messages: list[Message], max_len: int = 1000, max_turn:int = 8) -> list[Message]:
    new_messages: list[Message] = []
    len_sum = 0
    for i in range(len(messages) -1, -1, -1):
        if len(new_messages) >= max_turn:
            break
        if len_sum > max_len:
            break
        message = messages[i]
        if len(message.content) >= max_len:
            if len(new_messages) == 0:
                new_messages.append(Message(role=message.role, content=message.content[:max_len]))
                break
            else:
                break
        new_messages.insert(0, message)
        len_sum += len(message.content)
    return new_messages