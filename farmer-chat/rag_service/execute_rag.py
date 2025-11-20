import asyncio
import datetime
import logging

from generation.generate_response import generate_query_response
from rag_service.utils import (
    fetch_source_from_reranked_chunks,
    post_process_rag_pipeline,
)
from rephrasing.rephrase import rephrase_query
from reranking.rerank import rerank_query
from reranking.utils import prepare_reranked_chunks_to_insert
from retrieval.content_retrieval import content_retrieval
from retrieval.utils import prepare_retrieved_chunks_to_insert

logger = logging.getLogger(__name__)


def execute_rag_pipeline(
    original_query,
    input_language_detected,
    email_id,
    user_name=None,
    message_id=None,
    chat_history=None,
):
    """
    Execute RAG pipeline to process rephrasing, reranking and generating response
    for the given query based on the available content.
    Enhanced for ServVIA healthcare with local content retrieval.
    """
    
    # Execute full RAG pipeline (no bypasses)
    logger.info("🧠 Executing full RAG pipeline with content retrieval")
    
    generated_final_response = None
    retrieved_chunks = []
    response_map = {"message_id": message_id}
    message_data_to_insert_or_update = {"message_id": message_id}
    
    try:
        message_data_to_insert_or_update["main_bot_logic_start_time"] = (
            datetime.datetime.now()
        )

        # Step 1: Execute rephrasing
        try:
            logger.info(f"🔄 Rephrasing query: '{original_query}'")
            rephrased_query_response = asyncio.run(
                rephrase_query(original_query, chat_history)
            )
            rephrased_query = rephrased_query_response.get("rephrased_query")
            logger.info(f"✅ Rephrased to: '{rephrased_query}'")
        except Exception as rephrase_error:
            logger.warning(f"⚠️ Rephrasing failed, using original query: {rephrase_error}")
            rephrased_query = original_query
            rephrased_query_response = {"rephrased_query": original_query}

        # Step 2: Content retrieval (will use local healthcare content if available)
        try:
            logger.info(f"🔍 Retrieving content for: '{rephrased_query}'")
            retrieval_results = content_retrieval(rephrased_query, email_id)
            retrieved_chunks_data = retrieval_results.get("retrieved_chunks")
            
            if retrieved_chunks_data:
                logger.info(f"✅ Retrieved {len(retrieved_chunks_data)} chunks")
            else:
                logger.warning("⚠️ No content retrieved")
                
        except Exception as retrieval_error:
            logger.error(f"❌ Content retrieval failed: {retrieval_error}")
            retrieved_chunks_data = None

        # Step 3: Process retrieved content
        if not retrieved_chunks_data:
            # Fallback healthcare response when no content retrieved
            logger.warning("⚠️ No content available, using fallback response")
            
            fallback_response = f"""Hello {user_name}! 👋 

I'm having trouble accessing my knowledge base right now, but I'm here to help with your health concerns.

**For your query about: "{original_query}"**

**General Health Recommendations:**
• Stay hydrated by drinking plenty of water 💧
• Get adequate rest and sleep 😴  
• Eat nutritious, balanced meals 🥗
• Consider consulting a healthcare professional 👩‍⚕️

**⚠️ Important Medical Disclaimer:**
These are general wellness suggestions. For specific medical concerns, please consult with a qualified healthcare professional.

**🏥 When to Seek Medical Help:**
• If symptoms persist or worsen
• If you have severe or concerning symptoms  
• If you have underlying health conditions
• When in doubt about your health

**Emergency:** If this is a medical emergency, please call emergency services immediately."""

            response_map.update({
                "generated_final_response": fallback_response,
                "source": None,
                "follow_up_questions": [
                    "Should I consult a doctor for this?",
                    "What are general wellness tips?", 
                    "How do I know if this is serious?"
                ]
            })
            
        else:
            # Step 4: Prepare retrieved chunks for reranking
            try:
                logger.info("📊 Preparing chunks for reranking")
                retrieved_chunks = prepare_retrieved_chunks_to_insert(
                    retrieved_chunks_data, message_id
                )
            except Exception as prep_error:
                logger.warning(f"⚠️ Chunk preparation failed: {prep_error}")
                retrieved_chunks = retrieved_chunks_data

            # Step 5: Rerank the retrieved chunks
            try:
                logger.info("🎯 Reranking retrieved chunks")
                reranked_query_response = asyncio.run(
                    rerank_query(rephrased_query, retrieved_chunks_data)
                )
                reranked_chunks = reranked_query_response.get("reranked_chunks", {})
                
                if reranked_chunks:
                    logger.info(f"✅ Reranked {len(reranked_chunks)} chunks")
                else:
                    logger.warning("⚠️ Reranking returned no results, using original chunks")
                    reranked_chunks = retrieved_chunks_data
                    
            except Exception as rerank_error:
                logger.warning(f"⚠️ Reranking failed, using original chunks: {rerank_error}")
                reranked_chunks = retrieved_chunks_data
                reranked_query_response = {"reranked_chunks": retrieved_chunks_data}

            # Step 6: Prepare reranked chunks
            try:
                reranked_chunk_data = prepare_reranked_chunks_to_insert(
                    reranked_chunks, message_id
                )
            except Exception as prep_error:
                logger.warning(f"⚠️ Reranked chunk preparation failed: {prep_error}")
                reranked_chunk_data = []

            # Step 7: Format context for LLM generation
            try:
                logger.info("📝 Formatting context for LLM generation")
                
                # Extract text from chunks
                if isinstance(reranked_chunks, dict):
                    context_chunks = "\n\n".join([
                        chunk.get("chunk", str(chunk))
                        for chunk in reranked_chunks.values()
                    ])
                elif isinstance(reranked_chunks, list):
                    context_chunks = "\n\n".join([
                        chunk.get("chunk", str(chunk)) if isinstance(chunk, dict) else str(chunk)
                        for chunk in reranked_chunks
                    ])
                else:
                    context_chunks = str(reranked_chunks)
                
                logger.info(f"✅ Context prepared: {len(context_chunks)} characters")
                
            except Exception as context_error:
                logger.error(f"❌ Context formatting failed: {context_error}")
                context_chunks = "Healthcare information retrieved but could not be formatted properly."

            # Step 8: Generate final response using LLM
            try:
                logger.info("🤖 Generating response with LLM")
                generated_response = asyncio.run(
                    generate_query_response(
                        original_query, user_name, context_chunks, rephrased_query
                    )
                )
                generated_final_response = generated_response.get("response")
                
                if generated_final_response:
                    logger.info(f"✅ LLM response generated: {len(generated_final_response)} characters")
                else:
                    logger.warning("⚠️ LLM returned empty response")
                    generated_final_response = f"Hello {user_name}! I found relevant information but had trouble generating a response. Please consult a healthcare professional. 🏥"
                    
            except Exception as generation_error:
                logger.error(f"❌ Response generation failed: {generation_error}")
                generated_final_response = f"Hello {user_name}! I found some information but had trouble processing it. Please consult a healthcare professional for reliable medical advice. 🏥"

            # Step 9: Fetch source from reranked chunks
            try:
                content_source = fetch_source_from_reranked_chunks(reranked_chunks)
            except Exception as source_error:
                logger.warning(f"⚠️ Source extraction failed: {source_error}")
                content_source = "Healthcare Content"

            # Step 10: Update response map
            response_map.update({
                "generated_final_response": generated_final_response,
                "source": content_source,
                "follow_up_questions": [
                    "What are the warning signs I should watch for?",
                    "How can I prevent this condition in the future?",
                    "Are there any foods or activities I should avoid?",
                    "When should I see a doctor for this condition?"
                ]
            })

            # Step 11: Post-process RAG pipeline data
            try:
                post_process_rag_pipeline(
                    message_id,
                    rephrased_query_response,
                    retrieved_chunks,
                    reranked_chunk_data,
                    reranked_query_response,
                    generated_response,
                )
            except Exception as post_error:
                logger.warning(f"⚠️ Post-processing failed: {post_error}")

        # Mark end time
        message_data_to_insert_or_update["main_bot_logic_end_time"] = datetime.datetime.now()
        
        logger.info("✅ RAG pipeline execution completed successfully")

    except Exception as error:
        logger.error(f"❌ ServVIA RAG pipeline error: {error}", exc_info=True)
        
        # Fallback error response
        user_name = user_name if user_name else "there"
        response_map.update({
            "generated_final_response": f"Hello {user_name}! I'm experiencing technical difficulties. For your health and safety, please consult a healthcare professional. 🏥",
            "source": None,
            "follow_up_questions": [
                "Contact your healthcare provider",
                "Visit urgent care if symptoms persist",
                "Call emergency services if severe"
            ]
        })
        
        message_data_to_insert_or_update["main_bot_logic_end_time"] = datetime.datetime.now()

    return response_map, message_data_to_insert_or_update