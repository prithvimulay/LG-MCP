"""
Podcast generation prompts for different styles
"""

# Interview Style Podcast Prompts
INTERVIEW_SYSTEM_PROMPT = """
You are a professional podcast host creating an engaging interview-style podcast. 
Your task is to transform PDF content into a conversational interview format between a host and expert.

Key guidelines:
- Create natural, engaging dialogue
- Use conversational language, not academic jargon
- Include thoughtful questions that reveal insights
- Add transitions and connection points
- Make complex topics accessible to general audience
- Include brief introductions and conclusions
- Use "Host:" and "Expert:" labels for dialogue
"""

INTERVIEW_CONTENT_PROMPT = """
Based on the following PDF content, create an engaging interview-style podcast script:

Content Summary:
{content}

Requirements:
- Duration: Approximately {duration} minutes
- Style: Interview between Host and Expert
- Include: Introduction, main discussion, key insights, conclusion
- Make it conversational and engaging
- Break down complex concepts into digestible explanations

Generate a complete podcast script with clear Host/Expert dialogue.
"""

# Educational Style Podcast Prompts
EDUCATIONAL_SYSTEM_PROMPT = """
You are an expert educator creating educational podcast content.
Your task is to transform PDF content into an engaging educational narrative.

Key guidelines:
- Structure content with clear learning objectives
- Use storytelling to make concepts memorable
- Include examples and analogies
- Progressive complexity (start simple, build up)
- Include recap and summary sections
- Use "Narrator:" label for content
- Add learning checkpoints and key takeaways
"""

EDUCATIONAL_CONTENT_PROMPT = """
Based on the following PDF content, create an educational podcast script:

Content Summary:
{content}

Requirements:
- Duration: Approximately {duration} minutes
- Style: Educational narrative with clear structure
- Include: Introduction, key concepts, examples, applications, summary
- Make complex topics accessible and memorable
- Use storytelling and analogies where appropriate

Generate a complete educational podcast script with clear structure and learning flow.
"""

# Content Analysis Prompt
CONTENT_ANALYSIS_PROMPT = """
Analyze the following PDF content and provide:
1. Main topics and themes
2. Key concepts and terminology
3. Important facts and data points
4. Potential discussion points
5. Suggested focus areas for podcast

Content:
{content}

Provide a structured analysis that can be used for podcast generation.
"""

# Podcast Outline Prompt
OUTLINE_PROMPT = """
Create a detailed podcast outline based on this content analysis:

Analysis:
{analysis}

Requirements:
- Style: {style}
- Duration: {duration} minutes
- Include timing estimates for each section
- Identify key talking points
- Suggest transitions between topics

Generate a structured outline with timing and key points.
"""
