"""
Test Query Endpoint - Mock responses for testing without Gemini API

This endpoint uses the existing mock data to demonstrate the RAG pipeline
without requiring Gemini API quota.
"""

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, status
import structlog

from src.api.gemini_schemas import QueryRequest, QueryResponse, SourceCitation

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/test/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Test query endpoint with mock responses",
    description="Returns mock responses using the existing mock data without calling Gemini API"
)
async def test_query(request: QueryRequest) -> QueryResponse:
    """
    Test query endpoint that returns mock responses.

    Uses pre-defined responses based on keywords in the question.
    """
    question = request.question.lower()

    # Mock responses based on keywords
    if "forward" in question or "kinematics" in question:
        answer = """Forward kinematics determines the position and orientation of the end-effector given joint angles. For humanoid robots, forward kinematics calculates the pose of each body part based on joint configurations. This is essential for planning movements.

The forward kinematics equation can be expressed as a series of transformation matrices."""

        citations = [
            SourceCitation(
                chunk_id=str(uuid4()),
                file_path="docs/module-2-digital-twin/chapter-1-physics-simulation.md",
                chapter="Module 2: Digital Twin",
                section="Kinematics",
                source_url="https://robotics.example.com/module-2/physics-simulation",
                similarity_score=0.95,
                rank=1
            )
        ]

    elif "inverse" in question:
        answer = """Inverse kinematics (IK) calculates joint angles required to achieve a desired end-effector pose. For humanoid robots, IK is crucial for reaching, walking, and maintaining balance. IK problems can have multiple solutions or no solution at all.

This is typically more complex than forward kinematics."""

        citations = [
            SourceCitation(
                chunk_id=str(uuid4()),
                file_path="docs/module-2-digital-twin/chapter-1-physics-simulation.md",
                chapter="Module 2: Digital Twin",
                section="Kinematics",
                source_url="https://robotics.example.com/module-2/physics-simulation",
                similarity_score=0.92,
                rank=1
            )
        ]

    elif "ros" in question:
        answer = """ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides services for hardware abstraction, low-level device control, implementation of commonly used functionality, message-passing between processes, and package management. ROS 2 uses DDS (Data Distribution Service) for communication.

In ROS 2, a node is a process that performs computation. Nodes communicate by publishing messages to topics and subscribing to topics."""

        citations = [
            SourceCitation(
                chunk_id=str(uuid4()),
                file_path="docs/module-1-ros2/chapter-1-ros2-basics.md",
                chapter="Module 1: ROS 2",
                section="ROS 2 Basics",
                source_url="https://robotics.example.com/module-1-ros2/chapter-1-ros2-basics",
                similarity_score=0.98,
                rank=1
            )
        ]

    elif "isaac" in question or "simulation" in question:
        answer = """NVIDIA Isaac Sim is a robotics simulation platform built on Omniverse. It provides photorealistic rendering, accurate physics simulation, and domain randomization for training AI models. Isaac Sim supports synthetic data generation and reinforcement learning environments.

This platform is particularly useful for testing robot behaviors in virtual environments before deploying to physical hardware."""

        citations = [
            SourceCitation(
                chunk_id=str(uuid4()),
                file_path="docs/module-3-isaac/chapter-1-isaac-sim.md",
                chapter="Module 3: NVIDIA Isaac",
                section="Isaac Sim",
                source_url="https://robotics.example.com/module-3/isaac-sim",
                similarity_score=0.94,
                rank=1
            )
        ]

    else:
        answer = """I can help you with questions about:
- ROS 2 (Robot Operating System)
- Kinematics (Forward and Inverse)
- NVIDIA Isaac Sim
- Digital Twin concepts
- Physics simulation for robotics

Try asking: "What is forward kinematics?" or "Explain ROS 2 basics" """

        citations = []

    response = QueryResponse(
        query_id=str(uuid4()),
        question=request.question,
        answer=answer,
        sources=citations,
        confidence=0.85,
        response_time_ms=50,
        timestamp=datetime.utcnow().isoformat(),
        chunks_retrieved=len(citations)
    )

    logger.info(
        "test_query_processed",
        question=request.question[:50],
        citations_count=len(citations)
    )

    return response
