import datetime
import json
import logging

from common.utils import send_request
from django_core.config import Config

logger = logging.getLogger(__name__)

def content_retrieval(
    original_query,
    email,
    domain_url=Config.CONTENT_DOMAIN_URL,
    api_endpoint=Config.CONTENT_RETRIEVAL_ENDPOINT,
):
    """
    Retrieve content chunks relevant to the user query from content retrieval site.
    Since ServVIA now uses healthcare PDF content, this is a fallback method.
    """
    response_map = {}
    retrieval_start = None
    retrieval_end = None

    response_map.update(
        {
            "retrieval_start": retrieval_start,
            "retrieval_end": retrieval_end,
        }
    )

    retrieval_start = datetime.datetime.now()
    
    try:
        # For ServVIA healthcare, we prioritize PDF content over external API
        logger.info("🏥 ServVIA: Content retrieval called - using healthcare PDF priority")
        
        # Try external content retrieval as fallback
        content_retrieval_url = f"{domain_url}{api_endpoint}"
        retrieved_content = None
        
        try:
            response = send_request(
                content_retrieval_url,
                data={"email": email, "query": original_query},
                content_type="JSON",
                request_type="POST",
                total_retry=3,
            )
            retrieved_content = (
                json.loads(response.text)
                if response and response.status_code == 200
                else None
            )
        except Exception as api_error:
            logger.info(f"🏥 ServVIA: External API unavailable, using PDF content: {api_error}")
            # Return None to indicate PDF content should be used instead
            retrieved_content = None

    except Exception as error:
        logger.error(f"ServVIA content retrieval error: {error}", exc_info=True)
        retrieved_content = None

    retrieval_end = datetime.datetime.now()

    response_map.update(
        {
            "retrieved_chunks": retrieved_content,
            "retrieval_start": retrieval_start,
            "retrieval_end": retrieval_end,
        }
    )

    return response_map