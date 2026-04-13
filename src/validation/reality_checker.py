"""
reality_checker.py

REALITY VALIDATION SYSTEM
=========================

Cross-validates model predictions and data values against real-world facts
using AI (LLM) to verify accuracy.

Checks:
- Inflation rates for specific years
- GDP growth rates
- Unemployment rates
- Economic events
- Market conditions

Author: System Validation
Date: 2026-04-13
Version: 1.0.0
"""

import os
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class RealityCheckResult:
    """Result of reality check validation"""
    metric: str
    year: int
    model_value: float
    ai_verified_value: Optional[float]
    ai_response: str
    is_accurate: bool
    deviation: Optional[float]
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    notes: str


class RealityChecker:
    """Validates data against real-world facts using AI"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    def check_inflation_rate(self, year: int, model_value: float) -> RealityCheckResult:
        """
        Verify inflation rate for a specific year against real data.
        
        Args:
            year: Year to check
            model_value: Model's predicted/stored inflation rate
            
        Returns:
            RealityCheckResult with verification
        """
        prompt = f"""You are a fact-checker for economic data.

Question: What was India's inflation rate (CPI) in {year}?

Provide:
1. The actual inflation rate (%)
2. The source (RBI, World Bank, etc.)
3. Any important context (e.g., COVID impact, policy changes)

Format your response as:
INFLATION_RATE: [number]%
SOURCE: [source name]
CONTEXT: [brief context]

