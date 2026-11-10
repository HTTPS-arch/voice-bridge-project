import asyncio
from dotenv import load_dotenv
from livekit import api

load_dotenv()


async def _find_call(lkapi):
    """Return (room, caller number, status) for a live SIP call, or None."""
    rooms = await lkapi.room.list_rooms(api.ListRoomsRequest())
    for r in rooms.rooms:
        if not r.name.startswith("pre"):
            continue
        parts = await lkapi.room.list_participants(
            api.ListParticipantsRequest(room=r.name)
        )
        for p in parts.participants:
            if p.identity.startswith("sip_"):
                status = p.attributes.get("sip.callStatus", "")
                if status in ("ringing", "active"):
                    return r.name, p.attributes.get("sip.phoneNumber", p.identity), status
    return None


async def find_call(lkapi):
    try:
        return await _find_call(lkapi)
    except Exception as e:
        print(f"(lookup failed, retrying: {e})")
        return None


async def main():
    lkapi = api.LiveKitAPI()
    print("Waiting for incoming calls... (Ctrl+C to quit)")
    try:
        while True:
            call = await find_call(lkapi)
            if not call or call[2] != "ringing":
                await asyncio.sleep(1.5)
                continue

            room, number, _ = call
            print(f"\nIncoming call from {number}")
            await asyncio.to_thread(input, "Press Enter to ANSWER... ")

            try:
                await lkapi.room.update_room_metadata(
                    api.UpdateRoomMetadataRequest(room=room, metadata="answer")
                )
            except Exception as e:
                print(f"Could not answer (caller may have hung up): {e}\n")
                continue

            for _ in range(10):
                await asyncio.sleep(0.5)
                now = await find_call(lkapi)
                if now and now[2] == "active":
                    break
            else:
                print("Warning: the call did not become active.")

            await asyncio.to_thread(input, "Call is live. Press Enter to HANG UP... ")
            try:
                await lkapi.room.delete_room(api.DeleteRoomRequest(room=room))
            except Exception as e:
                print(f"(Room already closed: {e})")
            print("Call ended.\n")
    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(main())