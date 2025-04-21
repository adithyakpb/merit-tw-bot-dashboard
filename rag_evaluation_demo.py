#!/usr/bin/env python3
"""
Merit RAG Evaluation Demo

This script demonstrates how to use Merit to evaluate a RAG (Retrieval-Augmented Generation) system
using a previously generated test set.

The demo:
1. Loads a test set from a file
2. Creates a simple RAG function
3. Evaluates the RAG function using the loaded test set
4. Generates a report of the evaluation results
"""

import os
from dotenv import load_dotenv
from merit.api.gemini_client import GeminiClient
from merit.knowledge import KnowledgeBase
from merit.core.models import TestSet, Response
from merit.evaluation import evaluate_rag

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

def simple_rag_function(query, knowledge_base, client):
    """
    A simple RAG function that retrieves relevant documents and generates a response.
    
    Args:
        query: The user query (can be a string or an Input object)
        knowledge_base: The knowledge base to search
        client: The client for generating responses
        
    Returns:
        Response: A Response object containing the generated text and retrieved documents
    """
    # Extract the query content if it's an Input object
    if hasattr(query, 'content'):
        query_text = query.content
    else:
        query_text = str(query)
    
    # Search for relevant documents
    search_results = knowledge_base.search(query_text, k=2)
    
    # Extract the documents
    documents = [doc for doc, _ in search_results]
    
    # Create a context from the documents
    context = "\n\n".join([doc.content for doc in documents])
    
    # Generate a response using the context
    prompt = f"""
    You are a helpful assistant that answers questions based on the provided context.
    
    Context:
    {context}
    
    Question: {query_text}
    
    Answer the question based on the context provided. If the context doesn't contain the information needed to answer the question, say "I don't have enough information to answer that question."
    """
    
    response_text = client.generate_text(prompt)
    
    # Create a Response object
    response = Response(content=response_text, documents=documents)
    
    return response

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

    # Check if the test set file exists
    test_set_file = "sample_testset.json"
    if not os.path.exists(test_set_file):
        print(f"Error: Test set file '{test_set_file}' not found.")
        print("Please run testset_generation_demo.py first to generate a test set.")
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

    print(f"Loading test set from {test_set_file}...")
    # Load the test set from file
    test_set = TestSet.load(test_set_file)
    print(f"Loaded test set with {len(test_set.inputs)} items")

    print("\nEvaluating RAG function...")
    # Create a function that wraps our simple_rag_function to match the expected interface
    def rag_answer_fn(query):
        return simple_rag_function(query, knowledge_base, client)

    # Create metric instances
    from merit.metrics.rag import CorrectnessMetric, FaithfulnessMetric, RelevanceMetric
    
    metrics = [
        CorrectnessMetric(llm_client=client, agent_description="A chatbot that answers questions about programming and AI"),
        FaithfulnessMetric(llm_client=client),
        RelevanceMetric(llm_client=client)
    ]
    
    # Evaluate the RAG function
    evaluation_report = evaluate_rag(
        answer_fn=rag_answer_fn,
        testset=test_set,
        knowledge_base=knowledge_base,
        llm_client=client,
        agent_description="A chatbot that answers questions about programming and AI",
        metrics=metrics  # Using pre-initialized metric instances
    )

    # Print evaluation summary
    print("\nEvaluation Results:")
    for metric_name in evaluation_report.summary:
        print(f"{metric_name}: {evaluation_report.summary[metric_name]}")

    # Save the evaluation report
    report_file = "evaluation_report.json"
    success = evaluation_report.save(report_file, generate_html=True)
    if success:
        print(f"\nEvaluation report saved to {report_file}")
        print(f"HTML report also generated at {report_file.replace('.json', '.html')}")
    else:
        print("\nFailed to save evaluation report")

    # Print some example results
    print("\nExample evaluation results:")
    for i, result in enumerate(evaluation_report.results[:2]):  # Show first 2 results
        print(f"\nResult {i+1}:")
        print(f"Input: {result.input.content}")
        print(f"Response: {result.response.content[:100]}...")
        print(f"Reference: {result.reference.content[:100]}...")
        print("Metrics:")
        for metric in result.metrics:
            for metric_name, metric_value in metric.items():
                if isinstance(metric_value, (int, float)):
                    print(f"  {metric_name}: {metric_value}")

if __name__ == "__main__":
    main()