Be precise and factual. If you're not certain, say so."""

        ai_response = self._query_ai(prompt)
        
        # Parse AI response
        ai_value, confidence, notes = self._parse_inflation_response(ai_response)
        
        # Calculate deviation
        if ai_value is not None:
            deviation = abs(model_value - ai_value)
            is_accurate = deviation <= 1.0  # Within 1 percentage point
        else:
            deviation = None
            is_accurate = False
        
        return RealityCheckResult(
            metric="Inflation Rate (CPI)",
            year=year,
            model_value=model_value,
            ai_verified_value=ai_value,
            ai_response=ai_response,
            is_accurate=is_accurate,
            deviation=deviation,
            confidence=confidence,
            notes=notes
        )
    
    def check_gdp_growth(self, year: int, model_value: float) -> RealityCheckResult:
        """
        Verify GDP growth rate for a specific year.
        
        Args:
            year: Year to check
            model_value: Model's predicted/stored GDP growth rate
            
        Returns:
            RealityCheckResult with verification
        """
        prompt = f"""You are a fact-checker for economic data.

Question: What was India's GDP growth rate in {year}?

Provide:
1. The actual GDP growth rate (%)
2. The source (World Bank, IMF, RBI, etc.)
3. Any important context (e.g., recession, boom, COVID)

Format your response as:
GDP_GROWTH: [number]%
SOURCE: [source name]
CONTEXT: [brief context]

Be precise and factual. If you're not certain, say so."""

        ai_response = self._query_ai(prompt)
        
        # Parse AI response
        ai_value, confidence, notes = self._parse_gdp_response(ai_response)
        
        # Calculate deviation
        if ai_value is not None:
            deviation = abs(model_value - ai_value)
            is_accurate = deviation <= 1.5  # Within 1.5 percentage points
        else:
            deviation = None
            is_accurate = False
        
        return RealityCheckResult(
            metric="GDP Growth Rate",
            year=year,
            model_value=model_value,
            ai_verified_value=ai_value,
            ai_response=ai_response,
            is_accurate=is_accurate,
            deviation=deviation,
            confidence=confidence,
            notes=notes
        )
    
    def check_unemployment_rate(self, year: int, model_value: float) -> RealityCheckResult:
        """
        Verify unemployment rate for a specific year.
        
        Args:
            year: Year to check
            model_value: Model's predicted/stored unemployment rate
            
        Returns:
            RealityCheckResult with verification
        """
        prompt = f"""You are a fact-checker for economic data.

Question: What was India's unemployment rate in {year}?

Provide:
1. The actual unemployment rate (%)
2. The source (PLFS, CMIE, World Bank, etc.)
3. Any important context (e.g., COVID spike, methodology changes)

Format your response as:
UNEMPLOYMENT_RATE: [number]%
SOURCE: [source name]
CONTEXT: [brief context]

Be precise and factual. If you're not certain, say so."""

        ai_response = self._query_ai(prompt)
        
        # Parse AI response
        ai_value, confidence, notes = self._parse_unemployment_response(ai_response)
        
        # Calculate deviation
        if ai_value is not None:
            deviation = abs(model_value - ai_value)
            is_accurate = deviation <= 1.0  # Within 1 percentage point
        else:
            deviation = None
            is_accurate = False
        
        return RealityCheckResult(
            metric="Unemployment Rate",
            year=year,
            model_value=model_value,
            ai_verified_value=ai_value,
            ai_response=ai_response,
            is_accurate=is_accurate,
            deviation=deviation,
            confidence=confidence,
            notes=notes
        )
    
    def check_economic_event(self, year: int, event_description: str) -> RealityCheckResult:
        """
        Verify if an economic event actually occurred.
        
        Args:
            year: Year of event
            event_description: Description of event
            
        Returns:
            RealityCheckResult with verification
        """
        prompt = f"""You are a fact-checker for economic events.

Question: Did this event occur in India in {year}?
Event: {event_description}

Provide:
1. YES or NO - did this event occur?
2. The actual details if it occurred
3. Source for verification

Format your response as:
OCCURRED: YES/NO
DETAILS: [actual details]
SOURCE: [source name]

Be precise and factual."""

        ai_response = self._query_ai(prompt)
        
        # Parse response
        occurred = "YES" in ai_response.upper()
        
        return RealityCheckResult(
            metric="Economic Event",
            year=year,
            model_value=1.0 if occurred else 0.0,
            ai_verified_value=1.0 if occurred else 0.0,
            ai_response=ai_response,
            is_accurate=occurred,
            deviation=0.0,
            confidence="MEDIUM",
            notes=event_description
        )
    
    def _query_ai(self, prompt: str) -> str:
        """
        Query AI (Groq or Gemini) for fact-checking.
        
        Args:
            prompt: Question to ask AI
            
        Returns:
            AI response text
        """
        # Try Groq first
        if self.groq_api_key:
            try:
                response = self._query_groq(prompt)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Groq API failed: {e}")
        
        # Try Gemini
        if self.gemini_api_key:
            try:
                response = self._query_gemini(prompt)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Gemini API failed: {e}")
        
        # No AI available
        return "AI_NOT_AVAILABLE: Cannot verify without AI API access"
    
    def _query_groq(self, prompt: str) -> Optional[str]:
        """Query Groq API with rate limiting and retry logic"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Low temperature for factual responses
            "max_tokens": 500
        }
        
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limits
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Rate limit hit, waiting {delay} seconds before retry {attempt + 1}")
                    time.sleep(delay)
                
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 429:
                    # Rate limit hit
                    logger.warning(f"Rate limit hit (429), attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return "RATE_LIMIT_EXCEEDED: Too many requests to Groq API"
                
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Groq API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    continue
                else:
                    raise
        
        return None
    
    def _query_gemini(self, prompt: str) -> Optional[str]:
        """Query Gemini API with rate limiting"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500
            }
        }
        
        max_retries = 3
        base_delay = 4  # Gemini has stricter rate limits
        
        for attempt in range(max_retries):
            try:
                # Add delay between requests
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Gemini rate limit, waiting {delay} seconds before retry {attempt + 1}")
                    time.sleep(delay)
                
                response = requests.post(url, json=data, timeout=30)
                
                if response.status_code == 429:
                    logger.warning(f"Gemini rate limit hit (429), attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return "RATE_LIMIT_EXCEEDED: Too many requests to Gemini API"
                
                response.raise_for_status()
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Gemini API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    continue
                else:
                    raise
        
        return None
    
    def _parse_inflation_response(self, response: str) -> Tuple[Optional[float], str, str]:
        """Parse AI response for inflation rate"""
        if "AI_NOT_AVAILABLE" in response or "RATE_LIMIT_EXCEEDED" in response:
            return None, "LOW", "AI not available for verification or rate limit exceeded"
        
        # Extract inflation rate
        ai_value = None
        for line in response.split('\n'):
            if "INFLATION_RATE:" in line.upper():
                try:
                    # Extract number from line
                    parts = line.split(':')[1].strip()
                    ai_value = float(parts.replace('%', '').strip())
                except:
                    pass
        
        # Extract context
        notes = ""
        for line in response.split('\n'):
            if "CONTEXT:" in line.upper():
                notes = line.split(':', 1)[1].strip()
                break
        
        # Determine confidence
        if "not certain" in response.lower() or "unclear" in response.lower() or "RATE_LIMIT_EXCEEDED" in response:
            confidence = "LOW"
        elif ai_value is not None:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"
        
        return ai_value, confidence, notes
    
    def _parse_gdp_response(self, response: str) -> Tuple[Optional[float], str, str]:
        """Parse AI response for GDP growth"""
        if "AI_NOT_AVAILABLE" in response or "RATE_LIMIT_EXCEEDED" in response:
            return None, "LOW", "AI not available for verification or rate limit exceeded"
        
        # Extract GDP growth
        ai_value = None
        for line in response.split('\n'):
            if "GDP_GROWTH:" in line.upper() or "GDP GROWTH:" in line.upper():
                try:
                    parts = line.split(':')[1].strip()
                    ai_value = float(parts.replace('%', '').strip())
                except:
                    pass
        
        # Extract context
        notes = ""
        for line in response.split('\n'):
            if "CONTEXT:" in line.upper():
                notes = line.split(':', 1)[1].strip()
                break
        
        # Determine confidence
        if "not certain" in response.lower() or "unclear" in response.lower() or "RATE_LIMIT_EXCEEDED" in response:
            confidence = "LOW"
        elif ai_value is not None:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"
        
        return ai_value, confidence, notes
    
    def _parse_unemployment_response(self, response: str) -> Tuple[Optional[float], str, str]:
        """Parse AI response for unemployment rate"""
        if "AI_NOT_AVAILABLE" in response or "RATE_LIMIT_EXCEEDED" in response:
            return None, "LOW", "AI not available for verification or rate limit exceeded"
        
        # Extract unemployment rate
        ai_value = None
        for line in response.split('\n'):
            if "UNEMPLOYMENT_RATE:" in line.upper() or "UNEMPLOYMENT RATE:" in line.upper():
                try:
                    parts = line.split(':')[1].strip()
                    ai_value = float(parts.replace('%', '').strip())
                except:
                    pass
        
        # Extract context
        notes = ""
        for line in response.split('\n'):
            if "CONTEXT:" in line.upper():
                notes = line.split(':', 1)[1].strip()
                break
        
        # Determine confidence
        if "not certain" in response.lower() or "unclear" in response.lower() or "RATE_LIMIT_EXCEEDED" in response:
            confidence = "LOW"
        elif ai_value is not None:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"
        
        return ai_value, confidence, notes


def format_reality_check_report(results: List[RealityCheckResult]) -> str:
    """
    Format reality check results into a readable report.
    
    Args:
        results: List of RealityCheckResult objects
        
    Returns:
        Formatted report string
    """
    report = "\n" + "="*80 + "\n"
    report += "REALITY CHECK VALIDATION REPORT\n"
    report += "="*80 + "\n\n"
    
    accurate_count = sum(1 for r in results if r.is_accurate)
    total_count = len(results)
    accuracy_pct = (accurate_count / total_count * 100) if total_count > 0 else 0
    
    report += f"Overall Accuracy: {accurate_count}/{total_count} ({accuracy_pct:.1f}%)\n"
    report += "\n" + "-"*80 + "\n\n"
    
    for i, result in enumerate(results, 1):
        status = "✅ ACCURATE" if result.is_accurate else "❌ INACCURATE"
        
        report += f"CHECK #{i}: {result.metric} ({result.year})\n"
        report += f"Status: {status}\n"
        report += f"Model Value: {result.model_value:.2f}%\n"
        
        if result.ai_verified_value is not None:
            report += f"AI Verified Value: {result.ai_verified_value:.2f}%\n"
            if result.deviation is not None:
                report += f"Deviation: {result.deviation:.2f} percentage points\n"
        else:
            report += f"AI Verified Value: Not available\n"
        
        report += f"Confidence: {result.confidence}\n"
        
        if result.notes:
            report += f"Notes: {result.notes}\n"
        
        report += f"\nAI Response:\n{result.ai_response[:200]}...\n"
        report += "\n" + "-"*80 + "\n\n"
    
    return report


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REALITY CHECKER TEST")
    print("="*80 + "\n")
    
    checker = RealityChecker()
    
    # Check if AI is available
    if not checker.groq_api_key and not checker.gemini_api_key:
        print("⚠️ WARNING: No AI API keys found")
        print("Set GROQ_API_KEY or GEMINI_API_KEY to enable reality checking")
        print("\nExample checks (without AI):")
    else:
        print("✅ AI API available for reality checking\n")
    
    # Test inflation rate
    print("TEST 1: Check India's inflation rate in 2020")
    result = checker.check_inflation_rate(2020, 6.2)
    print(f"Model Value: {result.model_value}%")
    print(f"AI Verified: {result.ai_verified_value}%")
    print(f"Accurate: {result.is_accurate}")
    print(f"Confidence: {result.confidence}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
