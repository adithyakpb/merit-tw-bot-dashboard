#!/usr/bin/env python3
"""
Merit Test Set Generation Demo

This script demonstrates how to use Merit to generate a test set for evaluating
RAG (Retrieval-Augmented Generation) systems.

The demo:
1. Creates a sample knowledge base from data
2. Generates a test set from the knowledge base
3. Saves the test set to a file
"""

import os
import pandas as pd
from dotenv import load_dotenv
from merit.api.gemini_client import GeminiClient
from merit.knowledge import KnowledgeBase
from merit.testset_generation import TestSetGenerator

# Load environment variables from .env file (if it exists)
load_dotenv()

# Set up Google API key
# Replace with your actual API key or set it as an environment variable
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "AIzaSyBlI7KwsmbYklgXcMuAdhjx7MHb6kncTSE")

# Sample data for the knowledge base
# In a real application, this would typically come from files or a database
SAMPLE_DATA = [
    {
        "content": "Python is a high-level, interpreted programming language known for its readability and simplicity. It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
        "metadata": {"topic": "programming", "language": "en"}
    },
    {
        "content": "JavaScript is a programming language that is one of the core technologies of the World Wide Web. It enables interactive web pages and is an essential part of web applications. JavaScript was initially created to 'make web pages alive'.",
        "metadata": {"topic": "programming", "language": "en"}
    },
    {
        "content": "Machine Learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.",
        "metadata": {"topic": "ai", "language": "en"}
    },
    {
        "content": "Deep Learning is part of a broader family of machine learning methods based on artificial neural networks. Learning can be supervised, semi-supervised or unsupervised. Deep learning architectures such as deep neural networks have been applied to fields including computer vision, speech recognition, and natural language processing.",
        "metadata": {"topic": "ai", "language": "en"}
    },
    {
        "content": "Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language. It involves programming computers to process and analyze large amounts of natural language data.",
        "metadata": {"topic": "ai", "language": "en"}
    }
]

def main():
    """Main function to run the demo."""
    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set your Google API key using:")
        print("  export GOOGLE_API_KEY=your-api-key")
        print("Or create a .env file with GOOGLE_API_KEY=your-api-key")
        return

    print("Setting up Gemini client...")
    # Create a Gemini client for embeddings and text generation
    client = GeminiClient(
        api_key=api_key,
        generation_model="gemini-1.5-pro",  # You can change this to a different model if needed
        embedding_model="embedding-001"  # You can change this to a different embedding model if needed
    )

    print("Creating knowledge base from sample data...")
    # Create a knowledge base from the sample data
    knowledge_base = KnowledgeBase(
        data=SAMPLE_DATA,
        client=client
    )
    print(f"Created knowledge base with {len(knowledge_base.documents)} documents")

    print("Generating test set...")
    # Create a test set generator
    generator = TestSetGenerator(
        knowledge_base=knowledge_base,
        language="en",
        agent_description="A chatbot that answers questions about programming and AI"
    )

    # Generate a test set with 10 items
    # In a real application, you might want to generate more items
    test_set = generator.generate(
        num_items=10,
        distribution_strategy="representative"  # This ensures the test set represents the knowledge base structure
    )
    print(f"Generated test set with {len(test_set.inputs)} items")

    # Print some example test items
    print("\nExample test items:")
    for i, item in enumerate(test_set.inputs[:3]):  # Show first 3 items
        print(f"\nItem {i+1}:")
        print(f"Input: {item.input.content}")
        print(f"Reference Answer: {item.reference_answer.content[:100]}...")
        print(f"Document: {item.document.content[:50]}...")

    # Save the test set to a file
    output_file = "sample_testset.json"
    success = test_set.save(output_file)
    if success:
        print(f"\nTest set saved to {output_file}")
    else:
        print("\nFailed to save test set")

if __name__ == "__main__":
    main()
