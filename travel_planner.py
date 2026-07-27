import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

flights_agent = Agent(
    name="flights_agent",
    model="gemini-3.5-flash",
    description="Suggests flight options for a trip.",
    instruction="You suggest realistic flight routes and rough price ranges for the requested trip. Keep it brief.",
)

hotels_agent = Agent(
    name="hotels_agent",
    model="gemini-3.5-flash",
    description="Suggests hotel/accommodation options for a trip.",
    instruction="You suggest 2-3 accommodation options fitting the trip's destination and budget vibe. Keep it brief.",
)

itinerary_agent = Agent(
    name="itinerary_agent",
    model="gemini-3.5-flash",
    description="Plans a day-by-day itinerary of activities for a trip.",
    instruction="You create a simple day-by-day activity plan for the requested trip length and destination.",
)

coordinator = Agent(
    name="travel_coordinator",
    model="gemini-3.5-flash",
    description="Coordinates a full trip plan using flights, hotels, and itinerary sub-agents.",
    instruction=(
        "You are a travel planning coordinator. Given a trip request, "
        "delegate to flights_agent, hotels_agent, and itinerary_agent as needed, "
        "then combine their answers into one clear, organized trip plan."
    ),
    sub_agents=[flights_agent, hotels_agent, itinerary_agent],
)


async def main():
    runner = InMemoryRunner(agent=coordinator)
    user_id = "user1"
    session_id = "session1"

    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    print("Travel Planner ready! Type 'exit' to quit.\n")

    while True:
        request = input("You: ")
        if request.lower() == "exit":
            break

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=request)]),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\nAgent: {part.text}")

if __name__ == "__main__":
    asyncio.run(main())