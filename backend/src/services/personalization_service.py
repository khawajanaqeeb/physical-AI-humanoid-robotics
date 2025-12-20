"""
Personalization service for generating context-aware system prompts based on user profiles.
"""
from typing import Optional
from src.users.models import UserProfile, SoftwareExperience, HardwareExperience


class PersonalizationService:
    """
    Service for generating personalized system prompts based on user experience levels.

    Creates different system prompts that adjust the complexity and depth of explanations
    based on user's software and hardware experience levels.
    """

    def __init__(self):
        """Initialize personalization service."""
        pass

    def generate_system_prompt(self, profile: UserProfile) -> str:
        """
        Generate a personalized system prompt based on user profile.

        Args:
            profile: User's profile with experience levels and interests

        Returns:
            Personalized system prompt string
        """
        software_exp = profile.software_experience
        hardware_exp = profile.hardware_experience
        interests = profile.interests

        # Base prompt
        base_prompt = (
            "You are an AI assistant for a university-level textbook on Physical AI and Humanoid Robotics. "
            "You must answer questions using ONLY the provided textbook context. "
            "Do not use external knowledge. "
            "Do not make assumptions. "
            "If the answer is not present in the context, you must respond EXACTLY with: "
            "'I could not find this information in the textbook.' "
        )

        # Adjust tone and complexity based on experience levels
        if software_exp == SoftwareExperience.BEGINNER or hardware_exp == HardwareExperience.NONE:
            # Beginner-friendly prompt with simpler explanations
            experience_prompt = (
                "Provide clear, beginner-friendly explanations. "
                "Break down complex concepts into simple, digestible parts. "
                "Use analogies and examples that are easy to understand. "
                "Explain technical terms when first introduced. "
                "Focus on the fundamental concepts and how they work together. "
                "Assume the user is learning these concepts for the first time. "
            )
        elif software_exp == SoftwareExperience.INTERMEDIATE or hardware_exp == HardwareExperience.BASIC:
            # Intermediate-level prompt with balanced explanations
            experience_prompt = (
                "Provide explanations that are clear but assume some foundational knowledge. "
                "Include technical details but explain them in context. "
                "Balance between depth and accessibility. "
                "Use appropriate technical terminology while remaining understandable. "
                "Assume the user has some experience with robotics or AI concepts. "
            )
        else:  # ADVANCED for either software or hardware
            # Advanced prompt with technical depth
            experience_prompt = (
                "Provide detailed, technical explanations. "
                "Include advanced concepts, implementation details, and nuanced discussions. "
                "Use technical terminology appropriately. "
                "Assume the user has significant experience with robotics, AI, or related fields. "
                "Include mathematical concepts, algorithmic details, and implementation considerations where relevant. "
            )

        # Add interest-based context if available
        interest_prompt = ""
        if interests:
            interest_prompt = (
                f"The user has expressed interest in: {', '.join(interests)}. "
                "When relevant to the question, connect the answer to these interests. "
            )

        # Combine all prompts
        full_prompt = f"{base_prompt}\n\n{experience_prompt}\n\n{interest_prompt}\n\n"

        # Final instructions
        full_prompt += (
            "Your tone must be factual, concise, and appropriate for the user's experience level. "
            "Do not mention that you are an AI model, the retrieval process, or any internal systems. "
            "Answer ONLY using the provided documents. "
            "Do not add information not present in the documents. "
            "If multiple documents are relevant, synthesize them into one coherent answer. "
            "If the documents do not contain the answer, respond with: 'I could not find this information in the textbook.' "
            "Use an academic, textbook-style tone appropriate for the user's experience level."
        )

        return full_prompt


# Global service instance
personalization_service = PersonalizationService()