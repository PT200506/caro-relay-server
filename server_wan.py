import asyncio
import websockets
import json

rooms = {}  # room_id -> {"A": ws, "B": ws}


async def handler(ws):
    player = None
    room_id = None

    try:
        async for message in ws:
            data = json.loads(message)
            msg_type = data.get("type")

            # --- Client join phòng ---
            if msg_type == "join":
                room_id = data["room"]
                player = data["player"]

                if room_id not in rooms:
                    rooms[room_id] = {}

                rooms[room_id][player] = ws
                print(f"Player {player} joined room {room_id}")

            # --- Relay nước đi ---
            elif msg_type == "move":
                room = data["room"]
                other = "B" if data["player"] == "A" else "A"

                # Nếu có player còn lại
                if room in rooms and other in rooms[room]:
                    await rooms[room][other].send(json.dumps(data))

            # --- Relay reset ---
            elif msg_type == "reset":
                room = data["room"]
                other = "B" if data["player"] == "A" else "A"

                if room in rooms and other in rooms[room]:
                    await rooms[room][other].send(json.dumps(data))

    except:
        print("Client disconnected")
    finally:
        # Cleanup
        if room_id and player and room_id in rooms:
            if player in rooms[room_id]:
                del rooms[room_id][player]
            if len(rooms[room_id]) == 0:
                del rooms[room_id]


async def main():
    print("Relay server chạy tại port 8000...")
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # keep running


asyncio.run(main())
