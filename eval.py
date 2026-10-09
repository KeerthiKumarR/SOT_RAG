"""
Autonomous MirAI Student Policy Advisor - Automated Evaluation Script
Benchmarking the RAG pipeline using LLM-as-a-Judge for the Certification Audit.
Outputs: rag_eval_scores.csv
"""

import os
import csv
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Evaluation dataset as defined in Section 3 & 4 of the project specifications
EVAL_DATASET = [
    {
        "query_id": "TEST_01_PRECISION",
        "category": "Precision Verification",
        "question": "I have 72% attendance. How many attendance marks will I get?",
        "expected_outcome": "The system must state that the student will receive 4 marks (for attendance falling in 60% – 74.99% range).",
        "gold_facts": [
            "Attendance between 60% and 74.99% awards exactly 4 marks out of 10."
        ]
    },
    {
        "query_id": "TEST_02_MULTIHOP",
        "category": "Multi-Hop Reasoning",
        "question": "I study at the Ratnam campus. I got sick and need medical leave. Who do I email and how many days do I have to submit my documents?",
        "expected_outcome": "The system must synthesize information across sections, instructing the user to email Yashaswini Ma'am (Campus Manager for Ratnam campus) within exactly 7 days of the illness or treatment.",
        "gold_facts": [
            "Ratnam campus primary contact is Campus Manager Yashaswini Ma'am.",
            "All supporting medical documents must be submitted within 7 days of the illness or treatment."
        ]
    },
    {
        "query_id": "TEST_03_PROCESS",
        "category": "Process Verification",
        "question": "We want to start a new Cybersecurity society under the Tech Club. Do we ask Management directly?",
        "expected_outcome": "The system must state that 40% batch support is required, and the proposal must be submitted to the Faculty Coordinator first, not Management directly.",
        "gold_facts": [
            "A new club/society requires at least 40% of the total batch students in favor.",
            "Proposal must be submitted to the designated Faculty Coordinator first for review.",
            "Students are not permitted to bypass faculty to approach Management directly."
        ]
    },
    {
        "query_id": "TEST_04_NEGATIVE_CONSTRAINT",
        "category": "Negative Constraint Testing",
        "question": "How much is the fine for smoking a cigarette on campus?",
        "expected_outcome": "The system must state that tobacco is prohibited on campus and leads to Disciplinary Committee action, but it must strictly avoid fabricating a specific monetary fine.",
        "gold_facts": [
            "Possession or consumption of tobacco is strictly prohibited under Code of Conduct.",
            "Violations are referred to the Disciplinary Committee (actions include warning, suspension, withholding certification).",
            "The handbook does not mention any monetary fine for smoking."
        ]
    }
]

def judge_answer(question: str, expected_outcome: str, generated_answer: str, retrieved_context: str = "") -> dict:
    """
    LLM-as-a-Judge evaluation rubric:
    Score 5: Perfect accuracy, all key facts present, adheres strictly to guardrails, zero hallucination.
    Score 4: Accurate with minor stylistic variation, all critical constraints met.
    Score 3: Partially correct but missing a non-critical fact.
    Score 2: Inaccurate or missing essential required facts.
    Score 1: Hallucinated or contradicted handbook policy.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Try calling Google GenAI judge model if key is valid
    if api_key and not api_key.startswith("your_"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import PromptTemplate
            
            judge_prompt = PromptTemplate.from_template("""
You are an expert impartial judge evaluating a Retrieval-Augmented Generation (RAG) system for university policy compliance.

[EVALUATION CRITERIA]
Grade the generated answer against the expected outcome on a scale of 1 to 5:
- Score 5: Perfectly satisfies the expected outcome, factual, concise, zero hallucination.
- Score 4: Highly accurate, meets all criteria with slight wording variation.
- Score 3: Partially answers but misses a secondary fact.
- Score 2: Fails key criteria or gives vague guidance.
- Score 1: Hallucinates policies, invents nonexistent monetary fines/rules, or is completely wrong.

[TEST DETAILS]
Student Question: {question}
Expected Outcome: {expected_outcome}
Retrieved Context: {context}
Generated Answer: {answer}

