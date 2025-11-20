"""
Content Retrieval Module for ServVIA
Retrieves healthcare content from multiple sources:
1. Remote FarmStack API (primary knowledge base)
2. Local healthcare content (fallback)
Applies medical profile filtering for personalized safety

Updated: 2025-11-19 - Fixed FarmStack chunk parsing
"""

import datetime
import json
import logging
import urllib3

# Disable SSL warnings (for expired certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from typing import Dict, List, Optional, Tuple

from common.utils import send_request
from django_core.config import Config

logger = logging.getLogger(__name__)

# Import local content retrieval for ServVIA
try:
    from healthcare.local_content_retriever import retrieve_from_local_content
    LOCAL_CONTENT_AVAILABLE = True
    logger.info("✅ ServVIA local content retrieval available")
except ImportError as e:
    LOCAL_CONTENT_AVAILABLE = False
    logger.warning(f"⚠️ ServVIA local content not available: {e}")

# Import medical profile filtering
try:
    from medical.remedy_filter import filter_remedies_by_medical_profile
    from medical.medical_db_operations import get_medical_profile_by_user_id
    MEDICAL_FILTERING_AVAILABLE = True
    logger.info("✅ ServVIA medical filtering available")
except ImportError as e:
    MEDICAL_FILTERING_AVAILABLE = False
    logger.warning(f"⚠️ ServVIA medical filtering not available: {e}")

# Import User model for ID lookup
try:
    from database.models import User
    USER_MODEL_AVAILABLE = True
except ImportError as e:
    USER_MODEL_AVAILABLE = False
    logger.warning(f"⚠️ User model not available: {e}")


def get_user_id_from_email(email: str) -> Optional[str]:
    """
    Get user ID from email address
    
    Args:
        email: User's email address
        
    Returns:
        User ID string or None
    """
    if not USER_MODEL_AVAILABLE:
        return None
    
    try:
        user = User.get(User.email == email)
        return str(user.id)
    except Exception as e:
        logger.warning(f"Could not find user for email {email}: {e}")
        return None


def retrieve_from_farmstack_api(
    query: str,
    email: str,
    domain_url: str = None,
    api_endpoint: str = None
) -> Optional[List[str]]:
    """
    Retrieve content from FarmStack API
    
    FarmStack Response Format:
    {
        "chunks": [
            {
                "id": "uuid",
                "score": 0.84,
                "text": "actual content..."
            }
        ]
    }
    
    Args:
        query: User's search query
        email: User's email for authentication
        domain_url: FarmStack domain URL
        api_endpoint: Content retrieval endpoint
        
    Returns:
        List of content text strings or None
    """
    domain_url = domain_url or Config.CONTENT_DOMAIN_URL
    api_endpoint = api_endpoint or Config.CONTENT_RETRIEVAL_ENDPOINT
    
    try:
        content_retrieval_url = f"{domain_url}{api_endpoint}"
        logger.info(f"🌐 Querying FarmStack API: {content_retrieval_url}")
        
        response = send_request(
            content_retrieval_url,
            data={"email": email, "query": query},
            content_type="JSON",
            request_type="POST",
            total_retry=3,
            verify=False  # Disable SSL verification for expired cert
        )
        
        if response and response.status_code == 200:
            content_data = json.loads(response.text)
            
            # FarmStack returns: {"chunks": [{"id": "...", "score": 0.84, "text": "..."}]}
            if isinstance(content_data, dict) and 'chunks' in content_data:
                chunks = content_data.get('chunks', [])
                
                if chunks and len(chunks) > 0:
                    # Extract only the text from each chunk
                    retrieved_content = []
                    total_score = 0
                    
                    for chunk in chunks:
                        if isinstance(chunk, dict):
                            text = chunk.get('text', '')
                            score = chunk.get('score', 0)
                            
                            if text:
                                retrieved_content.append(text)
                                total_score += score
                    
                    if retrieved_content:
                        avg_score = total_score / len(chunks)
                        logger.info(f"✅ Retrieved {len(retrieved_content)} chunks from FarmStack API")
                        logger.info(f"   Average relevance score: {avg_score:.3f}")
                        return retrieved_content
                    else:
                        logger.warning("⚠️ FarmStack returned chunks but no text content")
                        return None
                else:
                    logger.warning("⚠️ FarmStack API returned empty chunks array")
                    return None
            
            # Fallback: try other response structures
            elif isinstance(content_data, list):
                # Direct list of content
                retrieved_content = content_data
                logger.info(f"✅ Retrieved {len(retrieved_content)} items from FarmStack API (list format)")
                return retrieved_content
                
            elif isinstance(content_data, dict):
                # Try other common keys
                retrieved_content = (
                    content_data.get('content') or
                    content_data.get('results') or
                    content_data.get('data') or
                    ([content_data.get('text')] if content_data.get('text') else None)
                )
                
                if retrieved_content:
                    logger.info(f"✅ Retrieved content from FarmStack API (fallback parsing)")
                    return retrieved_content
                else:
                    logger.warning(f"⚠️ Unknown FarmStack response structure. Keys: {list(content_data.keys())}")
                    logger.debug(f"Response preview: {str(content_data)[:200]}")
                    return None
            else:
                logger.warning(f"⚠️ Unexpected FarmStack response type: {type(content_data)}")
                return None
                
        else:
            status = response.status_code if response else 'No response'
            logger.warning(f"⚠️ FarmStack API request failed: {status}")
            if response:
                logger.debug(f"Response body: {response.text[:200]}")
            return None
            
    except json.JSONDecodeError as json_error:
        logger.error(f"❌ Failed to parse FarmStack JSON response: {json_error}")
        if response:
            logger.debug(f"Raw response: {response.text[:500]}")
        return None
        
    except Exception as api_error:
        logger.error(f"❌ FarmStack API error: {api_error}", exc_info=True)
        return None


