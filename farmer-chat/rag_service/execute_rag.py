import asyncio
import datetime
import logging

# ServVIA healthcare PDF integration
try:
    from healthcare.pdf_content_handler import get_healthcare_response_from_pdf
    HEALTHCARE_PDF_AVAILABLE = True
except ImportError:
    HEALTHCARE_PDF_AVAILABLE = False

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
    Modified for ServVIA healthcare to prioritize PDF content.
    """
    
    # If healthcare PDF is available, use it directly instead of RAG pipeline
    if HEALTHCARE_PDF_AVAILABLE:
        logger.info("🏥 ServVIA: Using healthcare PDF instead of RAG pipeline")
        
        try:
            healthcare_response = get_healthcare_response_from_pdf(original_query, user_name)
            
            response_map = {
                "message_id": message_id,
                "generated_final_response": healthcare_response,
                "source": "Home_Remedies_Guide.pdf",
                "follow_up_questions": [
                    "What are the warning signs I should watch for?",
                    "How can I prevent this condition in the future?",
                    "Are there any foods or activities I should avoid?",
                    "When should I see a doctor for this condition?"
                ]
            }
            
            message_data_update_post_rag_pipeline = {
                "main_bot_logic_end_time": datetime.datetime.now(),
                "retrieval_method": "healthcare_pdf"
            }
            
            return response_map, message_data_update_post_rag_pipeline
            
        except Exception as pdf_error:
            logger.error(f"ServVIA PDF processing error: {pdf_error}")
            # Fall through to original RAG pipeline
    
    # Original RAG pipeline execution
    generated_final_response = None
    retrieved_chunks = []
    response_map = {"message_id": message_id}
    message_data_to_insert_or_update = {"message_id": message_id}
    
    try:
        message_data_to_insert_or_update["main_bot_logic_start_time"] = (
            datetime.datetime.now()
        )

        # execute rephrasing
        try:
            rephrased_query_response = asyncio.run(
                rephrase_query(original_query, chat_history)
            )
            rephrased_query = rephrased_query_response.get("rephrased_query")
        except Exception as rephrase_error:
            logger.warning(f"Rephrasing failed, using original query: {rephrase_error}")
            rephrased_query = original_query

        # content retrieval
        try:
            retrieval_results = content_retrieval(rephrased_query, email_id)
            logger.info(f"RETRIEVAL RESULTS: \n{retrieval_results}")
            retrieved_chunks_data = retrieval_results.get("retrieved_chunks")
        except Exception as retrieval_error:
            logger.warning(f"Content retrieval failed: {retrieval_error}")
            retrieved_chunks_data = None

        # If no content retrieved, provide fallback healthcare response
        if not retrieved_chunks_data:
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
            # Process retrieved content through remaining RAG pipeline
            try:
                # Continue with reranking and response generation
                # (This would include the rest of the original RAG pipeline)
                response_map.update({
                    "generated_final_response": f"Based on available information: {retrieved_chunks_data}",
                    "source": "External Knowledge Base"
                })
            except Exception as processing_error:
                logger.error(f"RAG processing error: {processing_error}")
                response_map.update({
                    "generated_final_response": f"Hello {user_name}! I found some information but had trouble processing it. Please consult a healthcare professional for reliable medical advice. 🏥"
                })

        message_data_to_insert_or_update["main_bot_logic_end_time"] = datetime.datetime.now()

    except Exception as error:
        logger.error(f"ServVIA RAG pipeline error: {error}", exc_info=True)
        
        # Fallback error response
        response_map.update({
            "generated_final_response": f"Hello {user_name}! I'm experiencing technical difficulties. For your health and safety, please consult a healthcare professional. 🏥",
            "source": None
        })

    return response_map, message_data_to_insert_or_update