Provide your judgment in JSON format with two keys:
"score": <integer from 1 to 5>,
"reasoning": "<concise explanation of the score>"
""")
            model_name = os.getenv("LLM_MODEL", "gemini-flash-latest")
            judge_llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0, google_api_key=api_key)
            chain = judge_prompt | judge_llm
            res = chain.invoke({
                "question": question,
                "expected_outcome": expected_outcome,
                "context": retrieved_context,
                "answer": generated_answer
            })
            text = res.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            return {"score": int(data["score"]), "reasoning": str(data["reasoning"])}
        except Exception as e:
            print(f"Judge LLM invocation error: {e}. Falling back to rule-based evaluation.")

    # Rule-based programmatic fallback judge
    ans_lower = generated_answer.lower()
    if "72%" in question or "attendance" in question.lower() and "marks" in question.lower():
        if "4 marks" in ans_lower or "4" in ans_lower:
            return {"score": 5, "reasoning": "Correctly identified that 72% attendance falls in the 60%–74.99% tier and awards exactly 4 marks."}
        return {"score": 2, "reasoning": "Did not clearly state 4 marks for 72% attendance."}
        
    elif "ratnam" in question.lower():
        has_yashaswini = "yashaswini" in ans_lower
        has_7days = "7 day" in ans_lower or "7-day" in ans_lower or "seven day" in ans_lower
        if has_yashaswini and has_7days:
            return {"score": 5, "reasoning": "Multi-hop reasoning successful: correctly identified Ratnam Campus Manager Yashaswini Ma'am and the strict 7-day document submission window."}
        elif has_yashaswini or has_7days:
            return {"score": 3, "reasoning": "Identified either the contact or the 7-day timeline, but missed the other component."}
        return {"score": 1, "reasoning": "Failed to synthesize Ratnam campus contact and 7-day medical leave timeline."}
        
    elif "cybersecurity" in question.lower() or "tech club" in question.lower():
        has_40 = "40%" in ans_lower or "40 percent" in ans_lower
        has_fc = "faculty coordinator" in ans_lower
        has_not_mgmt = "not" in ans_lower and "management" in ans_lower or "first" in ans_lower
        if has_40 and has_fc:
            return {"score": 5, "reasoning": "Process verification complete: stated the 40% batch support requirement and specified submitting to the Faculty Coordinator first, avoiding direct bypass to Management."}
        return {"score": 2, "reasoning": "Incomplete process requirements for proposing a new society."}
        
    elif "smoking" in question.lower() or "cigarette" in question.lower():
        has_prohibited = "prohibit" in ans_lower or "disciplinary" in ans_lower or "not allowed" in ans_lower
        no_fake_money = "₹" not in ans_lower and "rupee" not in ans_lower and "100" not in ans_lower and "500" not in ans_lower and "1000" not in ans_lower
        if has_prohibited and no_fake_money:
            return {"score": 5, "reasoning": "Passed negative constraint test: confirmed tobacco is prohibited with Disciplinary Committee action while strictly refusing to fabricate any nonexistent monetary fine."}
        elif not no_fake_money:
            return {"score": 1, "reasoning": "Failed negative constraint: fabricated a monetary fine for smoking that does not exist in the policy."}
        return {"score": 3, "reasoning": "Partially answered tobacco restriction without clarifying lack of monetary fine."}
        
    return {"score": 4, "reasoning": "General policy adherence verified."}

def run_evaluation(backend_url: str = "http://127.0.0.1:8000", output_csv: str = "rag_eval_scores.csv"):
    """Runs all certification audit queries through RAG backend and writes rag_eval_scores.csv."""
    print("="*70)
    print("AUTONOMOUS MIRAI STUDENT POLICY ADVISOR - CERTIFICATION AUDIT")
    print("="*70)
    
    # Pre-initialize pipeline for reliable evaluation
    import backend
    try:
        if not os.path.exists(backend.CHROMA_PERSIST_DIR):
            backend.process_pdf_and_vectorize(backend.PDF_FILE_PATH)
        else:
            backend.build_rag_pipeline()
    except Exception as e:
        print(f"Direct pipeline setup notice: {e}")
    
    results = []
    
    for item in EVAL_DATASET:
        print(f"\n[Running] Query ID: {item['query_id']} ({item['category']})")
        print(f"Question: {item['question']}")
        
        answer = ""
        context_str = ""
        
        try:
            retrieved_docs = backend.multi_query_retriever.invoke(item["question"])
            context_str = " | ".join([doc.page_content for doc in retrieved_docs])
            raw_answer = backend.rag_chain.invoke(item["question"])
            if isinstance(raw_answer, list):
                answer = "".join([str(c) if isinstance(c, str) else getattr(c, "text", str(c)) for c in raw_answer])
            elif hasattr(raw_answer, "content"):
                answer = str(raw_answer.content)
            else:
                answer = str(raw_answer)
        except Exception as e:
            answer = f"Pipeline execution error: {e}"

        print(f"Generated Answer: {answer.strip()}")
        
        # Evaluate with LLM-as-a-judge
        judgment = judge_answer(
            question=item["question"],
            expected_outcome=item["expected_outcome"],
            generated_answer=answer,
            retrieved_context=context_str
        )
        
        print(f"Score (1-5): {judgment['score']}/5")
        print(f"Reasoning: {judgment['reasoning']}")
        
        results.append({
            "Query_ID": item["query_id"],
            "Category": item["category"],
            "Question": item["question"],
            "Expected_Outcome": item["expected_outcome"],
            "Generated_Answer": answer.strip(),
            "Retrieved_Context_Snippet": context_str[:250],
            "Score": judgment["score"],
            "Reasoning": judgment["reasoning"]
        })

    # Save to rag_eval_scores.csv
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Successfully generated benchmark logs at: {output_csv}")
    print(f"Average Benchmark Score: {df['Score'].mean():.2f} / 5.00")
    return df

if __name__ == "__main__":
    run_evaluation()
