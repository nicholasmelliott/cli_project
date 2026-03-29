from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base
from core.docs_data import docs

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs

SUPPORTED_LANGUAGES = [
    "French", "Spanish", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian"
]

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs [doc_id]

@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]

@mcp.resource(
    "docs://languages",
    mime_type="application/json"
)
def list_languages() -> list[str]:
    return SUPPORTED_LANGUAGES

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.
    
    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>
    
    Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
    Use the 'edit_document' tool to edit the document. After the document has been reformatted...
    """

    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of the document."
)
def summarize_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
        Your goal is to summarize a document.

        The id of the document you need to summarize is:
        <document_id>
        {doc_id}
        </document_id>
    """
    return [ base.UserMessage(prompt) ]


@mcp.prompt(
    name="translate",
    description="Translates the contents of the document into the specified language."
)
def translate_document(
    doc_id: str = Field(description="Id of the document to translate"),
    target_language: str = Field(description="The language to translate the document into (e.g., 'French', 'Spanish', 'German')")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to translate a document into the specified language.

    The id of the document you need to translate is:
    <document_id>
    {doc_id}
    </document_id>

    The target language is:
    <target_language>
    {target_language}
    </target_language>

    Use the 'edit_document' tool to update the document with the translated content. Only translate the content, do not add commentary.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="extract_action_items",
    description="Extracts actionable tasks, deadlines, and responsible parties from the document, returning a structured list for project management or follow-up."
)
def extract_action_items(
    doc_id: str = Field(description="Id of the document to analyze for action items")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to extract all actionable tasks, deadlines, and responsible parties from the following document.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each action item, return:
    - Task description
    - Responsible party (if mentioned)
    - Deadline or due date (if mentioned)

    Return the results as a structured JSON list, e.g.:
    [
      { '{' }"task": "Review budget", "responsible": "Alex", "deadline": "2026-03-10"{ '}' },
      ...
    ]

    If no action items are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="detect_risks",
    description="Analyzes the document to identify and summarize potential risks, issues, or concerns, including their severity and suggested mitigations."
)
def detect_risks(
    doc_id: str = Field(description="Id of the document to analyze for risks")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to analyze the following document and identify any potential risks, issues, or concerns.
    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>
    For each risk, return:
    - Risk description
    - Severity (Low, Medium, High)
    - Suggested mitigation (if possible)
    - Estimated time duration for mitigation (e.g., "2 weeks", "3 days", "1 month", "5 minutes")

    Return the results as a structured JSON list, e.g.:
    [
      { '{' }"risk": "Project delay due to resource shortage", "severity": "High", "mitigation": "Hire additional staff", "estimated_duration": "2 weeks"{ '}' },
      ...
    ]
    If no risks are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="generate_questions",
    description="Generates comprehension or review questions based on the document’s content. Useful for training, study guides, or knowledge checks."
)
def generate_questions(
    doc_id: str = Field(description="Id of the document to generate questions from")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to generate comprehension or review questions based on the following document.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    Create 5-10 questions that test understanding of the document’s key points, facts, or concepts. Use a mix of question types (multiple choice, short answer, true/false, etc.) if possible. Return the questions as a structured JSON list, e.g.:
    [
      { '{' }"type": "multiple_choice", "question": "What is the deadline for project completion?", "choices": ["May 15, 2026", "June 1, 2026"], "answer": "May 15, 2026"{ '}' },
      ...
    ]

    If no questions can be generated, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="find_inconsistencies",
    description="Scans the document for conflicting statements, data discrepancies, or logical inconsistencies. Useful for quality assurance, technical reviews, or compliance."
)
def find_inconsistencies(
    doc_id: str = Field(description="Id of the document to scan for inconsistencies")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to scan the following document for conflicting statements, data discrepancies, or logical inconsistencies.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each inconsistency found, return:
    - Description of the inconsistency
    - Location or section (if possible)
    - Suggested correction or clarification (if possible)

    Return the results as a structured JSON list, e.g.:
    [
      { '{' }"description": "Budget total does not match itemized costs", "location": "Section 2.1", "suggested_correction": "Update itemized costs to match total"{ '}' },
      ...
    ]

    If no inconsistencies are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="detect_dependencies",
    description="Extracts and lists all dependencies, prerequisites, or required resources mentioned in the document. Useful for project planning, technical specs, or onboarding."
)
def detect_dependencies(
    doc_id: str = Field(description="Id of the document to analyze for dependencies")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to extract and list all dependencies, prerequisites, or required resources mentioned in the following document.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each dependency, return:
    - Dependency or resource name
    - Type (e.g., software, hardware, personnel, external document, etc.)
    - Description or notes (if available)

    Return the results as a structured JSON list, e.g.:
    [
      { '{' }"name": "Python 3.10", "type": "software", "description": "Required for running scripts"{ '}' },
      ...
    ]

    If no dependencies are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="detect_sentiment_zones",
    description="Maps out sections of the document by sentiment (positive, negative, neutral), highlighting emotional tone shifts. Useful for reviews, reports, or communications."
)
def detect_sentiment_zones(
    doc_id: str = Field(description="Id of the document to analyze for sentiment zones")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to analyze the following document and map out sections by sentiment: positive, negative, or neutral.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each section or paragraph, return:
    - Section identifier or excerpt
    - Sentiment (positive, negative, neutral)
    - Brief explanation of why

    Highlight any emotional tone shifts or transitions between sentiments throughout the document.

    Return the results as a structured JSON list, e.g.:
    [
      { '{' }"section": "Introduction", "sentiment": "neutral", "explanation": "Objective overview"{ '}' },
      { '{' }"section": "Budget Concerns", "sentiment": "negative", "explanation": "Expresses worry about overspending"{ '}' },
      ...
    ]

    If no sentiment zones are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="generate_index",
    description="Creates an index for the document, listing key topics, terms, or sections and their locations or page numbers. Useful for navigation and reference."
)
def generate_index(
    doc_id: str = Field(description="Id of the document to generate an index for")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to create an index for the following document, similar to the back-of-book index.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each index entry, return:
    - Topic, term, or section name
    - Location or page/section number (if available)
    - Brief context or description (optional)
    - Related topics or cross-references (if available)
    - Supporting excerpt (1-2 lines from the source text)

    Return the results as a structured JSON list, e.g.:
    [
            {{ "topic": "Budget", "location": "Section 2.1", "context": "Project financials", "related_topics": ["Forecast", "Expenses"], "excerpt": "The project budget allocates 45% to staffing and 20% to infrastructure." }},
      ...
    ]

    If no index entries are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="generate_glossary",
    description="Scans the document for technical terms, acronyms, and domain-specific language, then produces a structured glossary with definitions. Useful for onboarding, documentation, and knowledge sharing."
)
def generate_glossary(
    doc_id: str = Field(description="Id of the document to generate a glossary for")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to scan the following document and produce a glossary of key terms, acronyms, and domain-specific language.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    For each glossary entry, return:
    - Term or acronym
    - Definition or expansion (as used in the document)
    - Category (e.g., technical, business, legal, medical, acronym, etc.)
    - Example sentence or context from the document (if available)

    Return the results as a structured JSON list sorted alphabetically by term, e.g.:
    [
      {{"term": "API", "definition": "Application Programming Interface — a set of rules for how software components communicate", "category": "acronym", "example": "The API is used to connect the frontend to the backend services."}},
      ...
    ]

    If no glossary-worthy terms are found, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

@mcp.prompt(
        name="generate_cheat_sheet",
        description="Creates a practical cheat sheet from the document, including key concepts, commands, formulas, and quick-reference guidance. Useful for study, onboarding, and day-to-day execution."
)
def generate_cheat_sheet(
        doc_id: str = Field(description="Id of the document to generate a cheat sheet for")
) -> list[base.Message]:
        prompt = f"""
        Your goal is to create a concise, high-value cheat sheet from the following document.

        The id of the document is:
        <document_id>
        {doc_id}
        </document_id>

        Build the cheat sheet for quick reference. Prioritize practical utility over exhaustive detail.

        Include the following sections when the information exists:
        - Core concepts (short definitions)
        - Key steps or workflow (ordered)
        - Commands, functions, or syntax snippets
        - Rules, formulas, or thresholds
        - Common mistakes and how to avoid them
        - Quick checklist for execution/review

        Return results as a structured JSON object, e.g.:
        {{
            "title": "Document Cheat Sheet",
            "core_concepts": [
                {{"term": "Rate Limit", "summary": "Maximum requests per time window"}}
            ],
            "workflow": ["Step 1", "Step 2"],
            "commands_or_snippets": [
                {{"label": "Start server", "snippet": "python main.py", "notes": "Run from project root"}}
            ],
            "rules_or_formulas": [
                {{"name": "Retry backoff", "value": "delay = base * 2^attempt", "notes": "Cap at 30s"}}
            ],
            "common_mistakes": [
                {{"mistake": "Missing environment variable", "avoidance": "Validate .env before running"}}
            ],
            "quick_checklist": ["Confirm prerequisites", "Run smoke test"]
        }}

        Keep entries brief and actionable. If a section has no relevant data, return an empty list for that section.
        """
        return [ base.UserMessage(prompt) ]

@mcp.prompt(
    name="solve_common_problems",
    description="Scans the document for common problems and returns practical, document-grounded solutions."
)
def solve_common_problems(
    doc_id: str = Field(description="Id of the document to scan for common problems and solutions")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to scan the following document, identify common problems discussed or implied in it, and provide solutions grounded in the document context.

    The id of the document is:
    <document_id>
    {doc_id}
    </document_id>

    Instructions:
    - Focus only on problems that are supported by the document content.
    - For each problem, propose a practical solution that aligns with the document's terminology and constraints.
    - Do not invent external facts. If evidence is weak, mark confidence as "low".

    Return the results as a structured JSON list, e.g.:
    [
      {{"problem": "Configuration errors when starting the service", "solution": "Validate required environment variables before launch", "evidence": "Section 'Setup' requires API key in .env", "confidence": "high"}},
      ...
    ]

    If no common problems can be identified, return an empty list.
    """
    return [ base.UserMessage(prompt) ]

if __name__ == "__main__":
    mcp.run(transport="stdio")
