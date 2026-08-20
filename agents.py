from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from tools import web_search,scrap_url
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

out = StrOutputParser()

llm = ChatGroq(
    model = "qwen/qwen3.6-27b"
)
llm_max = ChatGroq(
    model = "openai/gpt-oss-120b"
)
def create_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt="""
You are a web research search agent.

You MUST use the web_search tool to research the user's question.

After using the tool, return the search results EXACTLY as provided by
the tool.

Do not summarize, rewrite, or omit the tool results.

The output MUST contain:
- Title
- URL
- Snippet

Never invent, modify, or remove URLs.
"""

    )
def create_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrap_url]
    )

#writer chain (LCEL PIPELINES)using runnables
writer_prompt = ChatPromptTemplate.from_messages([{
    "role":"system",
    "content":"You are an expert research writer. Write clear, structured and insightful reports."
},
{
    "role":"user",
    "content":"""
    Task: Write a detailed research report on the topic: {topic}

Context / Research Provided:
{research}

Formatting & Structural Requirements:

    Introduction: Provide a clear, thorough overview of the topic, defining key concepts and setting the context based on the research.

    Key Findings: Detail a minimum of 3 well-explained core findings. Use sub-bullet points or short analytical paragraphs for each finding to elaborate on specific data, implications, or examples provided in the source text.

    Conclusion: Synthesize the primary insights and highlight the broader significance of the research without introducing unmentioned facts.

    Sources: Create an itemized list of all explicit URLs provided within the research context.

Execution Constraints:

    Strict Factuality: Rely only on the clear facts directly mentioned in the research context. Do not extrapolate, assume, or fabricate outside details.

    Tone: Maintain an authoritative, objective, and professional tone throughout.

    Completeness: Ensure every main argument in the provided context is accurately represented with thorough explanation rather than high-level summaries.
    """
}])

critic_prompt = ChatPromptTemplate.from_messages([{
    "role":"system",
    "content":"You are a sharp and constructive research critic. Be honest and specific."
},
{
    "role":"user",
    "content":"""
    Topic-
    {topic}
    Input Report:
    {report}

Evaluation Criteria:
Evaluate the report across four core dimensions:

    Structural Compliance: Does it adhere strictly to all requested sections (Introduction, Key Findings, Conclusion, Sources)?

    Depth & Analysis: Are the Key Findings well-explained (minimum 3 detailed points) with thorough context rather than brief summaries?

    Factuality & Objectivity: Is the tone professional, objective, and strictly grounded without fluff, embellishments, or unverified claims?

    Source Integrity: Are source URLs explicitly listed and properly formatted?

Output Instructions:
You MUST respond using this exact format with no extra introductory or concluding text:

Score: [X]/10

Strengths:

    [Specific strength with concrete reference to the text]

    [Specific strength with concrete reference to the text]

Areas to Improve:

    [Actionable area of improvement with exact recommendation]

    [Actionable area of improvement with exact recommendation]

One line verdict:
[A single, definitive sentence summarizing the report's quality and readiness]
    """
}])
writer_chain = writer_prompt | llm_max | out
critic_chain = critic_prompt | llm_max | out