def apply_medical_filtering(
    content_chunks: List[str],
    user_id: str,
    email: str
) -> Tuple[List[str], List[str], str]:
    """
    Apply medical profile filtering to content
    
    Args:
        content_chunks: List of content strings
        user_id: User's ID
        email: User's email for logging
        
    Returns:
        Tuple of (filtered_content, warnings, disclaimer)
    """
    if not MEDICAL_FILTERING_AVAILABLE or not user_id:
        # No filtering available or no user ID
        return content_chunks, [], ""
    
    try:
        logger.info(f"🔍 Applying medical filtering for user: {email}")
        
        filtered_content, warnings, disclaimer = filter_remedies_by_medical_profile(
            content=content_chunks,
            user_id=user_id
        )
        
        if filtered_content:
            filtered_count = len(content_chunks) - len(filtered_content)
            if filtered_count > 0:
                logger.info(f"⚠️ Filtered out {filtered_count}/{len(content_chunks)} chunks based on medical profile")
            else:
                logger.info("✅ All content passed medical safety filter")
        else:
            logger.warning("⚠️ All content filtered out by medical profile")
        
        return filtered_content, warnings, disclaimer
        
    except Exception as filter_error:
        logger.error(f"❌ Medical filtering error: {filter_error}", exc_info=True)
        # On error, return original content (fail-safe)
        return content_chunks, [], ""


