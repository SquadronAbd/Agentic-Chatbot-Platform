from app.memory.session import SessionManager

manager = SessionManager()

abd = manager.get_memory("abdullah")

abd.add_user_message("Hello")

abd.add_ai_message("Hi Abdullah!")

ali = manager.get_memory("ali")

ali.add_user_message("What is AI?")

ali.add_ai_message("Artificial Intelligence")

print("=" * 60)
print("ACTIVE SESSIONS")
print("=" * 60)

print(manager.list_sessions())

print()

print("=" * 60)
print("ABDULLAH MEMORY")
print("=" * 60)

for message in abd.get_history():
    print(message.role, ":", message.content)

print()

print("=" * 60)
print("ALI MEMORY")
print("=" * 60)

for message in ali.get_history():
    print(message.role, ":", message.content)

print()

print("=" * 60)
print("TOTAL SESSIONS")
print("=" * 60)

print(manager.total_sessions())