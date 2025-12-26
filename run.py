import asyncio
import random
import inngest
from dotenv import load_dotenv

load_dotenv()

# Random topics
topics = [
    "AI",
    "Climate Change",
    "Space",
    "Crypto",
    "Energy",
    "ML",
    "Quantum",
    "Biotech",
    "Security",
    "EVs",
    "VR",
    "Blockchain",
    "Robotics",
    "5G",
    "IoT",
    "Drones",
    "Nanotech",
    "Health",
    "Cities",
    "AR",
    "Cloud",
    "Agriculture",
    "Ocean",
    "Wildlife",
    "Fintech",
    "Remote Work",
    "EdTech",
    "Food Tech",
    "Wearables",
    "3D Print",
    "Satellites",
    "Green Building",
    "Water",
    "Waste",
    "Carbon",
    "Nuclear",
    "Hydrogen",
    "Batteries",
    "Semiconductors",
    "Social Media",
    "Gaming",
    "Streaming",
    "Digital Art",
    "NFTs",
    "Metaverse",
    "Privacy",
]


async def send_request(client, i):
    topic = random.choice(topics)

    event = inngest.Event(
        name="newsletter/generate", data={"topic": topic, "max_articles": 3}
    )

    try:
        result = await client.send(event)
        print(f"{i}: {topic} -> SUCCESS")
    except Exception as e:
        print(f"{i}: {topic} -> ERROR: {e}")


async def main():
    client = inngest.Inngest(
        app_id="newsletter_client",
        is_production=False,
    )

    tasks = [send_request(client, i) for i in range(1, 101)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())