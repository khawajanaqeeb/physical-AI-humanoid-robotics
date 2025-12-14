#!/usr/bin/env python3
"""Create mock sample data for testing the Gemini RAG system."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
import random

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncpg
from qdrant_client.models import PointStruct
from src.clients.qdrant_client import get_qdrant_client
from src.config.settings import get_settings

settings = get_settings()

SAMPLE_CHUNKS = [
    {
        "file_path": "docs/module-1-ros2/chapter-1-ros2-basics.md",
        "chapter": "Module 1: ROS 2",
        "section": "ROS 2 Basics",
        "heading_path": ["ROS 2 Basics", "Introduction"],
        "source_url": "https://robotics.example.com/module-1-ros2/chapter-1-ros2-basics",
        "chunk_text": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides services for hardware abstraction, low-level device control, implementation of commonly used functionality, message-passing between processes, and package management. ROS 2 uses DDS (Data Distribution Service) for communication."
    },
    {
        "file_path": "docs/module-1-ros2/chapter-1-ros2-basics.md",
        "chapter": "Module 1: ROS 2",
        "section": "ROS 2 Basics",
        "heading_path": ["ROS 2 Basics", "Nodes and Topics"],
        "source_url": "https://robotics.example.com/module-1-ros2/chapter-1-ros2-basics",
        "chunk_text": "In ROS 2, a node is a process that performs computation. Nodes communicate by publishing messages to topics and subscribing to topics. A topic is a named bus for message exchange. QoS (Quality of Service) settings control reliability and performance of message delivery."
    },
    {
        "file_path": "docs/module-2-digital-twin/chapter-1-physics-simulation.md",
        "chapter": "Module 2: Digital Twin",
        "section": "Kinematics",
        "heading_path": ["Physics Simulation", "Forward Kinematics"],
        "source_url": "https://robotics.example.com/module-2/physics-simulation",
        "chunk_text": "Forward kinematics determines the position and orientation of the end-effector given joint angles. For humanoid robots, forward kinematics calculates the pose of each body part based on joint configurations. This is essential for planning movements."
    },
    {
        "file_path": "docs/module-2-digital-twin/chapter-1-physics-simulation.md",
        "chapter": "Module 2: Digital Twin",
        "section": "Kinematics",
        "heading_path": ["Physics Simulation", "Inverse Kinematics"],
        "source_url": "https://robotics.example.com/module-2/physics-simulation",
        "chunk_text": "Inverse kinematics (IK) calculates joint angles required to achieve a desired end-effector pose. For humanoid robots, IK is crucial for reaching, walking, and maintaining balance. IK problems can have multiple solutions or no solution."
    },
    {
        "file_path": "docs/module-3-isaac/chapter-1-isaac-sim.md",
        "chapter": "Module 3: NVIDIA Isaac",
        "section": "Isaac Sim",
        "heading_path": ["Isaac Sim", "Overview"],
        "source_url": "https://robotics.example.com/module-3/isaac-sim",
        "chunk_text": "NVIDIA Isaac Sim is a robotics simulation platform built on Omniverse. It provides photorealistic rendering, accurate physics simulation, and domain randomization for training AI models. Isaac Sim supports synthetic data generation and reinforcement learning environments."
    }
]

def generate_mock_embedding(dimension=768):
    """Generate normalized random embedding vector."""
    vector = [random.uniform(-1, 1) for _ in range(dimension)]
    magnitude = sum(x**2 for x in vector) ** 0.5
    return [x / magnitude for x in vector]

async def create_mock_data():
    # Fix database URL for asyncpg
    db_url = settings.database_url.replace('+asyncpg', '')
    
    print("\n" + "="*60)
    print("CREATING MOCK DATA FOR TESTING")
    print("="*60 + "\n")
    
    db_conn = await asyncpg.connect(db_url)
    qdrant_client = get_qdrant_client()
    
    inserted = 0
    
    try:
        for idx, chunk_data in enumerate(SAMPLE_CHUNKS):
            chunk_id = uuid4()
            qdrant_point_id = uuid4()
            embedding = generate_mock_embedding(768)
            
            await db_conn.execute("""
                INSERT INTO chunks (
                    id, chunk_text, file_path, chapter, section,
                    heading_path, source_url, chunk_index, total_chunks,
                    qdrant_point_id, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
            """, chunk_id, chunk_data["chunk_text"], chunk_data["file_path"],
                chunk_data["chapter"], chunk_data["section"], 
                chunk_data["heading_path"], chunk_data["source_url"],
                idx, len(SAMPLE_CHUNKS), qdrant_point_id)
            
            point = PointStruct(
                id=str(qdrant_point_id),
                vector=embedding,
                payload={
                    "chunk_id": str(chunk_id),
                    "chunk_text": chunk_data["chunk_text"],
                    "file_path": chunk_data["file_path"],
                    "chapter": chunk_data["chapter"],
                    "section": chunk_data["section"],
                    "heading_path": chunk_data["heading_path"],
                    "source_url": chunk_data["source_url"],
                    "chunk_index": idx,
                    "total_chunks": len(SAMPLE_CHUNKS)
                }
            )
            
            await qdrant_client.upsert(
                collection_name=settings.qdrant_collection_name,
                points=[point]
            )
            
            inserted += 1
            print(f"  [{inserted}/{len(SAMPLE_CHUNKS)}] {chunk_data['chapter']}: {chunk_data['section']}")
        
        db_count = await db_conn.fetchval("SELECT COUNT(*) FROM chunks")
        collection_info = await qdrant_client.get_collection(settings.qdrant_collection_name)

        print("\n" + "="*60)
        print("MOCK DATA CREATED SUCCESSFULLY")
        print("="*60)
        print(f"\nDatabase: {db_count} chunks")
        print(f"Qdrant: {collection_info.points_count} points")
        print(f"\nTopics included:")
        print(f"  - ROS 2 Basics (nodes, topics)")
        print(f"  - Kinematics (forward, inverse)")
        print(f"  - Isaac Sim (simulation)")
        print("\n" + "="*60 + "\n")
        
    finally:
        await db_conn.close()
        await qdrant_client.close()

if __name__ == "__main__":
    asyncio.run(create_mock_data())