def content_retrieval(
    original_query: str,
    email: str,
    domain_url: str = None,
    api_endpoint: str = None,
    apply_medical_filter: bool = True,
    top_k: int = 5
) -> Dict:
    """
    Retrieve content chunks relevant to the user query with medical filtering.
    
    Retrieval Priority:
    1. Remote FarmStack API (primary knowledge base)
    2. Local healthcare content (fallback)
    
    Then applies medical profile filtering for personalized safety.
    
    Args:
        original_query: User's search query
        email: User's email address
        domain_url: Override FarmStack domain URL (optional)
        api_endpoint: Override API endpoint (optional)
        apply_medical_filter: Whether to apply medical profile filtering
        top_k: Number of top results to retrieve
        
    Returns:
        Dict containing:
            - retrieved_chunks: List of content chunks (filtered if applicable)
            - retrieval_start: Start timestamp
            - retrieval_end: End timestamp
            - source: Content source ("farmstack" or "local")
            - medical_filtered: Whether medical filtering was applied
            - medical_warnings: List of filtering warnings
            - medical_disclaimer: Personalized health disclaimer
            - original_chunk_count: Number of chunks before filtering
            - filtered_chunk_count: Number of chunks after filtering
    """
    response_map = {}
    retrieval_start = datetime.datetime.now()
    retrieved_content = None
    content_source = None
    
    # Get user ID for medical filtering
    user_id = None
    if apply_medical_filter:
        user_id = get_user_id_from_email(email)
        if user_id:
            logger.info(f"👤 User ID found for medical filtering: {user_id}")
    
    # ============================================================
    # PRIORITY 1: Try FarmStack API (PRIMARY SOURCE)
    # ============================================================
    logger.info("🌐 Attempting FarmStack API retrieval (primary source)")
    retrieved_content = retrieve_from_farmstack_api(
        query=original_query,
        email=email,
        domain_url=domain_url,
        api_endpoint=api_endpoint
    )
    
    if retrieved_content:
        content_source = "farmstack"
        logger.info(f"✅ Using FarmStack API content ({len(retrieved_content)} chunks)")
    
    # ============================================================
    # PRIORITY 2: Fallback to local healthcare content
    # ============================================================
    if not retrieved_content and LOCAL_CONTENT_AVAILABLE:
        logger.info("🏥 Falling back to local healthcare content")
        try:
            retrieved_content = retrieve_from_local_content(original_query, top_k=top_k)
            
            if retrieved_content:
                content_source = "local"
                logger.info(f"✅ Using local healthcare content ({len(retrieved_content)} chunks)")
            else:
                logger.warning("⚠️ No local content found")
                
        except Exception as local_error:
            logger.error(f"❌ Local retrieval failed: {local_error}", exc_info=True)
            retrieved_content = None
    
    # ============================================================
    # STEP 3: Apply medical profile filtering
    # ============================================================
    medical_warnings = []
    medical_disclaimer = ""
    original_chunk_count = len(retrieved_content) if retrieved_content else 0
    medical_filtered = False
    
    if retrieved_content and apply_medical_filter and user_id:
        logger.info("🔍 Applying medical profile filtering")
        
        filtered_content, medical_warnings, medical_disclaimer = apply_medical_filtering(
            content_chunks=retrieved_content,
            user_id=user_id,
            email=email
        )
        
        if filtered_content is not None:
            retrieved_content = filtered_content
            medical_filtered = True
            logger.info(f"✅ Medical filtering complete: {len(filtered_content)}/{original_chunk_count} chunks retained")
        else:
            logger.warning("⚠️ Medical filtering returned no safe content")
            retrieved_content = []
    
    retrieval_end = datetime.datetime.now()
    retrieval_duration = (retrieval_end - retrieval_start).total_seconds()
    
    # ============================================================
    # Build response map
    # ============================================================
    response_map.update({
        "retrieved_chunks": retrieved_content,
        "retrieval_start": retrieval_start,
        "retrieval_end": retrieval_end,
        "retrieval_duration_seconds": retrieval_duration,
        "source": content_source or "none",
        "medical_filtered": medical_filtered,
        "medical_warnings": medical_warnings,
        "medical_disclaimer": medical_disclaimer,
        "original_chunk_count": original_chunk_count,
        "filtered_chunk_count": len(retrieved_content) if retrieved_content else 0,
        "user_id": user_id,
        "query": original_query,
        "success": retrieved_content is not None and len(retrieved_content) > 0
    })
    
    # Log summary
    if retrieved_content:
        logger.info(
            f"✅ Content retrieval complete: "
            f"source={content_source}, "
            f"chunks={len(retrieved_content)}, "
            f"filtered={medical_filtered}, "
            f"duration={retrieval_duration:.2f}s"
        )
    else:
        logger.warning(f"⚠️ No content retrieved for query: {original_query}")

    return response_map


def retrieve_content_from_api(
    query: str,
    user_email: str,
    apply_medical_filter: bool = True
) -> Optional[List[str]]:
    """
    Simplified wrapper for direct content retrieval with medical filtering
    
    Args:
        query: User's search query
        user_email: User's email address
        apply_medical_filter: Whether to apply medical filtering
        
    Returns:
        List of content chunks or None
    """
    response = content_retrieval(
        original_query=query,
        email=user_email,
        apply_medical_filter=apply_medical_filter
    )
    
    return response.get("retrieved_chunks")


# Backwards compatibility aliases
def get_content_chunks(query: str, email: str) -> Optional[List[str]]:
    """Backwards compatible alias"""
    return retrieve_content_from_api(query, email)