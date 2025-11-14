"""
Deep Legal Analysis Service using GPT-5.1

Generates comprehensive 2-3 page legal analysis with 10 sections:
1. Case Context & Background
2. Expert Witness Profile
3. Challenged Methodology
4. Daubert Standards Applied
5. Court's Reasoning
6. Exclusion/Admission Grounds
7. Precedent Analysis
8. Implications for Expert Testimony
9. Judicial Patterns
10. Key Takeaways
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path, override=True)

logger = logging.getLogger(__name__)


class DeepAnalysisService:
    """Service for generating deep legal analysis using GPT-5.1."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the deep analysis service.

        Args:
            api_key: OpenAI API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-5-nano"  # GPT-5 nano - fastest and cheapest
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def _build_analysis_prompt(self, order_text: str, metadata: Dict[str, Any]) -> str:
        """
        Build the comprehensive analysis prompt.

        Args:
            order_text: Full text of the legal order
            metadata: Extracted metadata

        Returns:
            Formatted prompt string
        """
        case_name = metadata.get('case_name', 'Unknown Case')
        experts = metadata.get('expert_names', [])
        citations = metadata.get('citations', [])
        daubert_count = metadata.get('daubert_mentions', 0)

        prompt = f"""You are an expert legal analyst specializing in expert witness testimony and Daubert/FRE 702 rulings. Analyze the following legal order from Judge Boyle and provide a comprehensive 2-3 page analysis.

**CASE INFORMATION:**
- Case Name: {case_name}
- Docket: {metadata.get('docket_number', 'Unknown')}
- Date: {metadata.get('date', 'Unknown')}
- Judge: {metadata.get('judge_name', 'Judge Boyle')}
- Experts Mentioned: {', '.join(experts) if experts else 'Not specified'}
- Citations Found: {len(citations)}
- Daubert Mentions: {daubert_count}

**LEGAL ORDER TEXT:**
{order_text}

**REQUIRED ANALYSIS:**

Provide a detailed analysis organized into exactly 10 sections. Each section should be thorough and substantive:

1. **Case Context & Background**
   - Summarize the underlying dispute
   - Identify the parties and their positions
   - Describe the procedural posture

2. **Expert Witness Profile**
   - Identify the expert(s) at issue
   - Describe their qualifications and proposed testimony
   - Note the area of expertise

3. **Challenged Methodology**
   - Detail what methodology or opinion was challenged
   - Explain the basis for the challenge
   - Identify specific concerns raised

4. **Daubert Standards Applied**
   - Identify which Daubert/FRE 702 factors were considered
   - Explain how the court applied these standards
   - Note any specific tests or criteria used

5. **Court's Reasoning**
   - Summarize the court's analytical framework
   - Explain the key reasoning behind the decision
   - Identify pivotal facts or arguments

6. **Exclusion/Admission Grounds**
   - State whether testimony was excluded or admitted
   - Detail the specific grounds for the ruling
   - Note any conditions or limitations

7. **Precedent Analysis**
   - Identify key cases cited by the court
   - Explain how precedent influenced the decision
   - Note any distinguishing factors

8. **Implications for Expert Testimony**
   - Discuss what this ruling means for similar cases
   - Identify standards experts must meet
   - Note any guidance for future cases

9. **Judicial Patterns**
   - Identify any patterns in Judge Boyle's approach
   - Note emphasis on particular Daubert factors
   - Discuss the level of scrutiny applied

10. **Key Takeaways**
    - Summarize 3-5 critical lessons from this order
    - Highlight practical implications for litigators
    - Note any unique aspects of the ruling

**FORMAT:**
Return your analysis as a JSON object with this structure:
{{
  "case_context": "...",
  "expert_profile": "...",
  "challenged_methodology": "...",
  "daubert_standards": "...",
  "court_reasoning": "...",
  "exclusion_admission": "...",
  "precedent_analysis": "...",
  "implications": "...",
  "judicial_patterns": "...",
  "key_takeaways": "..."
}}

Each field should contain 2-4 detailed paragraphs (150-300 words). Be specific, cite details from the order, and provide actionable insights.
"""
        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def generate_analysis(
        self,
        order_text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate deep legal analysis using GPT-5.1.

        Args:
            order_text: Full text of the legal order
            metadata: Extracted metadata

        Returns:
            Dictionary containing analysis sections and token usage

        Raises:
            Exception: If API call fails after retries
        """
        prompt = self._build_analysis_prompt(order_text, metadata)

        try:
            logger.info(f"Generating analysis for: {metadata.get('case_name', 'Unknown')}")

            # GPT-5.1 supports system messages, reasoning_effort, and structured outputs
            # Note: GPT-5.1 only supports default temperature (1)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert legal analyst specializing in expert witness testimony, Daubert motions, and FRE 702. Provide thorough, well-structured analysis with specific citations and actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                reasoning_effort="high",  # high reasoning effort for deep analysis
                max_completion_tokens=16000,
                response_format={"type": "json_object"}
            )

            # Extract response
            content = response.choices[0].message.content
            analysis = json.loads(content)

            # Track token usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

            # Calculate cost (GPT-5 mini pricing: $0.25/1M input, $1/1M output)
            cost = (input_tokens / 1_000_000 * 0.25) + (output_tokens / 1_000_000 * 1.00)
            self.total_cost += cost

            logger.info(
                f"✓ Analysis complete: {total_tokens} tokens "
                f"(in: {input_tokens}, out: {output_tokens}), "
                f"cost: ${cost:.4f}"
            )

            return {
                'analysis': analysis,
                'token_usage': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': total_tokens,
                    'cost_usd': round(cost, 4)
                },
                'model': self.model
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content[:500]}")
            raise

        except Exception as e:
            logger.error(f"Error generating analysis: {e}", exc_info=True)
            raise

    def get_total_cost(self) -> Dict[str, Any]:
        """
        Get total token usage and cost statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'total_cost_usd': round(self.total_cost, 2)
        }


# Convenience function
async def analyze_order(order_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze a legal order.

    Args:
        order_text: Full text of the order
        metadata: Extracted metadata

    Returns:
        Analysis dictionary
    """
    service = DeepAnalysisService()
    return await service.generate_analysis(order_text, metadata)
